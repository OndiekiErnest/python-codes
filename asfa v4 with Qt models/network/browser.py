# code for file browser
__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"


from ftplib import FTP_TLS, error_perm
import os
import common

downloads_folder = os.path.expanduser("~\\Downloads")


class ServerBrowser:
    def __init__(self):
        self.address = None
        self.port = 2121
        self.current_dir = ""
        self.file_excludes = common.file_excludes
        self.other_file_excludes = common.other_file_excludes
        self.browser_history = [self.current_dir]

    def updateHost(self, host: tuple):
        self.address, self.port = host

    def updateDir(self, path):
        if path and (path not in self.browser_history):
            self.browser_history.append(path)
        self.current_dir = path

    def getFilesList(self):
        """ return a list of files/folders and their sizes """
        ftp = FTP_TLS()
        ftp.certfile = common.CERTF

        try:
            print("Getting file list from:", self.address, self.port)
            ftp.connect(self.address, self.port)
            ftp.login()
            # set up a secure data channel
            ftp.prot_p()
            ftp.encoding = "utf-8"
            cwdir = "/".join(self.browser_history)
            print("------>", cwdir)
            ftp.cwd(cwdir)

            for item in ftp.mlsd():
                f_exists = 0
                name, size = item[0], int(item[1].get("size", 0))
                file_type = "Folder" if item[1]["type"] == "dir" else "File"
                if file_type == "File" and (name.startswith(self.other_file_excludes) or name in self.file_excludes):
                    # skip
                    continue
                local_path = os.path.join(downloads_folder, name)
                if os.path.exists(local_path) and (os.path.getsize(local_path) == size):
                    f_exists = 1
                yield (name, f_exists, file_type, size)
            # quit the connection
            ftp.quit()

        except Exception as e:
            ftp.close()
            print("[Error getting filelist]", e)
            yield ()

    def getRecursiveFileList(self):
        pass

    def pathExists(self, host, port, pwd):
        ftp = FTP_TLS()
        ftp.certfile = common.CERTF
        if (not host) or (not port) or (not pwd):
            return False
        try:
            ftp.connect(host, port)
            ftp.login()
            # set up a secure data channel
            ftp.prot_p()
            ftp.cwd(pwd)
            ftp.quit()
            return True
        except error_perm:
            return False

    def homedir(self) -> str:
        """ return the parent working dir """
        try:
            ftp = FTP_TLS()
            ftp.certfile = common.CERTF
            ftp.connect(self.address, self.port)
            ftp.login()
            # set up a secure data channel
            ftp.prot_p()
            ftp.encoding = "utf-8"
            pwd = ftp.pwd()
            ftp.quit()
            return pwd
        except Exception:
            ftp.close()
