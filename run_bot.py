#!/usr/bin/env python3
import sys
import os
import threading
import time
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, *args):
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), HealthCheck).serve_forever()

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()

    from src.bot import main
    main()
