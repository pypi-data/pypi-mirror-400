# src/tUilKit/factories.py
"""
Factory functions for creating and initializing tUilKit components.
Encapsulates setup logic and provides convenient one-liner instantiation.
"""

from tUilKit.config.config import ConfigLoader
from tUilKit.utils.output import ColourManager, Logger
from tUilKit.utils.fs import FileSystem

# Singleton instances
_config_loader = None
_colour_manager = None
_logger = None
_file_system = None


def get_config_loader():
    """
    Get or create the singleton ConfigLoader instance.
    Loads GLOBAL_CONFIG.json and provides access to all configuration.
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def get_colour_manager():
    """
    Get or create the singleton ColourManager instance.
    Initializes colour mappings from the loaded colour configuration.
    """
    global _colour_manager
    if _colour_manager is None:
        config_loader = get_config_loader()
        colour_config = config_loader.load_colour_config()
        _colour_manager = ColourManager(colour_config)
    return _colour_manager


def get_logger():
    """
    Get or create the singleton Logger instance.
    Fully initialized with ColourManager and log file paths from config.
    """
    global _logger
    if _logger is None:
        colour_manager = get_colour_manager()
        config_loader = get_config_loader()
        log_files = config_loader.global_config.get("LOG_FILES", {})
        _logger = Logger(colour_manager, log_files=log_files)
    return _logger

def get_file_system():
    """
    Get or create the singleton FileSystem instance.
    """
    global _file_system
    if _file_system is None:
        _file_system = FileSystem()
    return _file_system

def reset_factories():
    """
    Reset all singleton instances. Useful for testing.
    """
    global _config_loader, _colour_manager, _logger, _file_system
    _config_loader = None
    _colour_manager = None
    _logger = None
    _file_system = None
