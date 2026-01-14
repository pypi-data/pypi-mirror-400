# Lib/site-packages/tUilKit/config/config.py
"""
   Load JSON configuration of GLOBAL variables.
"""
import os
import json
from tUilKit.interfaces.config_loader_interface import ConfigLoaderInterface
from tUilKit.interfaces.file_system_interface import FileSystemInterface
 
class ConfigLoader(ConfigLoaderInterface):
    def __init__(self):
        self.global_config = self.load_config(self.get_json_path('GLOBAL_CONFIG.json'))

    def get_json_path(self, file: str, cwd: bool = False) -> str:
        if cwd:
            local_path = os.path.join(os.getcwd(), file)
            if os.path.exists(local_path):
                return local_path
        return os.path.join(os.path.dirname(__file__), file)

    def load_config(self, json_file_path: str) -> dict:
        with open(json_file_path, 'r') as f:
            return json.load(f)

    def ensure_folders_exist(self, file_system: FileSystemInterface):
        log_files = self.global_config.get("LOG_FILES", {})
        for log_path in log_files.values():
            folder = os.path.dirname(log_path)
            if folder:
                file_system.validate_and_create_folder(folder, category="fs")

    def get_config_file_path(self, config_key: str) -> str:
        """
        Get the path to a config file from the CONFIG_FILES section of global config.
        Paths in CONFIG_FILES are relative to the project root.
        """
        config_files = self.global_config.get("CONFIG_FILES", {})
        relative_path = config_files.get(config_key)
        if relative_path:
            # The relative_path is relative to the project root
            return os.path.join(os.getcwd(), relative_path)
        else:
            raise ValueError(f"Config file key '{config_key}' not found in CONFIG_FILES")

    def get_log_file_path(self, log_key: str) -> str:
        """
        Get the path to a log file from the LOG_FILES section of global config.
        """
        log_files = self.global_config.get("LOG_FILES", {})
        return log_files.get(log_key)

    def load_colour_config(self) -> dict:
        """
        Load the colour configuration from the COLOURS config file.
        """
        colour_config_path = self.get_config_file_path("COLOURS")
        return self.load_config(colour_config_path)

    def load_border_patterns_config(self) -> dict:
        """
        Load the border patterns configuration from the BORDER_PATTERNS config file.
        """
        border_patterns_path = self.get_config_file_path("BORDER_PATTERNS")
        return self.load_config(border_patterns_path)

# Create a global instance
config_loader = ConfigLoader()
global_config = config_loader.global_config



