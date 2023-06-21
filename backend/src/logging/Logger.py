import logging
from src.configuration.ConfigurationManager import ConfigurationManager
import enum
import os


class Logger:
    __instance = None

    @staticmethod
    def get_instance():
        if Logger.__instance is None:
            Logger.__instance = Logger()
        return Logger.__instance

    def _reset_log_file(self):
        filename = os.path.basename(self.log_file)
        folder = os.path.dirname(self.log_file)
        if not filename in os.listdir(folder):
            return
        with open(self.log_file, 'w') as file:
            pass
            #file.truncate()
        

    def __init__(self):
        self.configuration = ConfigurationManager.get_instance()
        self.loggin_level = self.configuration.get_component_value('log_level')
        self.log_file = self.configuration.get_component_value('log_file')
        self._reset_log_file()

        logging.basicConfig(
            level=self.loggin_level,
            format='%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.logger = logging.getLogger('BDXT_logger')
        
        # Configurar el manejador de archivo
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.loggin_level)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        
        # Agregar ambos manejadores al logger
        self.logger.addHandler(file_handler)

    def set_log_level(self, level: str):
        if level == 'INFO':
            self.loggin_level = logging.INFO
        elif level == 'DEBUG':
            self.loggin_level = logging.DEBUG
        elif level == 'ERROR':
            self.loggin_level = logging.ERROR
        else:
            self.loggin_level = logging.INFO

        self.logger.setLevel(self.loggin_level)

    
    def info(self, msg : str):
        self.logger.info(msg)
    
    def warn(self, msg : str):
        self.logger.warn(msg)

    def error(self, msg : str):
        self.logger.error(msg)