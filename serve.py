"""Local dev server that disables caching, so the browser always loads the latest files."""
import http.server, socketserver

PORT = 5577

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('', PORT), NoCacheHandler) as httpd:
    print('Volley Challenge serving (no-cache) on http://localhost:%d/index.html' % PORT)
    httpd.serve_forever()
