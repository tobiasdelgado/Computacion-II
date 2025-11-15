#!/usr/bin/env python3

import socket
import socketserver
import argparse
import json
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import process_images


process_pool = None


def process_request_worker(url):
    screenshot = generate_screenshot(url)
    performance = analyze_performance(url)
    thumbnails = process_images(url)

    return {
        'screenshot': screenshot,
        'performance': performance,
        'thumbnails': thumbnails
    }


class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            length_bytes = self.request.recv(4)
            if not length_bytes:
                return

            length = int.from_bytes(length_bytes, byteorder='big')

            chunks = []
            bytes_received = 0
            while bytes_received < length:
                chunk = self.request.recv(min(length - bytes_received, 4096))
                if not chunk:
                    break
                chunks.append(chunk)
                bytes_received += len(chunk)

            message = b''.join(chunks)
            data = json.loads(message.decode('utf-8'))

            url = data.get('url')

            future = process_pool.submit(process_request_worker, url)
            result = future.result()

            response_message = json.dumps(result).encode('utf-8')
            response_length = len(response_message)

            self.request.sendall(response_length.to_bytes(4, byteorder='big'))
            self.request.sendall(response_message)

        except Exception as e:
            error_response = {
                'screenshot': '',
                'performance': {'load_time_ms': 0, 'total_size_kb': 0, 'num_requests': 0},
                'thumbnails': [],
                'error': str(e)
            }
            response_message = json.dumps(error_response).encode('utf-8')
            response_length = len(response_message)
            self.request.sendall(response_length.to_bytes(4, byteorder='big'))
            self.request.sendall(response_message)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def main(host, port, num_processes):
    global process_pool

    process_pool = ProcessPoolExecutor(max_workers=num_processes)

    server = ThreadedTCPServer((host, port), ProcessingRequestHandler)

    print(f"Servidor B corriendo en {host}:{port} con {num_processes} procesos")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor B...")
    finally:
        server.shutdown()
        server.server_close()
        process_pool.shutdown(wait=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Servidor de Procesamiento Distribuido')
    parser.add_argument('-i', '--ip', required=True, help='Dirección de escucha')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto de escucha')
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=multiprocessing.cpu_count(),
        help=f'Número de procesos en el pool (default: {multiprocessing.cpu_count()})'
    )

    args = parser.parse_args()

    main(args.ip, args.port, args.processes)
