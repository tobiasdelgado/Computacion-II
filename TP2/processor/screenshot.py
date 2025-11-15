import base64
from io import BytesIO
from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import hashlib
from config import USE_PNG


def _save_screenshot_png(screenshot_bytes, url):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    filename = f"screenshot_{timestamp}_{url_hash}.png"

    images_dir = Path(__file__).parent.parent / 'images'
    images_dir.mkdir(exist_ok=True)

    filepath = images_dir / filename
    filepath.write_bytes(screenshot_bytes)

    return f"images/{filename}"


def generate_screenshot(url, timeout=30000):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=timeout)

            screenshot_bytes = page.screenshot(full_page=True)

            browser.close()

            if USE_PNG:
                return _save_screenshot_png(screenshot_bytes, url)
            else:
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                return screenshot_base64

    except Exception as e:
        return f"Error generando screenshot: {str(e)}"
