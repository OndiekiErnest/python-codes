# code for file browser
__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


from ftplib import FTP_TLS, error_perm
import os
import common


class ServerBrowser:
    def __init__(self):
        self.address = None
        self.port = 3000
        self.dst_dir = None
        self.browser_history = [""]
        self.signals = common.BasicSignals()

    def updateHost(self, host: tuple):
        self.address, self.port = host

    def updateDir(self, path, forward=1):
        if path and (forward):
            self.browser_history.append(path)

    def getFilesList(self):
        """ return a list of files/folders and their sizes """
        self.signals.success.emit("Fetching files, hang in there...")
        ftp = FTP_TLS()
        ftp.certfile = common.CERTF

        try:
            ftp.connect(self.address, self.port)
            ftp.login()
            # set up a secure data channel
            ftp.prot_p()
            ftp.encoding = "utf-8"
            cwdir = "/".join(self.browser_history)
            ftp.cwd(cwdir)

            for item in ftp.mlsd():
                f_exists = 0
                name, size = common._basename(item[0]), int(item[1].get("size", 0))
                file_type = "Folder" if item[1]["type"] == "dir" else "File"
                if file_type == "File" and (common.isSysFile(name)):
                    # skip
                    continue
                local_path = os.path.join(self.dst_dir, name)
                if os.path.exists(local_path) and (os.path.getsize(local_path) == size):
                    f_exists = 1
                yield (name, f_exists, file_type, size)
            # quit the connection
            ftp.quit()
            self.signals.success.emit("")

        except Exception as e:
            ftp.close()
            self.browser_history = [""]
            self.signals.error.emit(str(e))
            yield
