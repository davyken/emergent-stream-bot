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

def keep_alive_ping():
    """Pings the Render server every 10 minutes to prevent it from sleeping."""
    render_url = os.environ.get("RENDER_URL")
    if not render_url:
        return
    while True:
        try:
            urllib.request.urlopen(render_url, timeout=30)
            print(f"🔄 Keep-alive ping sent to {render_url}")
        except Exception as e:
            print(f"⚠️ Keep-alive ping failed: {e}")
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    
    keep_alive = os.environ.get("RENDER_URL")
    if keep_alive:
        threading.Thread(target=keep_alive_ping, daemon=True).start()
        print(f"🔄 Keep-alive ping enabled: {keep_alive} every 10 minutes")

    from src.bot import main
    main()