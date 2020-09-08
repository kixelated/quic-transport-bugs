#!/usr/bin/env python3

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

httpd = HTTPServer(('localhost', 4444), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="localhost.key", certfile='localhost.crt', server_side=True)
httpd.serve_forever()
