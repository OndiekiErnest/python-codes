
# Using examples from https://pythonhosted.org/pyftpdlib/tutorial.html

from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

import socket
from os.path import exists as path_exists
from os.path import getsize

from .customSignals import ServerStatsUpdater

from PyQt5.QtCore import QThread


def isPortAvailable(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    return not (result == 0)


class CustomHandler(FTPHandler):
    stats = ServerStatsUpdater()

    def on_connect(self):
        self.stats.connected()

    def on_disconnect(self):
        self.stats.disconnected()

    def on_file_sent(self, file):
        self.stats.transferred(getsize(file))

    def on_incomplete_file_sent(self, file):
        self.stats.transferred(getsize(file))


class Server(QThread):
    def __init__(self):
        super().__init__()
        self.port = 3000
        self.sharedDir = ""
        self.dtp_handler = ThrottledDTPHandler
        self.ftp_handler = CustomHandler
        self.ftp_handler.banner = "asfa"
        self.connected = 0
        self.bytesTransferred = 0
        self.filesTransferred = 0
        self.setTerminationEnabled(True)

    def setPort(self, port):
        if isPortAvailable(port):
            self.port = port

    def setSharedDirectory(self, path):
        if not path_exists(path):
            return
        self.authorizer = DummyAuthorizer()
        self.authorizer.add_anonymous(path)
        self.ftp_handler.authorizer = self.authorizer

    def setBandwidth(self, netSpeed):
        self.dtp_handler.read_limit = netSpeed
        self.ftp_handler.dtp_handler = self.dtp_handler

    def stopServer(self):
        if self.isRunning():
            self.server.close_all()
            self.quit()
            if not self.wait(1000):
                self.terminate()

    def run(self):
        self.server = FTPServer(("127.0.0.1", self.port), self.ftp_handler)
        self.finished.connect(self.server.close_all)
        self.server.serve_forever()
        # if it ever stops serving forever
        self.server = None
