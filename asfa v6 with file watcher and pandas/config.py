import json

CONFIG_FILE = "data\\config.json"


class Settings():
    configDict = {
        "username": "",
        "port": 3000,
        "speed_limit": 2,
        "shared_dir": "",
        "download_dir": "",
    }

    def update(self, username, port, speed_limit, shared_dir, download_dir):
        self.configDict["username"] = username
        self.configDict["port"] = port
        self.configDict["speed_limit"] = speed_limit
        self.configDict["shared_dir"] = shared_dir
        self.configDict["download_dir"] = download_dir
        self.save()

    def save(self, filename=CONFIG_FILE):
        with open(filename, 'w') as file:
            file.write(json.dumps(self.configDict))

    def load(self, filename=CONFIG_FILE):
        data = {}
        try:
            with open(filename) as file:
                data = json.loads(file.read())
        except Exception:
            pass
        if data.keys() == self.configDict.keys():
            self.configDict = data
            return True
        return False
