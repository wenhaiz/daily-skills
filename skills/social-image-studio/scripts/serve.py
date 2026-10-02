#!/usr/bin/env python3
"""Serve the local editor with an optional JSON draft or live Markdown source."""
import argparse
import json
from collections import OrderedDict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlsplit

from markdown_source import MarkdownSource, SourceError


class SourceCache:
    """Keep a small, shared cache of image encodings for recently opened files."""

    def __init__(self, limit=4):
        self.limit = limit
        self._sources = OrderedDict()
        self._lock = Lock()

    def get(self, value):
        if not value or len(value) > 4096 or '\x00' in value:
            raise SourceError('请输入 Markdown 文件的完整路径。')
        path = Path(value)
        if not path.is_absolute():
            raise SourceError('请使用以 / 开头的 Markdown 文件完整路径。')
        if path.suffix.lower() not in ('.md', '.markdown'):
            raise SourceError('请选择 .md 或 .markdown 文件。')
        try:
            path = path.resolve()
            with self._lock:
                source = self._sources.pop(path, None)
                if source is None:
                    source = MarkdownSource(path)
                self._sources[path] = source
                while len(self._sources) > self.limit:
                    self._sources.popitem(last=False)
                return source
        except (ValueError, OSError, RuntimeError):
            raise SourceError('Markdown 文件路径无效，请检查路径。') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument('--content', type=Path, help='UTF-8 JSON draft to load on opening')
    inputs.add_argument('--markdown', type=Path, help='UTF-8 Markdown source to preview live')
    args = parser.parse_args()
    content = None
    if args.content:
        try:
            content = args.content.read_bytes()
            json.loads(content)
        except (OSError, ValueError) as error:
            parser.error(f'Cannot read content JSON: {error}')
    assets = Path(__file__).resolve().parents[1] / 'assets'
    source = MarkdownSource(args.markdown) if args.markdown else None
    source_cache = SourceCache()

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
            if self.path.split('?')[0] == '/source.json':
                active_source = source
                try:
                    try:
                        query = parse_qs(urlsplit(self.path).query, keep_blank_values=True,
                                         max_num_fields=8)
                    except ValueError:
                        raise SourceError('Markdown 请求参数过多或格式无效。') from None
                    if any(key not in ('path', 'revision') or len(values) != 1
                           for key, values in query.items()):
                        raise SourceError('Markdown 请求参数无效，请重新选择文件。')
                    if 'path' in query:
                        active_source = None
                        active_source = source_cache.get(query['path'][0])
                    if active_source is None:
                        self.send_response(204)
                        self.end_headers()
                        return
                    payload = active_source.read()
                    payload['path'] = str(active_source.path)
                    status = 200
                except SourceError as error:
                    payload = active_source.error_response(error) if active_source else {
                        'sourceId': None, 'filename': '', 'error': str(error),
                    }
                    payload['path'] = str(active_source.path) if active_source else ''
                    status = 422
                revision = query.get('revision', [None])[0] if status == 200 else None
                if status == 200 and revision == payload['revision']:
                    self.send_response(204)
                    self.end_headers()
                    return
                data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
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
    if source:
        print(f'Markdown 实时预览：{source.path}', flush=True)
    print('按 Ctrl+C 停止。', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
