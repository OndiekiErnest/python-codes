__author__ = "Ondieki"
__email__ = "ondieki.codes@gmail.com"

import json
from common import logging, _join


config_logger = logging.getLogger(__name__)
config_logger.debug(f"Initializing {__name__}")


_CONFIG_FILE = _join("config.json")


class Settings():
    choices = {
        "username": "",
        "password": "",
        "download_dir": "",
        "disks": {},
    }

    def update_n_save(self, username, password, download_dir):
        """ update setting fields and save """
        self.choices["username"] = username
        self.choices["password"] = password
        self.choices["download_dir"] = download_dir
        self.save()

    def save(self, filename=_CONFIG_FILE):
        config_logger.info("Saving settings for later use")
        with open(filename, 'w') as file:
            file.write(json.dumps(self.choices))

    def load(self, filename=_CONFIG_FILE):
        data = {}
        try:
            with open(filename) as file:
                data = json.loads(file.read())
        except Exception as e:
            config_logger.error(f"{e}")
            pass
        if data.keys() == self.choices.keys():
            config_logger.info("Saved settings loaded successfully")
            self.choices = data
            return True
        return False

    def remember_disk(self, disk_name, t_from, t_to, operation, recurse, remember):
        config_logger.info(f"Saving disk ({disk_name}) settings for automation")

        new_disk = {"source_folder": t_from,
                    "dest_folder": t_to, "copy": operation,
                    "recurse": recurse, "save": remember,
                    }

        self.choices["disks"][disk_name] = new_disk
        self.save()
