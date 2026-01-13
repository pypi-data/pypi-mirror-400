"""Image optimizer - downloads and converts images to WebP."""
import os
import time
import requests
from io import BytesIO
from PIL import Image


class ImageOptimizer:
    """Handles downloading and optimizing images."""

    # Headers to mimic a browser request
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    def __init__(self, quality: int = 80, max_width: int = 1200, max_retries: int = 2):
        self.quality = quality
        self.max_width = max_width
        self.max_retries = max_retries

    def _download_with_retry(self, url: str) -> bytes:
        """Download image with retry and exponential backoff."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.HEADERS, timeout=30)
                
                # Handle rate limiting
                if response.status_code == 429:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"   ⏳ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response.content
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   ⏳ Retry {attempt + 1}/{self.max_retries} in {wait_time}s...")
                    time.sleep(wait_time)
        
        raise last_error or Exception(f"Failed to download after {self.max_retries} retries")

    def download_and_optimize(self, url: str, save_path: str, format: str = 'WEBP') -> bool:
        """Downloads an image from URL and saves an optimized version."""
        try:
            if url.startswith(('http://', 'https://')):
                content = self._download_with_retry(url)
                img = Image.open(BytesIO(content))
            else:
                # Treat as local file path
                img = Image.open(url)
            
            # Convert to RGB if saving as JPEG or if original is RGBA/P
            if format.upper() == 'JPEG' and img.mode != 'RGB':
                img = img.convert('RGB')
            elif img.mode == 'RGBA' and format.upper() == 'WEBP':
                # WebP supports RGBA, keep it
                pass
            elif img.mode == 'P':
                img = img.convert('RGBA' if format.upper() == 'WEBP' else 'RGB')
                
            # Resize if too large
            if img.width > self.max_width:
                ratio = self.max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((self.max_width, new_height), Image.Resampling.LANCZOS)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            img.save(save_path, format=format, quality=self.quality, optimize=True)
            return True
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return False

