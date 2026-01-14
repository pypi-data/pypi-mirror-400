"""
Tests for tUilKit interfaces: ConfigLoader, ColourManager, Logger, FileSystem.
"""

import sys
import os
import json
import time
import argparse

# --- 1. Command line argument for log cleanup ---
parser = argparse.ArgumentParser(description="Run tUilKit interfaces test suite.")
parser.add_argument('--clean', action='store_true', help='Remove all log files in the test log folder before running tests.')
args, unknown = parser.parse_known_args()

# --- 2. Imports and initialization ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.config.config import ConfigLoader
import os
import json
import time
import argparse
from datetime import datetime

COLOUR_CONFIG_PATH = os.path.join(base_dir, "tUilKit", "config", "COLOURS.json")
BORDER_PATTERN_PATH = os.path.join(base_dir, "tUilKit", "config", "BORDER_PATTERNS.json")

with open(COLOUR_CONFIG_PATH, "r") as f:
    colour_config = json.load(f)

with open(BORDER_PATTERN_PATH, "r") as f:
    border_patterns = json.load(f)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
config_loader = ConfigLoader()
file_system = FileSystem(logger)

TEST_LOG_FOLDER = os.path.join(os.path.dirname(__file__), "testOutputLogs")
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_interfaces_output.log")

# Ensure all log folders exist
all_log_paths = list(logger.log_files.values()) + [TEST_LOG_FILE]
for path in all_log_paths:
    folder = os.path.dirname(path)
    if folder:
        file_system.validate_and_create_folder(folder, category="fs")

if not os.path.exists(TEST_LOG_FOLDER):
    os.makedirs(TEST_LOG_FOLDER, exist_ok=True)

# Remove all log files if --clean is passed
if args.clean:
    for fname in os.listdir(TEST_LOG_FOLDER):
        if fname.endswith('.log'):
            try:
                # Create backup before removing
                base, ext = os.path.splitext(fname)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_fname = f"{base}_{timestamp}.bak"
                os.rename(os.path.join(TEST_LOG_FOLDER, fname), os.path.join(TEST_LOG_FOLDER, backup_fname))
                print(f"Backed up {fname} to {backup_fname}")
            except Exception as e:
                print(f"Could not backup {fname}: {e}")

# --- 3. Test functions ---

def test_config_loader(function_log=None):
    # Test locating and logging the path of the global config file
    global_config_path = config_loader.get_json_path('GLOBAL_CONFIG.json')
    log_files = [f for f in [TEST_LOG_FILE, function_log] if f]
    logger.colour_log("!file", colour_manager.colour_path(global_config_path), "!info", "Global config file path.", log_files=log_files)

    # Log paths of log files
    log_files = config_loader.global_config.get("LOG_FILES", {})
    for key, path in log_files.items():
        logger.colour_log("!file", f"{key}:", colour_manager.colour_path(path), log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Read and log description
    description = config_loader.global_config.get("PROJECT_DESCRIPTION", "No description")
    logger.colour_log("!text", f"Project Description: {description}", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Ensure folders exist
    config_loader.ensure_folders_exist(file_system)

    logger.colour_log("!proc", "ConfigLoader tests passed.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_colour_manager(function_log=None):
    # Test colour functions
    red_code = colour_manager.get_fg_colour("RED")
    assert red_code == "\033[38;2;255;0;0m", f"Expected red ANSI code, got {red_code}"

    coloured = colour_manager.colour_fstr("RED", "Hello", "BLUE", "World")
    assert "Hello" in coloured and "World" in coloured, "colour_fstr should include text"

    interpreted = colour_manager.interpret_codes("This is {RED}red{RESET} text.")
    assert "{RED}" not in interpreted, "interpret_codes should replace {RED}"
    assert "\033[38;2;255;0;0m" in interpreted, "Should include ANSI code"

    logger.colour_log("!proc", "ColourManager tests passed.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_logger(function_log=None):
    # Test colour_log
    logger.colour_log("!info", "Testing Logger interface.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test colour_log_text
    logger.colour_log_text("Interpreted {GREEN}green{RESET} text.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test log_exception (simulate)
    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.log_exception("Test exception logging", e, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!proc", "Logger tests passed.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_file_system(function_log=None):
    # Test creating log files by ensuring folders and logging
    log_files = config_loader.global_config.get("LOG_FILES", {})
    for path in log_files.values():
        folder = os.path.dirname(path)
        if folder:
            file_system.validate_and_create_folder(folder)
            assert os.path.exists(folder), f"Folder {folder} should exist"

    # Log to the actual log files
    logger.colour_log("!file", "Logging to configured log files.", log_files=list(log_files.values()))

    logger.colour_log("!proc", "FileSystem tests passed.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_apply_border(function_log=None):
    pattern = border_patterns.get("DOUBLE_LINE", {
        "TOP": ["═"],
        "LEFT": ["║"],
        "RIGHT": ["║"], 
        "BOTTOM": ["═"]
    })

    logger.apply_border("test", pattern, 30, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    logger.print_bottom_border(pattern, 30, log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!proc", "Apply border tests passed.", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
TESTS = [
    (1, "test_config_loader", test_config_loader),
    (2, "test_colour_manager", test_colour_manager),
    (3, "test_logger", test_logger),
    (4, "test_file_system", test_file_system),
    (5, "test_apply_border", test_apply_border),
]

# --- 5. Test runner ---
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
            logger.apply_border(f"Running test {num}: {name}", border_pattern, 40, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            time.sleep(1)
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