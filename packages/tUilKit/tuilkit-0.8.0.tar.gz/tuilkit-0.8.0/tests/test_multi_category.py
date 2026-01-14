# Lib/site-packages/tUilKit/tests/test_multi_category.py
"""
Tests for multi-category logging functionality.
Extremely verbose logging following the new selective logging standard.
"""

import sys
import os
import json
import time
import tempfile
import shutil
import argparse
from datetime import datetime

# --- 1. Command line argument for log cleanup ---
parser = argparse.ArgumentParser(description="Run tUilKit multi-category logging test suite.")
parser.add_argument('--clean', action='store_true', help='Backup all log files in the test log folder before running tests.')
args, unknown = parser.parse_known_args()

# --- 2. Imports and initialization ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.config.config import ConfigLoader

COLOUR_CONFIG_PATH = os.path.join(base_dir, "tUilKit", "config", "COLOURS.json")
BORDER_PATTERN_PATH = os.path.join(base_dir, "tUilKit", "config", "BORDER_PATTERNS.json")

with open(BORDER_PATTERN_PATH, "r") as f:
    border_patterns = json.load(f)

with open(COLOUR_CONFIG_PATH, "r") as f:
    colour_config = json.load(f)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
config_loader = ConfigLoader()
file_system = FileSystem(logger)

TEST_LOG_FOLDER = os.path.join(os.path.dirname(__file__), "testOutputLogs")
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_multi_category_output.log")

if not os.path.exists(TEST_LOG_FOLDER):
    os.makedirs(TEST_LOG_FOLDER, exist_ok=True)

