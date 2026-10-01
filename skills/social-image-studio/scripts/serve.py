#!/usr/bin/env python3
"""Serve the self-contained editor on localhost, optionally loading a JSON draft."""
import argparse
import json
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--content', type=Path, help='UTF-8 JSON draft to load on opening')
    args = parser.parse_args()
    content = None
    if args.content:
        try:
            content = args.content.read_bytes()
            json.loads(content)
        except (OSError, ValueError) as error:
            parser.error(f'Cannot read content JSON: {error}')
    assets = Path(__file__).resolve().parents[1] / 'assets'

    class Handler(SimpleHTTPRequestHandler):
        def log_request(self, code='-', size='-'):
            # A long-running local session must not block on access-log output.
            pass

        def end_headers(self):
            self.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def do_GET(self):
            # Always return complete assets while iterating on the local editor.
            for header in ('If-Modified-Since', 'If-None-Match'):
                if header in self.headers:
                    del self.headers[header]
            if self.path.split('?')[0] == '/initial.json':
                if content is None:
                    self.send_response(204)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            super().do_GET()

    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(assets)))
    except OSError as error:
        parser.error(f'Cannot start server: {error}. Try another --port.')
    print(f'纸页工作台：http://127.0.0.1:{server.server_port}', flush=True)
    print('按 Ctrl+C 停止。所有编辑和导出都在浏览器本地完成。', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
