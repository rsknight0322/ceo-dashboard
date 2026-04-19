#!/usr/bin/env python3
"""
CEO Dashboard – Local Server
─────────────────────────────
Run once:   python3 serve.py
Then open:  http://localhost:8080

Your tasks and KPIs are saved to ceo-dashboard-data.json in this folder.
They will NEVER disappear — even after restarting your computer.
Press Ctrl+C to stop the server.
"""
import http.server
import socketserver
import json
import os
from pathlib import Path

PORT     = 8080
BASE_DIR = Path(__file__).parent.resolve()
DATA     = BASE_DIR / "ceo-dashboard-data.json"
HTML     = BASE_DIR / "CEO Dashboard.html"

TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css":  "text/css",
    ".js":   "application/javascript",
    ".json": "application/json",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif":  "image/gif",
    ".svg":  "image/svg+xml",
    ".ico":  "image/x-icon",
    ".woff": "font/woff",
    ".woff2":"font/woff2",
}

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # keep terminal clean

    # ── CORS headers (needed for fetch() from localhost) ──────────────
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    # ── GET /load  →  return saved JSON (or 204 if no file yet) ──────
    # ── GET /      →  serve the dashboard HTML ────────────────────────
    # ── GET /foo.png etc. → serve static assets ───────────────────────
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/load":
            if DATA.exists():
                body = DATA.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_response(204)
                self._cors()
                self.end_headers()
            return

        if path in ("/", "/index.html", "/CEO%20Dashboard.html", "/CEO Dashboard.html"):
            body = HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._cors()
            self.end_headers()
            self.wfile.write(body)
            return

        # Static asset
        safe = path.lstrip("/").replace("%20", " ")
        fpath = BASE_DIR / safe
        if fpath.exists() and fpath.is_file():
            body = fpath.read_bytes()
            ct = TYPES.get(fpath.suffix.lower(), "application/octet-stream")
            self.send_response(200)
            self.send_header("Content-Type", ct)
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    # ── POST /save  →  write JSON to disk ─────────────────────────────
    def do_POST(self):
        if self.path == "/save":
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n)
            DATA.write_bytes(body)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()


socketserver.TCPServer.allow_reuse_address = True
print(f"\n  ✦  CEO Dashboard is live →  http://localhost:{PORT}")
print(f"     Data file:  {DATA}")
print(f"     Press Ctrl+C to stop.\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
