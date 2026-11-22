#!/usr/bin/env python3
import http.server
import json
import time
import urllib.request

OLLAMA = "http://127.0.0.1:11434"
PORT = 11436
SAMPLING = {"temperature": float, "top_p": float}
_cache = {}


def model_params(model):
    hit = _cache.get(model)
    if hit and time.time() - hit[0] < 60:
        return hit[1]
    req = urllib.request.Request(OLLAMA + "/api/show", data=json.dumps({"model": model}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        text = json.load(r).get("parameters", "")
    params = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] in SAMPLING:
            params[parts[0]] = SAMPLING[parts[0]](parts[1])
    _cache[model] = (time.time(), params)
    return params


def fill_sampling(body):
    try:
        data = json.loads(body)
        params = model_params(data["model"])
    except Exception:
        return body
    missing = {k: v for k, v in params.items() if k not in data}
    if not missing:
        return body
    data.update(missing)
    return json.dumps(data).encode()


class Handler(http.server.BaseHTTPRequestHandler):
    def forward(self, method):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else None
        if body and method == "POST" and self.path.startswith("/v1/"):
            body = fill_sampling(body)
        headers = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length", "connection")}
        req = urllib.request.Request(OLLAMA + self.path, data=body, method=method, headers=headers)
        try:
            r = urllib.request.urlopen(req, timeout=900)
        except urllib.error.HTTPError as e:
            r = e
        with r:
            self.send_response(r.status)
            for k, v in r.headers.items():
                if k.lower() not in ("transfer-encoding", "connection", "content-length"):
                    self.send_header(k, v)
            self.send_header("Connection", "close")
            self.end_headers()
            read = getattr(r, "read1", r.read)
            try:
                while chunk := read(65536):
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

    def do_GET(self):
        self.forward("GET")

    def do_POST(self):
        self.forward("POST")

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
