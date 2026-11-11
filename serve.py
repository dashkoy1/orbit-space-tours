#!/usr/bin/env python3
"""Local server with HTTP Range support (Safari needs it to play/seek video). Usage: python3 serve.py [port]"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        self._left = None
        rng = self.headers.get('Range')
        path = self.translate_path(self.path)
        m = rng and re.match(r'bytes=(\d*)-(\d*)$', rng)
        if not m or not os.path.isfile(path):
            return super().send_head()
        size = os.path.getsize(path)
        a, b = m.groups()
        start = int(a) if a else max(0, size - int(b))
        end = min(int(b), size - 1) if a and b else size - 1
        if start >= size:
            self.send_error(416); return None
        f = open(path, 'rb'); f.seek(start)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        self._left = end - start + 1
        return f

    def copyfile(self, src, dst):
        left = getattr(self, '_left', None)
        if left is None:
            return super().copyfile(src, dst)
        while left > 0:
            chunk = src.read(min(65536, left))
            if not chunk: break
            dst.write(chunk); left -= len(chunk)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
print(f'http://localhost:{port}')
ThreadingHTTPServer(('', port), Handler).serve_forever()
