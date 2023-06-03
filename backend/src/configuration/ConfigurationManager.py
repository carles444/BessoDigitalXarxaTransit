import json, sys, os

CONFIG_PATH = 'config.json'

class ConfigurationManager:
    __instance = None
    
    @staticmethod
    def get_instance():
        if ConfigurationManager.__instance is None:
            ConfigurationManager.__instance = ConfigurationManager()
        return ConfigurationManager.__instance
    
    def __init__(self, configuration_file_path : str = None) -> None:
        if ConfigurationManager.__instance is not None:
            raise Exception("This class is a singleton, use get_instance() method to get the instance.")
        else:
            ConfigurationManager.__instance = self
            
        if configuration_file_path is None:
            configuration_file_path = CONFIG_PATH
        try:
            config_file = open(configuration_file_path, 'r')
            self.config_file = json.load(config_file)
            config_file.close()
        except:
            sys.exit(f"Configuration file could not be opened")
    
    def get_component_value(self, key : str) -> any:
        if key in self.config_file:
            return self.config_file[key]
        else:
            return None

