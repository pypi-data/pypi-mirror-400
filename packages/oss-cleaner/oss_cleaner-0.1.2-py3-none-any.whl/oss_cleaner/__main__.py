import argparse
import webbrowser
import threading
import time
import os
import sys
from .app import app

def open_browser(url):
    """Open browser after a short delay."""
    time.sleep(1.5)
    try:
        webbrowser.open(url)
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(description="OSS Cleaner - Manage orphaned images in Aliyun OSS")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically")
    parser.add_argument("--port", type=int, default=6900, help="Port to run the server on (default: 6900)")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    host = "127.0.0.1"
    url = f"http://{host}:{args.port}"
    
    # Only open browser if not disabled
    if not args.no_browser:
        # If debug is enabled, Werkzeug reloader spawns a child process.
        # We want to open the browser only in the reloader process (WERKZEUG_RUN_MAIN='true')
        # OR if debug is disabled (single process).
        if not args.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
             threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    print(f"Starting OSS Cleaner at {url}")
    app.run(debug=args.debug, port=args.port, host=host)

if __name__ == "__main__":
    main()
