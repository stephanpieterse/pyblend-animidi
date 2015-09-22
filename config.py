__author__ = "Stephan Pieterse"

import yaml


class configParser:
    configFile = "config.yml"

    def __init__(self, configFile = "config.yml"):
        self.configFile = configFile

    def getConfig(self, configNeeded):
        f = open(self.configFile, 'r')
        cfg = yaml.safe_load(f)

        configFound = False

        for section in cfg:
            if section == configNeeded:
                configFound = cfg[section]

        return configFound
