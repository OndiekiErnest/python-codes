import json
from common import logging


config_logger = logging.getLogger(__name__)

config_logger.debug(f"Initializing {__name__}")


CONFIG_FILE = "data\\config.json"


class Settings():
    choices = {
        "username": "",
        "password": "",
        "download_dir": "",
        "disk": "",
        "source_folder": "",
        "dest_folder": "",
        "copy": "",
        "recurse": "",
        "save": "",
    }

    def update_n_save(self, username, password, download_dir):
        """ update setting fields and save """
        self.choices["username"] = username
        self.choices["password"] = password
        self.choices["download_dir"] = download_dir
        self.save()

    def save(self, filename=CONFIG_FILE):
        print("SAVING >>>")
        with open(filename, 'w') as file:
            file.write(json.dumps(self.choices))

    def load(self, filename=CONFIG_FILE):
        data = {}
        try:
            with open(filename) as file:
                data = json.loads(file.read())
        except Exception:
            pass
        if data.keys() == self.choices.keys():
            self.choices = data
            return True
        return False

    def remember_disk(self, disk_name, t_from, t_to, operation, recurse, remember):
        print(">>> Remember called")
        disk_options = {"disk": disk_name, "source_folder": t_from,
                        "dest_folder": t_to, "copy": operation,
                        "recurse": recurse, "save": remember,
                        }
        self.choices.update(disk_options)
        self.save()
