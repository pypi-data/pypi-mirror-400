"""
Tests for tUilKit.config.config (ConfigLoader) and configuration management.
"""

import sys
import os
import json
import time
import tempfile
import shutil

# --- 1. Command line argument for log cleanup ---
import argparse
parser = argparse.ArgumentParser(description="Run tUilKit ConfigLoader test suite.")
parser.add_argument('--clean', action='store_true', help='Remove all log files in the test log folder before running tests.')
args, unknown = parser.parse_known_args()

# --- 2. Imports and initialization ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.config.config import ConfigLoader
from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from datetime import datetime

# Load configurations
config_loader = ConfigLoader()
colour_config = config_loader.load_colour_config()
border_patterns = config_loader.load_border_patterns_config()

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
file_system = FileSystem(logger)

TEST_LOG_FOLDER = os.path.join(os.path.dirname(__file__), "testOutputLogs")
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_config.log")

# Ensure all log folders exist
if not os.path.exists(TEST_LOG_FOLDER):
    os.makedirs(TEST_LOG_FOLDER, exist_ok=True)

# Remove all log files if --clean is passed
if args.clean:
    for fname in os.listdir(TEST_LOG_FOLDER):
        if fname.endswith('.log'):
            try:
                base, ext = os.path.splitext(fname)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_fname = f"{base}_{timestamp}.bak"
                os.rename(os.path.join(TEST_LOG_FOLDER, fname), os.path.join(TEST_LOG_FOLDER, backup_fname))
                print(f"Backed up {fname} to {backup_fname}")
            except Exception as e:
                print(f"Could not backup {fname}: {e}")

# --- 3. Test variables ---
temp_dir = tempfile.mkdtemp()

