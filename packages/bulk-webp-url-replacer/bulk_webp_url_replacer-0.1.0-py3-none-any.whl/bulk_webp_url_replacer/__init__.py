"""
Bulk WebP URL Replacer.
Bulk convert images to WebP and update URLs in markdown files.
"""
from .etl_types import ImageMapping, ETLResult
from .extractor import ImageURLExtractor
from .pipeline import ImageETL

__version__ = "0.1.0"
__all__ = ["ImageETL", "ImageURLExtractor", "ImageMapping", "ETLResult"]
