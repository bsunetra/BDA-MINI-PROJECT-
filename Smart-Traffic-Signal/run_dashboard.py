import os
import sys
import webbrowser
import http.server
import socketserver

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    os.chdir(DIRECTORY)
    url = f"http://localhost:{PORT}/dashboard.html"
    print(f"Starting Smart Traffic Signal Dashboard at {url}")
    webbrowser.open(url)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running. Press Ctrl+C to exit.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
