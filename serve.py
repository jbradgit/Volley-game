"""Local dev server: disables caching (always load the latest files) AND handles requests concurrently.

THREADING MATTERS: the previous single-threaded socketserver.TCPServer served one connection at a time,
so a browser's concurrent / idle "preconnect" sockets could block the server's only thread and leave
asset requests stuck in "loading..." forever (this is what hung the Vic portrait and stalled early loads).
ThreadingHTTPServer gives each connection its own thread, so nothing starves.
"""
import http.server

PORT = 5578   # off 5577 to escape a stuck service worker cached against the old origin

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    def log_message(self, *a):   # quiet console
        pass

# Bind to localhost only — local dev convenience, not a LAN/public server (AUDIT L-2).
with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), NoCacheHandler) as httpd:
    httpd.daemon_threads = True
    print('SCORDAGOL serving (no-cache, threaded) on http://localhost:%d/index.html' % PORT)
    httpd.serve_forever()