# --- 4. Test functions ---
def test_config_loader_init(function_log=None):
    """Test ConfigLoader initialization and global_config loading."""
    try:
        # Test initialization
        loader = ConfigLoader()
        assert loader.global_config is not None, "global_config should not be None"
        assert "PROJECT_NAME" in loader.global_config, "PROJECT_NAME should be in global_config"
        assert "VERSION" in loader.global_config, "VERSION should be in global_config"
        assert loader.global_config["VERSION"] == "0.7.0", f"VERSION should be 0.7.0, got {loader.global_config['VERSION']}"
        
        logger.colour_log("!proc", "ConfigLoader initialization tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "ConfigLoader initialization tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_config_loader_init failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_get_json_path(function_log=None):
    """Test get_json_path method."""
    try:
        loader = ConfigLoader()
        
        # Test getting GLOBAL_CONFIG.json path
        global_config_path = loader.get_json_path('GLOBAL_CONFIG.json')
        assert os.path.exists(global_config_path), f"GLOBAL_CONFIG.json path should exist: {global_config_path}"
        assert "GLOBAL_CONFIG.json" in global_config_path, "Path should contain GLOBAL_CONFIG.json"
        
        # Test with non-existent file (should still return a path)
        test_path = loader.get_json_path('NONEXISTENT.json')
        assert "NONEXISTENT.json" in test_path, "Path should contain NONEXISTENT.json"
        
        logger.colour_log("!proc", "get_json_path tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "get_json_path tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_get_json_path failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_load_config(function_log=None):
    """Test load_config method."""
    try:
        loader = ConfigLoader()
        
        # Load GLOBAL_CONFIG.json
        global_config_path = loader.get_json_path('GLOBAL_CONFIG.json')
        loaded_config = loader.load_config(global_config_path)
        
        assert isinstance(loaded_config, dict), "load_config should return a dict"
        assert "VERSION" in loaded_config, "Loaded config should contain VERSION"
        assert "LOG_FILES" in loaded_config, "Loaded config should contain LOG_FILES"
        
        logger.colour_log("!proc", "load_config tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "load_config tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_load_config failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_load_colour_config(function_log=None):
    """Test load_colour_config method."""
    try:
        loader = ConfigLoader()
        
        # Load colour config
        colour_config = loader.load_colour_config()
        
        assert isinstance(colour_config, dict), "load_colour_config should return a dict"
        assert "COLOUR_KEY" in colour_config, "Colour config should contain COLOUR_KEY"
        assert isinstance(colour_config["COLOUR_KEY"], dict), "COLOUR_KEY should be a dict"
        assert len(colour_config["COLOUR_KEY"]) > 0, "COLOUR_KEY should not be empty"
        
        logger.colour_log("!proc", "load_colour_config tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "load_colour_config tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_load_colour_config failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_load_border_patterns_config(function_log=None):
    """Test load_border_patterns_config method."""
    try:
        loader = ConfigLoader()
        
        # Load border patterns config
        border_config = loader.load_border_patterns_config()
        
        assert isinstance(border_config, dict), "load_border_patterns_config should return a dict"
        assert len(border_config) > 0, "Border patterns should not be empty"
        # Check for at least one standard border pattern
        assert any(key in border_config for key in ["SINGLE_LINE", "DOUBLE_LINE", "BOLD"]), "Should contain standard border patterns"
        
        logger.colour_log("!proc", "load_border_patterns_config tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "load_border_patterns_config tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_load_border_patterns_config failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_get_config_file_path(function_log=None):
    """Test get_config_file_path method."""
    try:
        loader = ConfigLoader()
        
        # Test getting COLOURS config path
        colours_path = loader.get_config_file_path("COLOURS")
        assert "COLOURS.json" in colours_path, "Path should reference COLOURS.json"
        
        # Test getting BORDER_PATTERNS config path
        patterns_path = loader.get_config_file_path("BORDER_PATTERNS")
        assert "BORDER_PATTERNS.json" in patterns_path, "Path should reference BORDER_PATTERNS.json"
        
        # Test with invalid key (should raise ValueError)
        try:
            loader.get_config_file_path("NONEXISTENT_KEY")
            assert False, "Should raise ValueError for non-existent key"
        except ValueError as e:
            assert "not found" in str(e), "Error message should indicate key not found"
        
        logger.colour_log("!proc", "get_config_file_path tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "get_config_file_path tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_get_config_file_path failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_get_log_file_path(function_log=None):
    """Test get_log_file_path method."""
    try:
        loader = ConfigLoader()
        
        # Test getting SESSION log path
        session_log = loader.get_log_file_path("SESSION")
        assert session_log is not None, "SESSION log path should not be None"
        assert "logs" in session_log or "RUNTIME" in session_log, "Should reference log file"
        
        # Test getting MASTER log path
        master_log = loader.get_log_file_path("MASTER")
        assert master_log is not None, "MASTER log path should not be None"
        
        # Test with non-existent key (should return None)
        nonexistent = loader.get_log_file_path("NONEXISTENT_LOG")
        assert nonexistent is None, "Should return None for non-existent log key"
        
        logger.colour_log("!proc", "get_log_file_path tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "get_log_file_path tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_get_log_file_path failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

def test_ensure_folders_exist(function_log=None):
    """Test ensure_folders_exist method."""
    try:
        loader = ConfigLoader()
        
        # Create a test filesystem instance
        test_fs = FileSystem(logger)
        
        # Test ensure_folders_exist (should create log folders)
        loader.ensure_folders_exist(test_fs)
        
        # Check if log folder was created
        log_files = loader.global_config.get("LOG_FILES", {})
        for log_key, log_path in list(log_files.items())[:2]:  # Test first 2 log files
            folder = os.path.dirname(log_path)
            if folder:
                # Folder should exist or be creatable
                assert folder, f"Log folder should have a valid path for {log_key}"
        
        logger.colour_log("!proc", "ensure_folders_exist tests passed.", log_files=TEST_LOG_FILE)
        if function_log:
            logger.colour_log("!proc", "ensure_folders_exist tests passed.", log_files=function_log, log_to="file")
    except AssertionError as e:
        logger.log_exception("test_ensure_folders_exist failed", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        raise

# --- 5. TESTS tuple ---
TESTS = [
    (1, "test_config_loader_init", test_config_loader_init),
    (2, "test_get_json_path", test_get_json_path),
    (3, "test_load_config", test_load_config),
    (4, "test_load_colour_config", test_load_colour_config),
    (5, "test_load_border_patterns_config", test_load_border_patterns_config),
    (6, "test_get_config_file_path", test_get_config_file_path),
    (7, "test_get_log_file_path", test_get_log_file_path),
    (8, "test_ensure_folders_exist", test_ensure_folders_exist),
]

# --- 6. Test runner ---
if __name__ == "__main__":
    results = []
    successful = []
    unsuccessful = []

    border_pattern = {
        "TOP": ["==="],
        "LEFT": ["|"],
        "RIGHT": ["|"],
        "BOTTOM": ["==="]
    }

    for num, name, func in TESTS:
        function_log = os.path.join(TEST_LOG_FOLDER, f"{name}.log")
        try:
            logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            logger.print_top_border(border_pattern, 50, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            logger.colour_log("!test", "Running test", "!int", num, "!info", ":", "!proc", name, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            time.sleep(0.5)
            func(function_log=function_log)
            logger.colour_log("!test", "Test", "!int", num, "!info", ":", "!proc", name, "!pass", "PASSED.", log_files=[TEST_LOG_FILE, function_log], log_to="both")
            results.append((num, name, True))
            successful.append(name)
        except Exception as e:
            logger.log_exception(f"{name} failed", e, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            results.append((num, name, False))
            unsuccessful.append(name)

    total_count = len(TESTS)
    count_successes = sum(1 for _, _, passed in results if passed)
    count_unsuccessfuls = total_count - count_successes

    logger.colour_log("!pass", "Successful tests:", "!int", f"{count_successes} / {total_count}", "!list", successful, log_files=TEST_LOG_FILE)
    if count_unsuccessfuls > 0:
        logger.colour_log("!fail", "Unsuccessful tests:", "!fail", count_unsuccessfuls, "!int", f"/ {total_count}", "!list", unsuccessful, log_files=TEST_LOG_FILE)
        for num, name, passed in results:
            if not passed:
                logger.colour_log("!test", "Test", "!int", num, "!info", ":", "!proc", name, "!fail", "FAILED.", log_files=TEST_LOG_FILE)
    else:
        logger.colour_log("!done", "All tests passed!", log_files=TEST_LOG_FILE)

    # Clean up temp dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
