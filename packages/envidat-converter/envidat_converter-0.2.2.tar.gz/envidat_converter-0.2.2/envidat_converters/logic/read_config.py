"""
Class to read the config.ini file
"""

import configparser


class Config:
    def __init__(self, environment="prod"):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.environment = environment
        if self.environment not in self.config.sections():
            print(f"{environment} is not defined")

    def get(self, key):
        try:
            return self.config.get(self.environment, key)
        except Exception as e:
            if self.environment == "prod":
                return "https://envidat.ch/"
            else:
                raise KeyError(f"Key '{key}' not found in environment '{self.environment}'")
