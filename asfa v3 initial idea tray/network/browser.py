# code for file browser
from ftplib import FTP, error_perm


class ServerBrowser:
    def __init__(self):
        self.address = None
        self.port = 3000
        self.current_dir = None

    def updateHost(self, host: tuple):
        self.address, self.port = host

    def updateDir(self, path):
        self.current_dir = path

    def getFilesList(self):
        """ return a list of files/folders and their sizes """
        details_lst = []
        ftp = FTP()

        try:
            ftp.connect(self.address, self.port)
            ftp.login()
            ftp.dir(details_lst.append)
            ftp.quit()
            fileslist = []
            for item in details_lst:
                lst = item.split()
                item_type = "File"
                if item.startswith("d"):
                    # is a folder
                    item_type = "Folder"
                name_size_type = (item[55:], item_type, int(lst[4]))
                fileslist.append(name_size_type)
            return fileslist
        except Exception as e:
            ftp.close()
            print("[Error getting filelist]", e)
            return []

    def getRecursiveFileList(self):
        pass

    def pathExists(self, host, port, pwd):
        ftp = FTP()
        if (not host) or (not port) or (not pwd):
            return False
        try:
            ftp.connect(host, port)
            ftp.login()
            ftp.cwd(pwd)
            ftp.quit()
            return True
        except error_perm:
            return False
