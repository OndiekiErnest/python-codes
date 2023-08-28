# store runtime data for asfa
__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

from typing import Set, Tuple
from os import walk, scandir, path

class Data(object):

    # streamline memory usage
    __slots__ = ("root", "folders", "files", "downloaded", "exclude")

    def __init__(self, root: str):
        self.root = root
        self.folders = self.get_folders()
        self.files = set()
        self.downloaded = set()
        # file extensions to avoid
        self.exclude = {".bat"}

    def get_files(self, folder: str) -> Tuple:
        """
            return the files in a folder
        """

        files = set()
        # basename = path.basename(folder)
        for entry in scandir(folder):
            _, ext = path.splitext(entry.name)
            if entry.is_file() and ext not in self.exclude:
                files.add(entry.name)
        return folder, files

    def get_folders(self):
        """
        """

        folders = set()
        for folder, subfolders, files in walk(self.root):
            if files:
                folders.add(folder)
        return folders


if __name__ == '__main__':
    root = "C:\\Users\\code\\Music\\Playlists"
    data = Data(root)
    folders = data.get_folders()
    folder_files = data.get_files(root)
    print(len(folders), folders)
    print(len(folder_files[1]), folder_files)
