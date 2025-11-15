import aiohttp
import asyncio
from utils.errors import ScrapingError


async def fetch_url(url, timeout=30):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=timeout),
                headers={'User-Agent': 'Mozilla/5.0 (compatible; ScraperBot/1.0)'}
            ) as response:
                response.raise_for_status()
                return await response.text()

    except asyncio.TimeoutError:
        raise ScrapingError(f"Timeout al acceder a {url}")
    except aiohttp.ClientError as e:
        raise ScrapingError(f"Error al descargar {url}: {str(e)}")
    except Exception as e:
        raise ScrapingError(f"Error inesperado: {str(e)}")
