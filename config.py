import json
import os
from pathlib import Path


class Configuration:
    env_fields = ["AzureWebJobsStorage", "storageAccountName", "DIGITAL_TWIN_URL"]

    def __init__(self):
        self.data = {}
        self.load_from_env()
        self.load_from_file(Path("config.json"))

    def load_from_env(self):
        for field in self.env_fields:
            self.data[field] = os.environ.get(field)

    def load_from_file(self, path: Path):
        with open(path, "r") as file:
            self.data = {**self.data, **json.load(file)}

    def __getitem__(self, key):
        if key not in self.data.keys():
            raise KeyError
        return self.data[key]


configuration = Configuration()