# Backup all log files if --clean is passed
if args.clean:
    for fname in os.listdir(TEST_LOG_FOLDER):
        if fname.endswith('.log'):
            try:
                # Create backup
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
def test_single_category_logging(function_log=None):
    logger.colour_log("!info", "Starting test_single_category_logging", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Create temporary log files
    log_files = {
        "SESSION": os.path.join(temp_dir, "session_single.log"),
        "MASTER": os.path.join(temp_dir, "master_single.log"),
        "ERROR": os.path.join(temp_dir, "error_single.log"),
        "FS": os.path.join(temp_dir, "fs_single.log"),
        "INIT": os.path.join(temp_dir, "init_single.log")
    }

    # Initialize logger with test log files
    test_logger = Logger(colour_manager, log_files=log_files)
    logger.colour_log("!file", f"Created test logger with log files: {list(log_files.keys())}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test single category logging for each category
    categories = ["default", "error", "fs", "init"]
    for cat in categories:
        logger.colour_log("!try", f"Testing single category logging for: {cat}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        test_logger.colour_log("!info", f"Single category test message for {cat}", category=cat)
        logger.colour_log("!pass", f"Logged to category: {cat}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Verify logs were written to correct files
    for cat in categories:
        log_path = log_files.get(cat.upper(), log_files.get("SESSION"))
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                content = f.read()
                assert f"Single category test message for {cat}" in content, f"Message not found in {cat} log"
                logger.colour_log("!pass", f"Verified log entry in {cat} file", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        else:
            logger.colour_log("!fail", f"Log file not found: {log_path}", category="error", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!done", "test_single_category_logging completed", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_multi_category_logging_basic(function_log=None):
    logger.colour_log("!info", "Starting test_multi_category_logging_basic", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Create temporary log files
    log_files = {
        "SESSION": os.path.join(temp_dir, "session_multi.log"),
        "MASTER": os.path.join(temp_dir, "master_multi.log"),
        "ERROR": os.path.join(temp_dir, "error_multi.log"),
        "FS": os.path.join(temp_dir, "fs_multi.log"),
        "INIT": os.path.join(temp_dir, "init_multi.log")
    }

    # Initialize logger with test log files
    test_logger = Logger(colour_manager, log_files=log_files)
    logger.colour_log("!file", f"Created test logger with log files: {list(log_files.keys())}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test multi-category logging
    test_cases = [
        (["fs", "error"], "Multi-category: fs and error"),
        (["default", "init"], "Multi-category: default and init"),
        (["fs", "error", "init"], "Multi-category: fs, error, and init"),
    ]

    for categories, message in test_cases:
        logger.colour_log("!try", f"Testing multi-category logging for: {categories}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        test_logger.colour_log("!info", message, category=categories)
        logger.colour_log("!pass", f"Logged to categories: {categories}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

        # Verify message appears in all relevant log files
        for cat in categories:
            log_path = log_files.get(cat.upper(), log_files.get("SESSION"))
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    content = f.read()
                    assert message in content, f"Message not found in {cat} log"
                    logger.colour_log("!pass", f"Verified message in {cat} log file", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
            else:
                logger.colour_log("!fail", f"Log file not found: {log_path}", category="error", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!done", "test_multi_category_logging_basic completed", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_multi_category_with_filesystem(function_log=None):
    logger.colour_log("!info", "Starting test_multi_category_with_filesystem", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Create temporary log files
    log_files = {
        "SESSION": os.path.join(temp_dir, "session_fs.log"),
        "MASTER": os.path.join(temp_dir, "master_fs.log"),
        "ERROR": os.path.join(temp_dir, "error_fs.log"),
        "FS": os.path.join(temp_dir, "fs_fs.log"),
        "INIT": os.path.join(temp_dir, "init_fs.log")
    }

    # Initialize logger and filesystem
    test_logger = Logger(colour_manager, log_files=log_files)
    test_fs = FileSystem(test_logger, log_files)
    logger.colour_log("!file", f"Created test filesystem with log files: {list(log_files.keys())}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test filesystem operations with multi-category logging
    test_folder = os.path.join(temp_dir, "test_multi_fs")
    logger.colour_log("!try", f"Creating folder with multi-category logging: {test_folder}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # This should log to both FS and ERROR categories
    result = test_fs.validate_and_create_folder(test_folder, category=["fs", "error"])
    assert result == True, "Folder creation should succeed"
    assert os.path.exists(test_folder), "Folder should exist"
    logger.colour_log("!pass", "Folder created successfully with multi-category logging", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Verify logging in both categories
    fs_content = ""
    error_content = ""

    if os.path.exists(log_files["FS"]):
        with open(log_files["FS"], 'r') as f:
            fs_content = f.read()

    if os.path.exists(log_files["ERROR"]):
        with open(log_files["ERROR"], 'r') as f:
            error_content = f.read()

    # Check that folder creation message appears in both logs
    assert "Attempting to create folder" in fs_content, "FS log should contain folder creation message"
    assert "Attempting to create folder" in error_content, "ERROR log should contain folder creation message"
    logger.colour_log("!pass", "Verified multi-category logging in filesystem operations", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!done", "test_multi_category_with_filesystem completed", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_backwards_compatibility(function_log=None):
    logger.colour_log("!info", "Starting test_backwards_compatibility", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Create temporary log files
    log_files = {
        "SESSION": os.path.join(temp_dir, "session_compat.log"),
        "MASTER": os.path.join(temp_dir, "master_compat.log"),
        "ERROR": os.path.join(temp_dir, "error_compat.log"),
        "FS": os.path.join(temp_dir, "fs_compat.log"),
        "INIT": os.path.join(temp_dir, "init_compat.log")
    }

    # Initialize logger with test log files
    test_logger = Logger(colour_manager, log_files=log_files)
    logger.colour_log("!file", f"Created test logger for backwards compatibility: {list(log_files.keys())}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test that old single string categories still work
    old_style_calls = [
        ("default", "Old style default logging"),
        ("error", "Old style error logging"),
        ("fs", "Old style fs logging"),
    ]

    for category, message in old_style_calls:
        logger.colour_log("!try", f"Testing backwards compatibility for category: {category}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        test_logger.colour_log("!info", message, category=category)
        logger.colour_log("!pass", f"Backwards compatible logging for: {category}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

        # Verify message appears in correct log file
        log_path = log_files.get(category.upper(), log_files.get("SESSION"))
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                content = f.read()
                assert message in content, f"Message not found in {category} log"
                logger.colour_log("!pass", f"Verified backwards compatibility for {category}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        else:
            logger.colour_log("!fail", f"Log file not found: {log_path}", category="error", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!done", "test_backwards_compatibility completed", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_log_file_deduplication(function_log=None):
    logger.colour_log("!info", "Starting test_log_file_deduplication", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Create temporary log files
    log_files = {
        "SESSION": os.path.join(temp_dir, "session_dedup.log"),
        "MASTER": os.path.join(temp_dir, "master_dedup.log"),
        "ERROR": os.path.join(temp_dir, "error_dedup.log"),
        "FS": os.path.join(temp_dir, "fs_dedup.log"),
        "INIT": os.path.join(temp_dir, "init_dedup.log")
    }

    # Initialize logger with test log files
    test_logger = Logger(colour_manager, log_files=log_files)
    logger.colour_log("!file", f"Created test logger for deduplication: {list(log_files.keys())}", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Test that overlapping categories don't create duplicate log entries
    # If ERROR and FS both map to SESSION, we should only log once
    logger.colour_log("!try", "Testing log file deduplication with overlapping categories", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    test_logger.colour_log("!info", "Deduplication test message", category=["default", "error"])  # Both might map to SESSION
    logger.colour_log("!pass", "Logged with potentially overlapping categories", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    # Count occurrences of the message in SESSION log
    session_path = log_files["SESSION"]
    if os.path.exists(session_path):
        with open(session_path, 'r') as f:
            content = f.read()
            count = content.count("Deduplication test message")
            assert count == 1, f"Message should appear exactly once, but found {count} times"
            logger.colour_log("!pass", f"Verified deduplication: message appears {count} time(s)", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    else:
        logger.colour_log("!fail", f"Session log file not found: {session_path}", category="error", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

    logger.colour_log("!done", "test_log_file_deduplication completed", category="default", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

# --- 5. TESTS tuple ---
TESTS = [
    (1, "test_single_category_logging", test_single_category_logging),
    (2, "test_multi_category_logging_basic", test_multi_category_logging_basic),
    (3, "test_multi_category_with_filesystem", test_multi_category_with_filesystem),
    (4, "test_backwards_compatibility", test_backwards_compatibility),
    (5, "test_log_file_deduplication", test_log_file_deduplication),
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
            logger.apply_border(f"Running test {num}: {name}", border_pattern, 50, log_files=[TEST_LOG_FILE, function_log], log_to="both")
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

    # Clean up temp dir
    shutil.rmtree(temp_dir)