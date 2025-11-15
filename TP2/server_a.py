#!/usr/bin/env python3

import asyncio
import argparse
from datetime import datetime, timezone
from aiohttp import web

from scraper.http_client import fetch_url
from scraper.html_extractor import extract_page_info
from utils.protocol import async_send_message, async_receive_message
from utils.errors import ScrapingError, CommunicationError


SERVER_B_HOST = "127.0.0.1"
SERVER_B_PORT = 9000


async def communicate_with_server_b(url):
    try:
        reader, writer = await asyncio.open_connection(SERVER_B_HOST, SERVER_B_PORT)

        await async_send_message(writer, {"url": url})

        response = await async_receive_message(reader)

        writer.close()
        await writer.wait_closed()

        return response

    except Exception as e:
        raise CommunicationError(f"Error comunicando con servidor B: {str(e)}")


async def handle_scrape(request):
    url = request.query.get("url")

    if not url:
        return web.json_response(
            {"status": "error", "message": "Falta parámetro url"}, status=400
        )

    try:
        html_content = await fetch_url(url)

        scraping_data = extract_page_info(html_content, url)

        processing_data = await communicate_with_server_b(url)

        response = {
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scraping_data": scraping_data,
            "processing_data": processing_data,
            "status": "success",
        }

        return web.json_response(response)

    except ScrapingError as e:
        return web.json_response(
            {"status": "error", "message": f"Error en scraping: {str(e)}"}, status=500
        )
    except CommunicationError as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)
    except Exception as e:
        return web.json_response(
            {"status": "error", "message": f"Error inesperado: {str(e)}"}, status=500
        )


async def init_app(host, port):
    from pathlib import Path
    from config import USE_PNG

    app = web.Application()
    app.router.add_get("/scrape", handle_scrape)

    if USE_PNG:
        images_dir = Path(__file__).parent / 'images'
        images_dir.mkdir(exist_ok=True)
        app.router.add_static('/images', images_dir, name='images')

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    print(f"Servidor A corriendo en http://{host}:{port}")

    return runner


async def main(host, port):
    runner = await init_app(host, port)

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de Scraping Web Asíncrono")
    parser.add_argument(
        "-i", "--ip", required=True, help="Dirección de escucha (soporta IPv4/IPv6)"
    )
    parser.add_argument(
        "-p", "--port", type=int, required=True, help="Puerto de escucha"
    )
    parser.add_argument(
        "-w", "--workers", type=int, default=4, help="Número de workers (default: 4)"
    )

    args = parser.parse_args()

    asyncio.run(main(args.ip, args.port))
