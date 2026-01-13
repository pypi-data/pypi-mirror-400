# bulk-webp-url-replacer

[link](https://github.com/HoangYell/bulk-webp-url-replacer)

Bulk convert images to WebP and automatically update URLs in markdown files with a custom CDN prefix.

## Features

- 🔍 **Extract** image URLs from markdown files (frontmatter, galleries, inline images)
- 📥 **Download** images from remote URLs (parallel downloads)
- 🖼️ **Convert** to optimized WebP format
- 🔄 **Replace** original URLs with new CDN-prefixed paths
- ⏭️ **Skip** already-processed images and excluded extensions
- 👀 **Dry-run** mode to preview changes

## Installation

```bash
pip install bulk-webp-url-replacer
```

Or install from source:

```bash
git clone https://github.com/HoangYell/bulk-webp-url-replacer.git
cd bulk-webp-url-replacer
pip install -e .
```

## Usage

### CLI

```bash
# Dry run - preview what would be processed
bulk-webp-url-replacer \
  --scan-dir ./content \
  --output-dir ./webp_images \
  --dry-run

# Full run with custom URL prefix
bulk-webp-url-replacer \
  --scan-dir ./content \
  --output-dir ./webp_images \
  --new-url-prefix "https://cdn.example.com/images"

# Faster with more threads
bulk-webp-url-replacer \
  --scan-dir ./content \
  --output-dir ./webp_images \
  --new-url-prefix "https://cdn.example.com/images" \
  --threads 8
```

### As Python Module

```bash
python -m bulk_webp_url_replacer \
  --scan-dir ./content \
  --output-dir ./webp_images \
  --new-url-prefix "https://cdn.example.com/images"
```

### Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--scan-dir` | Yes | - | Directory to scan for files containing image URLs |
| `--output-dir` | Yes | - | Directory to save converted WebP images |
| `--new-url-prefix` | No | - | URL prefix to replace old image URLs |
| `--quality` | No | 80 | WebP quality 1-100 |
| `--max-width` | No | 1200 | Max image width in pixels |
| `--exclude-ext` | No | gif svg webp ico | File extensions to skip |
| `--threads` | No | 4 | Number of parallel download threads |
| `--dry-run` | No | - | Preview changes without downloading or modifying files |

## Supported Patterns

The tool detects image URLs in:

```markdown
# YAML frontmatter
---
image: "https://example.com/image.jpg"
---

# TOML frontmatter
+++
image = "https://example.com/image.jpg"
+++

# Gallery shortcodes
{{< gallery >}}
- https://example.com/photo1.jpg
- https://example.com/photo2.png
{{< /gallery >}}

# HTML img tags in shortcodes
{{< embed >}}
<img src="https://example.com/image.jpg" width="250" height="250"/>
{{< /embed >}}

# Standard markdown
![Alt text](https://example.com/image.jpg)
```

## Output

After running, you'll have:

1. **WebP images** in your `--output-dir`
2. **mapping.json** tracking original → WebP conversions
3. **Updated files** with new URLs

## License

MIT
