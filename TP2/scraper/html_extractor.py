from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def extract_page_info(html_content, base_url=''):
    soup = BeautifulSoup(html_content, 'lxml')

    title = soup.find('title')
    title_text = title.get_text(strip=True) if title else ''

    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if base_url:
            href = urljoin(base_url, href)
        if _is_valid_url(href):
            links.append(href)

    meta_tags = {}
    for meta in soup.find_all('meta'):
        name = meta.get('name') or meta.get('property')
        content = meta.get('content')
        if name and content:
            meta_tags[name] = content

    images_count = len(soup.find_all('img'))

    structure = {}
    for i in range(1, 7):
        tag_name = f'h{i}'
        structure[tag_name] = len(soup.find_all(tag_name))

    return {
        'title': title_text,
        'links': links,
        'meta_tags': meta_tags,
        'images_count': images_count,
        'structure': structure
    }


def _is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
