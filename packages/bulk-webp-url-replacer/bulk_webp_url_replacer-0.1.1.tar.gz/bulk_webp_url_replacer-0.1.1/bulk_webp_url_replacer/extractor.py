"""Image URL extraction from markdown files."""
import re
from pathlib import Path
from typing import List, Tuple, Set


class ImageURLExtractor:
    """Extracts image URLs from markdown files."""

    # Patterns to match image URLs in markdown
    PATTERNS = [
        # YAML frontmatter: image: "https://..."
        re.compile(r'^image:\s*["\']?(https?://[^"\'>\s]+)["\']?\s*$', re.MULTILINE),
        # TOML frontmatter: image = "https://..."
        re.compile(r'^image\s*=\s*["\']?(https?://[^"\'>\s]+)["\']?\s*$', re.MULTILINE),
        # Gallery shortcode URLs: -   https://...
        re.compile(r'^\s*-\s+(https?://[^\s]+\.(jpg|jpeg|png|gif|webp))\s*$', re.MULTILINE | re.IGNORECASE),
        # Standard markdown images: ![alt](https://...)
        re.compile(r'!\[[^\]]*\]\((https?://[^)]+)\)', re.MULTILINE),
        # HTML img tags: <img src="https://...">
        re.compile(r'<img[^>]+src=["\']?(https?://[^"\']+)["\']?', re.IGNORECASE),
    ]

    def extract_from_file(self, file_path: str) -> List[Tuple[int, str]]:
        """
        Extract image URLs from a markdown file.
        
        Returns:
            List of (line_number, url) tuples
        """
        results = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all URLs using patterns
            found_urls: Set[str] = set()
            for pattern in self.PATTERNS:
                for match in pattern.finditer(content):
                    url = match.group(1)
                    if url not in found_urls:
                        found_urls.add(url)
                        # Find line number
                        pos = match.start()
                        line_num = content[:pos].count('\n') + 1
                        results.append((line_num, url))
                        
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
        return results

    def extract_from_directory(self, directory: str) -> List[Tuple[str, int, str]]:
        """
        Extract image URLs from all markdown files in a directory.
        
        Returns:
            List of (file_path, line_number, url) tuples
        """
        results = []
        content_path = Path(directory)
        
        for md_file in content_path.rglob('*.md'):
            file_urls = self.extract_from_file(str(md_file))
            for line_num, url in file_urls:
                results.append((str(md_file), line_num, url))
                
        return results
