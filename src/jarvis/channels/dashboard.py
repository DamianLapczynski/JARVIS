"""Tiny local dashboard (stdlib http.server): GET / (page) and GET /api/status (JSON).

Binds to 127.0.0.1 by default. Do not expose it to a network without adding authentication.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from jarvis import __version__
from jarvis.tools.registry import ToolRegistry

PAGE = b"""<!doctype html><meta charset=utf-8><title>Jarvis</title>
<h1>Jarvis skeleton</h1><pre id=s>loading...</pre>
<script>fetch('/api/status').then(r=>r.json()).then(d=>s.textContent=JSON.stringify(d,null,2))</script>"""


def make_handler(registry: ToolRegistry, dry_run: bool):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path == "/api/status":
                body = json.dumps(
                    {
                        "version": __version__,
                        "dry_run": dry_run,
                        "tools": [{"name": t.name, "level": t.level.value} for t in registry.all()],
                    }
                ).encode()
                ctype = "application/json"
            elif self.path == "/":
                body, ctype = PAGE, "text/html; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):  # silence default access log
            return

    return Handler


def serve(registry: ToolRegistry, host: str, port: int, dry_run: bool) -> None:
    server = HTTPServer((host, port), make_handler(registry, dry_run))
    print(f"Dashboard: http://{host}:{port}")
    server.serve_forever()
