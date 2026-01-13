from __future__ import annotations

import http.server
import mimetypes
import os
import socket
import socketserver
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import unquote


def find_free_port(start_port: int = 8000, bind: str = "127.0.0.1") -> int:
    port = int(start_port)
    while port < 65535:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((bind, port))
                return port
        except OSError:
            port += 1
    raise RuntimeError("无法找到可用端口")


def _parse_range_header(range_header: str, size: int) -> Optional[tuple[int, int]]:
    # 支持：Range: bytes=start-end / bytes=start- / bytes=-suffix
    if not range_header:
        return None
    if not range_header.startswith("bytes="):
        return None
    spec = range_header[len("bytes=") :].strip()
    if "," in spec:
        # 不支持多段 range
        return None
    if "-" not in spec:
        return None
    start_s, end_s = spec.split("-", 1)
    start_s = start_s.strip()
    end_s = end_s.strip()

    if start_s == "" and end_s == "":
        return None
    if start_s == "":
        # suffix bytes
        suffix = int(end_s)
        if suffix <= 0:
            return None
        start = max(0, size - suffix)
        end = size - 1
        return start, end
    start = int(start_s)
    if end_s == "":
        end = size - 1
    else:
        end = int(end_s)
    if start < 0 or end < start:
        return None
    start = min(start, size)
    end = min(end, size - 1)
    return start, end


def make_handler(*, html_content: str, media_map: Dict[str, Path], html_filename: str = "index.html"):
    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "viz-media-in-html/1.0.0"

        def do_GET(self):  # noqa: N802
            path = unquote(self.path.split("?", 1)[0])
            if path in ("/", f"/{html_filename}", "/index.html"):
                body = html_content.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if path.startswith("/media/"):
                media_id = path[len("/media/") :].strip("/")
                p = media_map.get(media_id)
                if not p:
                    self.send_error(404, "Not Found")
                    return
                self._send_file(p)
                return

            self.send_error(404, "Not Found")

        def log_message(self, fmt: str, *args) -> None:  # noqa: A003
            # 默认仅输出简化信息，避免泄露路径
            msg = fmt % args
            print(msg)

        def _send_file(self, p: Path) -> None:
            try:
                st = p.stat()
            except FileNotFoundError:
                self.send_error(404, "Not Found")
                return

            ctype, _ = mimetypes.guess_type(os.fspath(p))
            if not ctype:
                ctype = "application/octet-stream"

            size = int(st.st_size)
            range_header = self.headers.get("Range", "")
            byte_range = _parse_range_header(range_header, size) if range_header else None

            if byte_range is None:
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(size))
                self.send_header("Accept-Ranges", "bytes")
                self.end_headers()
                with p.open("rb") as f:
                    self.wfile.write(f.read())
                return

            start, end = byte_range
            length = end - start + 1
            self.send_response(206)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            self.end_headers()
            with p.open("rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)

    return Handler


def serve(*, bind: str, port: int, handler_cls):
    class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    with ThreadingTCPServer((bind, port), handler_cls) as httpd:
        httpd.serve_forever()


