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


class MixedHandler(ThrottledDTPHandler, TLS_DTPHandler):
    """
    A DTP handler which supports SSL and bandwidth throttling
    """


class Server(QThread):
    def __init__(self):
        super().__init__()
        self.port = 3000
        self.sharedDir = ""
        self.signals = common.BasicSignals()
        self.dtp_handler = MixedHandler
        # self.dtp_handler.read_limit = 4194304
        self.ftp_handler = TLS_FTPHandler
        self.ftp_handler.log_prefix = "asfa[%(username)s]-%(remote_ip)s"
        self.ftp_handler.dtp_handler = self.dtp_handler
        self.ftp_handler.certfile = common.CERTF
        self.ftp_handler.tls_control_required = 1
        self.ftp_handler.tls_data_required = 1
        self.ftp_handler.banner = "asfa"
        self.setTerminationEnabled(1)

    def set_port(self, port):
        self.port = port

    def setSharedDirectory(self, path):
        if not os.path.exists(path):
            # notify user of this error
            self.signals.error.emit("The folder you set as shared does not exist")
            return
        self.authorizer = DummyAuthorizer()
        self.authorizer.add_anonymous(path)
        self.ftp_handler.authorizer = self.authorizer
        self.signals.success.emit(f"Shared folder set: {path}")

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
