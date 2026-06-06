import os
import json
import logging
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
HOST = os.getenv("FRONTEND_HOST", "127.0.0.1")
PORT = int(os.getenv("FRONTEND_PORT", "3003"))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("texstyle.frontend")


class SpaHandler(SimpleHTTPRequestHandler):
    def proxy_api(self):
        target = f"{BACKEND_URL}{self.path}"
        body = None
        if self.command in {"POST", "PUT", "PATCH"}:
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))

        headers = {
            key: value
            for key, value in self.headers.items()
            if key.lower() not in {"host", "content-length"}
        }
        request = urllib.request.Request(target, data=body, headers=headers, method=self.command)

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                response_body = response.read()
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in {"transfer-encoding"}:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response_body)
        except urllib.error.HTTPError as error:
            response_body = error.read()
            logger.warning(
                "proxy method=%s path=%s backend_status=%s response=%s",
                self.command,
                self.path,
                error.code,
                response_body.decode("utf-8", errors="replace"),
            )
            self.send_response(error.code)
            for key, value in error.headers.items():
                if key.lower() not in {"transfer-encoding"}:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response_body)
        except (urllib.error.URLError, TimeoutError) as error:
            logger.exception("proxy method=%s path=%s backend_unavailable", self.command, self.path)
            response_body = json.dumps(
                {
                    "detail": f"Backend serverga ulanib bo'lmadi: {error}",
                    "path": self.path,
                }
            ).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.proxy_api()
        return super().do_POST()

    def do_PUT(self):
        if self.path.startswith("/api/"):
            return self.proxy_api()
        return super().do_PUT()

    def do_DELETE(self):
        if self.path.startswith("/api/"):
            return self.proxy_api()
        return super().do_DELETE()

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy_api()
        requested = Path(self.translate_path(self.path))
        if not requested.exists() and "." not in Path(self.path).name:
            self.path = "/index.html"
        return super().do_GET()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), SpaHandler)
    print(f"Serving TexStyle CRM on http://{HOST}:{PORT}/")
    server.serve_forever()
