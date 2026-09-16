#!/usr/bin/env python3
"""One-click dev server for the MANO HAND ONLINE viewer.

Serves this folder over HTTP and opens it in your default browser:

    python serve.py                 # -> http://localhost:8765/
    python serve.py --port 9000     # use another port
    python serve.py --no-browser    # start the server only
    python serve.py --bind 0.0.0.0  # expose it on your local network

Why not just `python -m http.server 8765`?

  * the browser opens by itself, so a double-click is enough;
  * `http.server` binds to every interface by default, this one stays
    local-only unless you explicitly ask otherwise;
  * if the port is busy it walks up to the next free one instead of
    dying with "Address already in use";
  * responses are marked no-store, so a plain reload always shows the
    current file on disk.

Requires Python 3.8+. No third-party packages.
"""
from __future__ import annotations

import argparse
import contextlib
import http.server
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_PORT = 8765
PORT_TRIES = 20
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


class Handler(http.server.SimpleHTTPRequestHandler):
    """Static file handler rooted at this script's folder."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("  {}\n".format(fmt % args))


class Server(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


def pick_port(host: str, port: int) -> int:
    """Return the first free port at or after `port`."""
    for candidate in range(port, port + PORT_TRIES):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind((host, candidate))
            except OSError:
                continue
            return candidate
    raise SystemExit(
        "No free port in range {}-{}. Try `python serve.py --port 9000`.".format(
            port, port + PORT_TRIES - 1
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="serve.py",
        description="Serve the MANO HAND ONLINE viewer on a local HTTP server.",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=DEFAULT_PORT,
        help="port to listen on; falls back to the next free port (default: %(default)s)",
    )
    parser.add_argument(
        "--bind", default="127.0.0.1",
        help="interface to bind to; use 0.0.0.0 to share it on the LAN (default: %(default)s)",
    )
    parser.add_argument(
        "--no-browser", action="store_true",
        help="do not open the default browser",
    )
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    port = pick_port(args.bind, args.port)
    host = "localhost" if args.bind in LOCAL_HOSTS else args.bind
    url = "http://{}:{}/".format(host, port)

    try:
        httpd = Server((args.bind, port), Handler)
    except OSError as exc:
        print("Could not start the server: {}".format(exc), file=sys.stderr)
        return 1

    print("MANO HAND ONLINE — serving {}".format(ROOT))
    print("  {}".format(url))
    if args.bind not in LOCAL_HOSTS:
        print("  (reachable from other devices on your network)")
    print("  Press Ctrl+C to stop.")

    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()

    try:
        with httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
