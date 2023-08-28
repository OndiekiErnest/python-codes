__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

# Using examples from https://pythonhosted.org/pyftpdlib/tutorial.html

from pyftpdlib.handlers import ThrottledDTPHandler, TLS_FTPHandler, TLS_DTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed

import common
import os
from PyQt5.QtCore import QThread


server_logger = common.logging.getLogger(__name__)

server_logger.debug(f"Initializing {__name__}")


class asfaServerAuthorizer(DummyAuthorizer):
    """
    custom server authorizer
    inherits:
        DummyAuthorizer
    """

    def validate_authentication(self, username, password, handler):
        """
        Raises AuthenticationFailed if supplied username and
        password don't match the stored credentials, else return
        None.
        """

        msg = "Authentication failed."

        if not self.has_user(username):
            if not username or (username == 'anonymous'):
                msg = "Anonymous access not allowed."
            raise AuthenticationFailed(msg)

        elif username != 'anonymous':
            if self.user_table[username]["pwd"] != password:
                raise AuthenticationFailed(msg)


class MixedHandler(ThrottledDTPHandler, TLS_DTPHandler):
    """
    A DTP handler which supports SSL and bandwidth throttling
    """


class Server(QThread):
    def __init__(self):
        super().__init__()
        self.port = 3000
        self.sharedDir = ""
        self.added_users = set()
        self.signals = common.BasicSignals()
        self.dtp_handler = MixedHandler
        # self.dtp_handler.read_limit = 4194304
        self.ftp_handler = TLS_FTPHandler
        self.ftp_handler.log_prefix = "asfa[%(username)s]-%(remote_ip)s"
        self.ftp_handler.dtp_handler = self.dtp_handler
        self.ftp_handler.certfile = common.CERTF
        self.ftp_handler.tls_control_required = True
        self.ftp_handler.tls_data_required = True
        # self.ftp_handler.banner = "asfa"
        self.authorizer = asfaServerAuthorizer()
        self.ftp_handler.authorizer = self.authorizer

        self.setTerminationEnabled(1)

    def set_port(self, port):
        self.port = port

    def setUser(self, username, password, path):
        if not os.path.exists(path):
            # notify user of this error
            self.signals.error.emit(f"Error: '{path}' does not exist")
            return
        if username not in self.added_users:
            self.added_users.add(username)
            # self.authorizer.add_anonymous(path)
            self.authorizer.add_user(username, password, path)
            self.signals.success.emit(f"Shared folder set: '{path}'")
        else:
            self.signals.error.emit(f"Username ({username}) already exists. Let's try a different one")

    def delete_user(self, username: str):
        """ remove authorized username """
        try:
            self.authorizer.remove_user(username)
            self.added_users.remove(username)
            self.signals.success.emit(f"Username ({username}) removed successfully")
        except KeyError:
            pass

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
        self.server = FTPServer((common.MACHINE_IP, self.port), self.ftp_handler)
        self.finished.connect(self.server.close_all)
        self.server.serve_forever()
        # if it ever stops serving forever
        self.server = None
