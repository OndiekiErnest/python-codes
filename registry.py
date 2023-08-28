import winreg
import shlex
import errno
import logging
import os


def path_exists(path: str):
    if path.startswith("%") or ("%" in path):
        path = winreg.ExpandEnvironmentStrings(path)
    return os.path.exists(path)


# logging.basicConfig(level=logging.INFO)
reg_logger = logging.getLogger(__name__)
reg_logger.info(f"Initializing {__name__}")


def exe_path_from_ext(ext):
    """ `ext` like '.py' """
    try:
        root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, ext)
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"{root}\\shell\\open\\command") as key:
            # print("KEY >>>", key)
            command = winreg.QueryValueEx(key, "")[0]
            reg_logger.info(f"COMMAND >>> {command}")
            return shlex.split(command)[0]
    except Exception as e:
        reg_logger.error(f"EXTENSION >>> {e} '{ext}'")
        return


def path_from_appid(application_id):
    """ `application_id` like vlc.exe """
    for application_id in (application_id.lower(), application_id.title(), application_id.upper()):
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"Applications\\{application_id}\\shell\\open\\command") as key:
                command = winreg.QueryValueEx(key, "")[0]
                # reg_logger.info(f"COMMAND >>> {command}")
                path = shlex.split(command)[0]
                return path if path_exists(path) else None
        except Exception:
            # reg_logger.error(f"APPLICATION ID >>> {e} '{application_id}'")
            continue


def file_type(ext: str):
    """ `ext` like '.py' """
    try:
        root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, ext)
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, root) as file_type_key:
            file_type = winreg.QueryValueEx(file_type_key, "")
            default = file_type[0].strip("(VLC)")
    except Exception as e:
        reg_logger.error(f"FILE TYPE >>> {e} '{ext}'")
        default = f"{ext.strip('.').upper()} File"
    return default


def open_with_list(ext):

    n = 0
    available = set()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, f"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\{ext}\\OpenWithList") as access_key:
            # print("KEY >>>", access_key)
            while 1:
                try:
                    x = winreg.EnumValue(access_key, n)[1]
                    available.add(path_from_appid(x))
                    n += 1
                except OSError as e:
                    # 'No more data is available' error
                    if e.errno == errno.EINVAL:
                        reg_logger.info("Done. No more data")
                        break
    except Exception as e:
        reg_logger.error(f"OPEN WITH >>> {e} '{ext}'\n")
    print(available)


def app_file_assoc():
    n = 0
    # available = set()
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\RegisteredApplications") as access_key:
            # print("KEY >>>", access_key)
            while 1:
                try:
                    x = winreg.EnumValue(access_key, n)
                    print(x)
                    n += 1
                except OSError as e:
                    # 'No more data is available' error
                    if e.errno == errno.EINVAL:
                        reg_logger.info("Done. No more data")
                        break
    except Exception as e:
        reg_logger.error(f"APP ASSOC >>> {e}\n")
    # print(available)


if __name__ == '__main__':
    open_with_list(".mp4")
    print("\n\n")
    # app_file_assoc()
