import os, http.server, socketserver

os.chdir("/Users/matthewschneider/Downloads/salesaiguide")

handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", 8080), handler) as httpd:
    print("Serving on port 8080")
    httpd.serve_forever()
