import time
import requests
from bs4 import BeautifulSoup


def analyze_performance(url, timeout=30):
    try:
        start_time = time.time()

        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        load_time_ms = int((time.time() - start_time) * 1000)

        content_length = len(response.content)
        total_size_kb = content_length / 1024

        soup = BeautifulSoup(response.text, 'lxml')
        scripts = len(soup.find_all('script', src=True))
        stylesheets = len(soup.find_all('link', rel='stylesheet'))
        images = len(soup.find_all('img', src=True))

        num_requests = 1 + scripts + stylesheets + images

        return {
            'load_time_ms': load_time_ms,
            'total_size_kb': round(total_size_kb, 2),
            'num_requests': num_requests
        }

    except Exception as e:
        return {
            'load_time_ms': 0,
            'total_size_kb': 0,
            'num_requests': 0,
            'error': str(e)
        }
