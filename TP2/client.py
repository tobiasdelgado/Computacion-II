#!/usr/bin/env python3

import sys
import json
import requests


def main():
    if len(sys.argv) < 2:
        print("Uso: python client.py <URL>")
        print("Ejemplo: python client.py https://example.com")
        sys.exit(1)

    url_to_scrape = sys.argv[1]
    server_url = "http://127.0.0.1:8000/scrape"

    print(f"Solicitando scraping de: {url_to_scrape}")
    print(f"Conectando a servidor en: {server_url}\n")

    try:
        response = requests.get(server_url, params={'url': url_to_scrape}, timeout=60)
        response.raise_for_status()

        data = response.json()

        print("=" * 80)
        print("RESULTADO DEL SCRAPING")
        print("=" * 80)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 80)

        if data.get('status') == 'success':
            print("\n✓ Scraping completado exitosamente")
        else:
            print("\n✗ Error en el scraping")

    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al servidor.")
        print("Asegúrate de que server_a.py esté corriendo en http://127.0.0.1:8000")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: La petición tardó demasiado tiempo")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
