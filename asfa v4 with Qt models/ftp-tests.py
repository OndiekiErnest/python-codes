from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
import logging


def server():
    authorizer = DummyAuthorizer()
    authorizer.add_anonymous("C:\\Users\\code\\Downloads")
    throttled_handler = ThrottledDTPHandler
    # kbps
    throttled_handler.read_limit = 1024 * 1024
    throttled_handler.write_limit = 1024 * 1024

    handler = FTPHandler
    handler.use_gmt_times = False
    handler.authorizer = authorizer
    handler.dtp_handler = throttled_handler

    # logging.basicConfig(filename="data\\debug.log", level=logging.DEBUG)

    ftp_server = FTPServer(("127.0.0.1", 21), handler)
    ftp_server.serve_forever()


if __name__ == '__main__':
    server()
