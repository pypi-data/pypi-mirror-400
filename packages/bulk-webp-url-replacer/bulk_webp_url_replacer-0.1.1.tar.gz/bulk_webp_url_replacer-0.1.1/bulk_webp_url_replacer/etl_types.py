from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ImageMapping:
    """Maps an original image URL to its processed WebP file."""
    original_url: str
    raw_path: str  # Path where raw image was downloaded
    webp_path: str  # Path to converted WebP file
    webp_filename: str  # Just the filename for replacement


@dataclass
class ETLResult:
    """Contains the results of an ETL run."""
    total_urls_found: int = 0
    downloaded: int = 0
    converted: int = 0
    files_updated: int = 0
    skipped: int = 0
    errors: List[str] = field(default_factory=list)
    mappings: Dict[str, str] = field(default_factory=dict)  # original_url -> webp_filename
