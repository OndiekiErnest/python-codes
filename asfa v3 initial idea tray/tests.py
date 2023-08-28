import os
# import asfaUtils


def copy_folder(src_folder: str, dst_folder: str):
    """ copy folder recursively """
    dst = os.path.join(dst_folder, os.path.basename(src_folder))
    if not os.path.exists(dst):
        os.mkdir(dst)
    sorted_items = get_files_folders(src_folder)
    for item in sorted_items:
        if os.path.isfile(item):
            # transfer file
            print(item, "->", dst)
        elif os.path.isdir(item):
            # recurse
            copy_folder(item, dst)


def get_files_folders(path: str):
    """ return a sorted list of files first and lastly folders """
    items = []
    for entry in os.scandir(path):
        if entry.is_file():
            # put files at the beginning
            items.insert(0, entry.path)
        else:
            # put folders at the end
            items.append(entry.path)
    return items


copy_folder("C:\\Users\\code\\Desktop\\Fourth Year", "F:")
