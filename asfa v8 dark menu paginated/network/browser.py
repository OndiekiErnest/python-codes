# code for file browser
__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

from common import BasicSignals, isSysFile, _basename, ftp_tls, error_perm, logging, os


browser_logger = logging.getLogger(__name__)

browser_logger.debug(f"Initializing {__name__}")


class ServerBrowser:
    def __init__(self):
        self.address = None
        self.port = 3000
        self.dst_dir = None
        self.browser_history = [""]
        self.signals = BasicSignals()

    def updateUser(self, host: tuple):
        self.username, self.password, self.address, self.port = host

    def updateDir(self, path, forward=1):
        if path and (forward):
            self.browser_history.append(path)

    def getFilesList(self):
        """ return a list of files/folders and their sizes """
        ftp = ftp_tls()

        try:
            ftp.connect(self.address, self.port)
            ftp.login(user=self.username, passwd=self.password)
            # secure control connection
            # ftp.auth()
            # set up a secure data connection
            ftp.prot_p()
            cwdir = "/".join(self.browser_history)
            ftp.cwd(cwdir)

            browser_logger.debug(f"Fetching files from '{cwdir}'")

            for index, item in enumerate(ftp.mlsd()):
                f_exists = 0
                name, size = _basename(item[0]), int(item[1].get("size", 0))
                file_type = "Folder" if item[1]["type"] == "dir" else "File"
                if file_type == "File" and (isSysFile(name)):
                    # skip
                    continue
                local_path = os.path.join(self.dst_dir, name)
                if os.path.exists(local_path) and (os.path.getsize(local_path) == size):
                    f_exists = 1
                yield (name, f_exists, file_type, size)
            # quit the connection
            ftp.quit()
            browser_logger.debug(f"Fetched {index + 1} items")
            # self.signals.success.emit("Done fetching files")
            self.signals.error.emit("")

        except error_perm as e:
            ftp.close()
            # get back to Home://
            self.browser_history = [""]
            browser_logger.error(f"Error fetching files: {str(e)}")
            self.signals.success.emit("")
            self.signals.error.emit(str(e))
            yield

        except Exception as e:
            ftp.close()
            # get back to Home://
            self.browser_history = [""]
            browser_logger.error(f"Error fetching files: {str(e)}")
            self.signals.success.emit("")
            self.signals.error.emit("Could not fetch items. Click the drop-down menu above to 'connect as'")
            yield
