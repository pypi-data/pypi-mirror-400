"""
Image ETL Pipeline - Orchestrates the download, convert, and update workflow.
"""
import os
import json
from typing import Optional, List, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .etl_types import ETLResult
from .extractor import ImageURLExtractor
from .optimizer import ImageOptimizer


class ImageETL:
    """
    ETL pipeline for image optimization.
    
    Extract: Find image URLs in markdown files
    Transform: Download and convert to WebP
    Load: Update markdown files with new URLs
    """

    def __init__(
        self,
        content_dir: str,
        webp_dir: str,
        webp_base_url: Optional[str] = None,
        quality: int = 80,
        max_width: int = 1200,
        exclude_extensions: Optional[List[str]] = None,
        threads: int = 4
    ):
        """
        Initialize the ETL pipeline.
        
        Args:
            content_dir: Directory containing markdown files
            webp_dir: Directory to save converted WebP images
            webp_base_url: Base URL for WebP images (if None, uses relative path)
            quality: WebP quality (1-100)
            max_width: Maximum image width
            exclude_extensions: List of file extensions to skip (e.g., ['gif'])
            threads: Number of parallel download threads (default: 4)
        """
        self.content_dir = content_dir
        self.webp_dir = webp_dir
        self.webp_base_url = webp_base_url
        self.exclude_extensions = [ext.lower().lstrip('.') for ext in (exclude_extensions or [])]
        self.threads = threads
        self.extractor = ImageURLExtractor()
        self.optimizer = ImageOptimizer(quality=quality, max_width=max_width)
        self.mapping_file = os.path.join(webp_dir, 'mapping.json')

    def _get_filename_from_url(self, url: str) -> str:
        """Extract a clean filename from URL, preserving original name."""
        parsed = urlparse(url)
        path = parsed.path
        # Get the filename from URL path
        filename = os.path.basename(path)
        # Remove query params if any
        if '?' in filename:
            filename = filename.split('?')[0]
        return filename

    def _get_webp_filename(self, original_filename: str) -> str:
        """Convert original filename to WebP filename."""
        name, _ = os.path.splitext(original_filename)
        return f"{name}.webp"

    def _load_existing_mappings(self) -> dict:
        """Load existing mappings from JSON file."""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_mappings(self, mappings: dict):
        """Save mappings to JSON file."""
        os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)
        with open(self.mapping_file, 'w') as f:
            json.dump(mappings, f, indent=2)

    def run(self, dry_run: bool = False) -> ETLResult:
        """
        Run the ETL pipeline.
        
        Args:
            dry_run: If True, only show what would be done without making changes
            
        Returns:
            ETLResult with statistics and mappings
        """
        result = ETLResult()
        
        # Create directories
        if not dry_run:
            os.makedirs(self.webp_dir, exist_ok=True)

        # Load existing mappings to skip already processed
        existing_mappings = self._load_existing_mappings()
        
        # Step 1: Extract URLs from markdown files
        print("=" * 60)
        print("STEP 1: Extracting image URLs from markdown files...")
        print("=" * 60)
        
        url_occurrences = self.extractor.extract_from_directory(self.content_dir)
        
        # Deduplicate URLs while tracking which files use them
        url_to_files: dict = {}  # url -> list of (file_path, line_num)
        for file_path, line_num, url in url_occurrences:
            if url not in url_to_files:
                url_to_files[url] = []
            url_to_files[url].append((file_path, line_num))
        
        unique_urls = list(url_to_files.keys())
        result.total_urls_found = len(unique_urls)
        
        print(f"Found {len(url_occurrences)} image references in markdown files")
        print(f"Unique URLs: {len(unique_urls)}")
        
        if dry_run:
            print("\n[DRY RUN] Would process these URLs:")
            for url in unique_urls[:10]:
                print(f"  - {url}")
            if len(unique_urls) > 10:
                print(f"  ... and {len(unique_urls) - 10} more")
            return result

        # Step 2 & 3: Download and convert each unique URL
        print("\n" + "=" * 60)
        print(f"STEP 2 & 3: Downloading and converting images ({self.threads} threads)...")
        print("=" * 60)
        
        new_mappings = {}
        urls_to_process = []
        
        # Filter URLs first
        for url in unique_urls:
            original_filename = self._get_filename_from_url(url)
            _, ext = os.path.splitext(original_filename)
            
            if ext.lower().lstrip('.') in self.exclude_extensions:
                print(f"⏭ Skipping (excluded extension {ext}): {url[:50]}...")
                result.skipped += 1
                continue
                
            if url in existing_mappings:
                print(f"⏭ Skipping (already processed): {url[:60]}...")
                result.skipped += 1
                new_mappings[url] = existing_mappings[url]
                continue
            
            urls_to_process.append(url)
        
        print(f"\n📥 Processing {len(urls_to_process)} images...")
        
        def process_url(url: str) -> Tuple[str, Optional[str], Optional[str]]:
            """Process a single URL. Returns (url, webp_filename, error)."""
            try:
                original_filename = self._get_filename_from_url(url)
                webp_filename = self._get_webp_filename(original_filename)
                webp_path = os.path.join(self.webp_dir, webp_filename)
                
                success = self.optimizer.download_and_optimize(
                    url=url,
                    save_path=webp_path,
                    format='WEBP'
                )
                
                if success:
                    return (url, webp_filename, None)
                else:
                    return (url, None, f"Failed to process: {url}")
                    
            except Exception as e:
                return (url, None, f"Error processing {url}: {e}")
        
        # Process URLs in parallel
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(process_url, url): url for url in urls_to_process}
            
            for future in as_completed(futures):
                url, webp_filename, error = future.result()
                
                if error:
                    print(f"   ❌ {error}")
                    result.errors.append(error)
                else:
                    result.downloaded += 1
                    result.converted += 1
                    new_mappings[url] = webp_filename
                    print(f"   ✅ {webp_filename}")

        # Save updated mappings
        all_mappings = {**existing_mappings, **new_mappings}
        self._save_mappings(all_mappings)
        result.mappings = all_mappings
        
        # Step 4: Update markdown files
        print("\n" + "=" * 60)
        print("STEP 4: Updating markdown files...")
        print("=" * 60)
        
        files_to_update: dict = {}  # file_path -> list of (old_url, new_url)
        
        for url, occurrences in url_to_files.items():
            if url in all_mappings:
                webp_filename = all_mappings[url]
                if self.webp_base_url:
                    new_url = f"{self.webp_base_url.rstrip('/')}/{webp_filename}"
                else:
                    new_url = webp_filename
                    
                for file_path, _ in occurrences:
                    if file_path not in files_to_update:
                        files_to_update[file_path] = []
                    files_to_update[file_path].append((url, new_url))

        for file_path, replacements in files_to_update.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for old_url, new_url in replacements:
                    content = content.replace(old_url, new_url)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                result.files_updated += 1
                print(f"✅ Updated: {file_path}")
                
            except Exception as e:
                error_msg = f"Error updating {file_path}: {e}"
                print(f"❌ {error_msg}")
                result.errors.append(error_msg)

        # Print summary
        print("\n" + "=" * 60)
        print("ETL COMPLETE - Summary")
        print("=" * 60)
        print(f"Total unique URLs found: {result.total_urls_found}")
        print(f"Downloaded & converted:  {result.downloaded}")
        print(f"Skipped (existing):      {result.skipped}")
        print(f"Markdown files updated:  {result.files_updated}")
        print(f"Errors:                  {len(result.errors)}")
        
        if result.errors:
            print("\nErrors encountered:")
            for err in result.errors[:5]:
                print(f"  - {err}")
            if len(result.errors) > 5:
                print(f"  ... and {len(result.errors) - 5} more errors")

        return result
