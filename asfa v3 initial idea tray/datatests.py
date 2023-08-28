import os
import numpy as np
import pandas as pd
import sys


def convert_bytes(num: int) -> str:
    if num >= 1073741824:
        return f"{round(num / 1073741824, 2)} GB"
    elif num >= 1048576:
        return f"{round(num / 1048576, 2)} MB"
    elif num >= 1024:
        return f"{round(num / 1024, 2)} KB"
    else:
        return f"{num} Bytes"

    
def get_files(folder: str):
    """
        return the file and its stats
    """

    file_excludes = {"AlbumArtSmall.jpg", "Folder.jpg", "desktop.ini"}
    other_file_excludes = ("AlbumArt_",)
    for entry in os.scandir(folder):
        # avoid listing folder-info files
        if entry.is_file() and not (entry.name.startswith(other_file_excludes) or entry.name in file_excludes):
            ext = os.path.splitext(entry.name)[-1]
            ext = f"{ext.strip('.').upper()} File"
            stats = entry.stat()
            size = convert_bytes(stats.st_size)
            yield entry.name, folder, ext, size


def get_folders(path: str) -> list:
    """
        return all recursive folders in path
    """

    folders = []
    for folder, subfolders, files in os.walk(path):
        if files:
            folders.append(folder)
    folders.sort()
    return folders

if __name__ == "__main__":
    folders = get_folders(os.path.expanduser("~\\Downloads"))
    generators = [get_files(folder) for folder in folders]
    files = [row for generator in generators for row in generator]
    print("List size:", sys.getsizeof(files) / 1024, "MB, Length:", len(files))
    
    # numpy array are around 3.5X larger in size than list
    # files = np.array(files, dtype="object")
    # print("Numpy size:", sys.getsizeof(files) / 1024, "MB, Length:", len(files))
    
    # pandas dataframe is much larger, 46.5X
    # files = pd.DataFrame(files, columns=("Name", "Dir", "Type", "Size"))
    # print("Pandas size:", sys.getsizeof(files) / 1024, "MB, Length:", len(files))
    
    
