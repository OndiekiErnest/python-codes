from ftplib import FTP, error_perm
import os

output_folder = "data"


class D:
    """ Download using ftp """

    def __init__(self, file, cwd):
        self.filename = file
        self.cwdir = cwd
        self.dst_dir = os.path.expanduser("~\\Music")

    def callback(self, data):

        self.fileptr.write(data)

    def download(self):
        self.ftp = FTP()
        try:
            file = os.path.join(self.dst_dir, self.filename)
            self.fileptr = open(file, "wb")
            self.ftp.connect("127.0.0.1", 21)
            self.ftp.login()
            # change working dir
            self.ftp.cwd(self.cwdir)

            self.ftp.retrbinary("RETR " + self.filename, self.callback)
        except error_perm as e:
            print("Server did not find file:", self.filename, e)
            self.ftp.quit()
            self.fileptr.close()
        except PermissionError:
            self.ftp.close()
            print("Permissin to write denied")
        else:
            print(self.filename, "completed")
            self.ftp.quit()
            self.fileptr.close()
            self.ftp = None
            self.fileptr = None


if __name__ == '__main__':
    ftp_client = FTP()
    # ftp_client.set_debuglevel(2)
    ftp_client.connect("127.0.0.1", 21)
    ftp_client.login()
    ftp_client.encoding = "utf-8"
    cwd_path = "/4_6039513020848145590/python-example-video/1 - Creating a Dice Rolling Simulator in Python"
    # ftp_client.cwd(cwd_path)
    print("Logged in!")
    print("\nFiles:\n\n")

    for item in ftp_client.mlsd():
        name, size = item[0], item[1].get("size", 0)
        file_type = "Folder" if item[1]["type"] == "dir" else "File"
        print(size, file_type, ":", repr(name))
    ftp_client.quit()
    # downloader = D("Iterating over Collections.mp4", cwd_path)
    # downloader.download()
    # x = input("Done?")
