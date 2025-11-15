import base64
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime
import hashlib
from config import USE_PNG


def _save_thumbnail_png(image, url, idx):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"thumb_{timestamp}_{url_hash}_{idx}.png"

    images_dir = Path(__file__).parent.parent / 'images'
    images_dir.mkdir(exist_ok=True)

    filepath = images_dir / filename
    image.save(filepath, format='PNG')

    return f"images/{filename}"


def process_images(url, max_images=5, thumbnail_size=(200, 200)):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        img_tags = soup.find_all('img', src=True)[:max_images]

        thumbnails = []
        for idx, img_tag in enumerate(img_tags):
            img_url = urljoin(url, img_tag['src'])

            try:
                img_response = requests.get(img_url, timeout=10)
                img_response.raise_for_status()

                image = Image.open(BytesIO(img_response.content))

                image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)

                if USE_PNG:
                    thumb_path = _save_thumbnail_png(image, url, idx)
                    thumbnails.append(thumb_path)
                else:
                    buffer = BytesIO()
                    image_format = image.format if image.format else 'PNG'
                    image.save(buffer, format=image_format)
                    buffer.seek(0)

                    thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    thumbnails.append(thumbnail_base64)

            except:
                continue

        return thumbnails

    except Exception as e:
        return []
