#!/usr/bin/env python3
"""
Simple HTTP + WebSocket server for ANSE GUI Demo.
Serves HTML from the same directory and WebSocket from the backend.
"""

import asyncio
import json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver
import threading
import webbrowser
import time

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from gui_demo import GUIDemoBackend


def start_http_server(port=8001):
    """Start a simple HTTP server on a different port."""
    handler = SimpleHTTPRequestHandler
    
    class MyHTTPHandler(handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=Path(__file__).parent, **kwargs)
        
        def log_message(self, format, *args):
            # Suppress HTTP logging
            pass
    
    httpd = socketserver.TCPServer(("0.0.0.0", port), MyHTTPHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    
    print(f"✓ HTTP server running on http://localhost:{port}")
    return httpd


async def main():
    """Start both HTTP and WebSocket servers."""
    
    # Start HTTP server
    http_server = start_http_server(port=8001)
    
    # Wait a moment then open browser
    await asyncio.sleep(1)
    webbrowser.open("http://localhost:8001/index.html", new=1)
    
    # Start WebSocket server
    backend = GUIDemoBackend(host="0.0.0.0", port=8000)
    await backend.run()


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("ANSE GUI Demo Server")
        print("="*60 + "\n")
        
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown complete")
