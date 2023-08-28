__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

# Using examples from https://pythonhosted.org/pyftpdlib/tutorial.html

from pyftpdlib.handlers import ThrottledDTPHandler, TLS_FTPHandler, TLS_DTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

import socket
import common
import os
from PyQt5.QtCore import QThread


def isPortAvailable(port):
    """
    test and see if a port number is free or taken
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("127.0.0.1", port))
    return not (result == 0)


class MixedHandler(ThrottledDTPHandler, TLS_DTPHandler):
    """
    A DTP handler which supports SSL and bandwidth throttling
    """


class CustomHandler(TLS_FTPHandler):

    def on_connect(self):
        print("[Connection]")
        # self.connect.emit()

    def on_disconnect(self):
        print("[Disconnection]")
        # self.disconnected.emit()

    def on_file_sent(self, file):
        print("[Received]", file)
        # self.file_sent.emit(getsize(file))

    def on_incomplete_file_sent(self, file):
        print("[Incomplete]", file)
        # self.incomplete_sent.emit(getsize(file))


class Server(QThread):
    def __init__(self):
        super().__init__()
        self.port = 2121
        self.sharedDir = ""
        self.dtp_handler = MixedHandler
        self.dtp_handler.read_limit = 1024 * 1024
        self.ftp_handler = CustomHandler
        self.ftp_handler.dtp_handler = self.dtp_handler
        self.ftp_handler.certfile = common.CERTF
        self.ftp_handler.tls_control_required = 1
        self.ftp_handler.tls_data_required = 1
        self.ftp_handler.banner = "asfa"
        self.connected = 0
        self.bytesTransferred = 0
        self.filesTransferred = 0
        self.setTerminationEnabled(1)

    def setPort(self, port):
        if isPortAvailable(port):
            self.port = port

    def setSharedDirectory(self, path):
        if not os.path.exists(path):
            # notify user of this error
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
        # serve using this machine's IP
        this_ip = socket.gethostbyname(socket.gethostname())
        self.server = FTPServer((this_ip, self.port), self.ftp_handler)
        self.finished.connect(self.server.close_all)
        self.server.serve_forever()
        # if it ever stops serving forever
        self.server = None
