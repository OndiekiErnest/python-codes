# manage and do file operations
from typing import Optional, IO
import os


class FManager():
    """
    """

    def __init__(self):
        # status 0 means nothing
        self.status = 0
        # buffer in bytes (1 MB)
        self.buffer = 1048576

    def read(self, filename: str) -> Optional[IO]:
        # open a file in read-binary mode and return it
        try:
            file = open(filename, "rb")
            return file
        except Exception:
            return

    def delete(self, filename: str) -> Optional[str]:
        # delete a filename permanently
        try:
            os.remove(filename)
            return filename
        except Exception:
            return

    def write(self, filename: str) -> Optional[IO]:
        # open a file in write-binary mode and return it
        try:
            file = open(filename, "wb")
            return file
        except Exception:
            return


if __name__ == '__main__':
    manager = FManager()
    filename = "C:\\Users\\code\\Desktop\\tests.txt"
    file_obj = manager.write(filename)
    file_obj.write(b"Hello! How are you?")
    # close the file
    file_obj.close()

    file_obj = manager.read(filename)
    print(file_obj.read(1024))
    file_obj.close()
