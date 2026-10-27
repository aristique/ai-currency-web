from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import logging
import mimetypes
import os
from urllib.parse import urlsplit, parse_qs

from .rates import Store, RateError, parse_date

WEB = Path(__file__).resolve().parent.parent.parent / "web"


def handler_for(store):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body):
            payload = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path == "/api/health":
                return self.reply(200, {"status": "ok"})
            if parsed.path == "/api/rates":
                query = parse_qs(parsed.query)
                try:
                    raw = query.get("date", [None])[0]
                    day = parse_date(raw) if raw else None
                    result = store.get(day, cached=query.get("cached") == ["1"])
                    return self.reply(200, result)
                except RateError as exc:
                    cache_date = store.cache_info()
                    return self.reply(503, {"error": str(exc), "cacheAvailable": bool(cache_date),
                                            "cachedDate": cache_date})
            files = {"/": "index.html", "/style.css": "style.css", "/app.js": "app.js"}
            if parsed.path not in files:
                return self.reply(404, {"error": "Страница не найдена."})
            content = (WEB / files[parsed.path]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", (mimetypes.guess_type(files[parsed.path])[0] or "text/plain") + "; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self):
            if self.path != "/api/convert":
                return self.reply(404, {"error": "Страница не найдена."})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    raise RateError("Некорректный размер запроса.")
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise RateError("Ожидается объект запроса.")
                return self.reply(200, store.conversion(body))
            except (RateError, ValueError, TypeError) as exc:
                return self.reply(400, {"error": str(exc)})

        def log_message(self, format, *args):
            logging.info(format, *args)

    return Handler


def main():
    logging.basicConfig(level=logging.INFO)
    store = Store(Path(os.environ.get("DATA_DIR", "/data")))
    server = ThreadingHTTPServer(("0.0.0.0", 8080), handler_for(store))
    server.serve_forever()
