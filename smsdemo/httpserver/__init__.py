"""
HTTPServer demo server.
"""

import logging
import socketserver

from smsdemo.httpserver.handler import handler_factory
from smsdemo.util import ServerConfig


def run(conf: ServerConfig):
    handler = handler_factory(conf)
    httpd = socketserver.TCPServer((conf.host, conf.port), handler)
    logging.info("SMS echo server (HTTPServer) running on %s:%d", conf.host, conf.port)
    httpd.serve_forever()
