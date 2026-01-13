"""CLI interface for bulk-webp-url-replacer."""
import argparse
import sys
from .pipeline import ImageETL


def main():
    parser = argparse.ArgumentParser(
        prog="bulk-webp-url-replacer",
        description="Bulk convert images to WebP and update URLs in markdown files"
    )
    
    parser.add_argument(
        "--scan-dir", 
        required=True, 
        help="Directory to scan for files containing image URLs (e.g., markdown, HTML)"
    )
    parser.add_argument(
        "--output-dir", 
        required=True, 
        help="Directory to save converted WebP images"
    )
    parser.add_argument(
        "--new-url-prefix", 
        help="URL prefix to replace old image URLs (e.g., https://cdn.example.com/images)"
    )
    parser.add_argument(
        "--quality", 
        type=int, 
        default=80, 
        help="WebP quality 1-100 (default: 80)"
    )
    parser.add_argument(
        "--max-width", 
        type=int, 
        default=1200, 
        help="Max image width in pixels (default: 1200)"
    )
    parser.add_argument(
        "--exclude-ext",
        nargs="+",
        default=["gif", "svg", "webp", "ico"],
        help="File extensions to skip (default: gif svg webp ico). Example: --exclude-ext gif svg"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of parallel download threads (default: 4)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Preview changes without downloading or modifying files"
    )

    args = parser.parse_args()

    etl = ImageETL(
        content_dir=args.scan_dir,
        webp_dir=args.output_dir,
        webp_base_url=args.new_url_prefix,
        quality=args.quality,
        max_width=args.max_width,
        exclude_extensions=args.exclude_ext,
        threads=args.threads
    )
    
    result = etl.run(dry_run=args.dry_run)
    
    if result.errors:
        sys.exit(1)


if __name__ == "__main__":
    main()


