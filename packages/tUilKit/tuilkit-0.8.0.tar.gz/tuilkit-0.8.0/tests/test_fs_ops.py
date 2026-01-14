# Lib/site-packages/tUilKit/tests/test_fs_ops.py
"""
Tests for tUilKit.utils.fs (FileSystem) operations.
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
parser = argparse.ArgumentParser(description="Run tUilKit fs ops test suite.")
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
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_fs_ops_output.log")

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
def test_validate_and_create_folder(function_log=None):
    logger.colour_log("!info", "Starting test_validate_and_create_folder", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    test_folder = os.path.join(temp_dir, "test_validate_folder")
    logger.colour_log("!file", f"Test folder path: {test_folder}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Test creating new folder
    logger.colour_log("!try", "Attempting to create new folder", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    result = file_system.validate_and_create_folder(test_folder)
    assert result == True, "Should return True for successful creation"
    assert os.path.exists(test_folder), "Folder should exist after creation"
    logger.colour_log("!pass", "Folder created successfully", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Test creating existing folder
    logger.colour_log("!try", "Attempting to create existing folder", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    result = file_system.validate_and_create_folder(test_folder)
    assert result == True, "Should return True for existing folder"
    logger.colour_log("!pass", "Existing folder handled correctly", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_validate_and_create_folder completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_remove_empty_folders(function_log=None):
    logger.colour_log("!info", "Starting test_remove_empty_folders", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    base_folder = os.path.join(temp_dir, "test_remove_empty")
    empty_sub = os.path.join(base_folder, "empty_sub")
    non_empty_sub = os.path.join(base_folder, "non_empty_sub")
    
    # Create structure
    file_system.validate_and_create_folder(base_folder)
    file_system.validate_and_create_folder(empty_sub)
    file_system.validate_and_create_folder(non_empty_sub)
    with open(os.path.join(non_empty_sub, "file.txt"), 'w') as f:
        f.write("test")
    
    logger.colour_log("!file", f"Created test structure in {base_folder}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Remove empty folders
    logger.colour_log("!try", "Removing empty folders", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    file_system.remove_empty_folders(base_folder)
    
    assert not os.path.exists(empty_sub), "Empty subfolder should be removed"
    assert os.path.exists(non_empty_sub), "Non-empty subfolder should remain"
    logger.colour_log("!pass", "Empty folders removed, non-empty preserved", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_remove_empty_folders completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_no_overwrite(function_log=None):
    logger.colour_log("!info", "Starting test_no_overwrite", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    test_file = os.path.join(temp_dir, "test_no_overwrite.txt")
    
    # Create initial file
    with open(test_file, 'w') as f:
        f.write("original")
    logger.colour_log("!file", f"Created initial file: {test_file}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Test no overwrite
    logger.colour_log("!try", "Testing no-overwrite with existing file", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    new_path = file_system.no_overwrite(test_file)
    assert new_path != test_file, "Should generate new path"
    logger.colour_log("!file", f"Generated non-overwrite path: {new_path}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Test with non-existing file
    non_exist = os.path.join(temp_dir, "non_exist.txt")
    logger.colour_log("!try", "Testing no-overwrite with non-existing file", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    new_path2 = file_system.no_overwrite(non_exist)
    assert new_path2 == non_exist, "Should return same path for non-existing"
    logger.colour_log("!file", f"Non-existing file path unchanged: {new_path2}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_no_overwrite completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_backup_and_replace(function_log=None):
    logger.colour_log("!info", "Starting test_backup_and_replace", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    test_file = os.path.join(temp_dir, "test_backup.txt")
    
    # Create initial file
    with open(test_file, 'w') as f:
        f.write("original content")
    logger.colour_log("!file", f"Created initial file: {test_file}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Backup and replace
    logger.colour_log("!try", "Backing up and replacing file", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    backup_file = os.path.join(temp_dir, "backup_test_backup.txt")
    file_system.backup_and_replace(test_file, backup_file)
    
    assert os.path.exists(backup_file), "Backup should exist"
    with open(backup_file, 'r') as f:
        assert f.read() == "original content", "Backup should have original content"
    with open(test_file, 'r') as f:
        assert f.read() == "", "Original should be empty"
    logger.colour_log("!pass", "Backup and replace worked correctly", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_backup_and_replace completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_sanitize_filename(function_log=None):
    logger.colour_log("!info", "Starting test_sanitize_filename", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    test_cases = [
        ("normal.txt", "normal.txt"),
        ("file:with:colons.txt", "file-with-colons.txt"),
        ("file\\with\\backslashes.txt", "filewithbackslashes.txt"),
        ("file?with?questions.txt", "filewithquestions.txt"),
        ("file*with*stars.txt", "filewithstars.txt"),
        ("file<with<angles.txt", "filewithangles.txt"),
        ("file>with>angles.txt", "filewithangles.txt"),
        ("file|with|pipes.txt", "filewithpipes.txt"),
    ]
    
    for input_name, expected in test_cases:
        logger.colour_log("!try", f"Sanitizing: {input_name}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        result = file_system.sanitize_filename(input_name)
        assert result == expected, f"Expected {expected}, got {result}"
        logger.colour_log("!pass", f"Result: {result}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_sanitize_filename completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_get_all_files(function_log=None):
    logger.colour_log("!info", "Starting test_get_all_files", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    test_folder = os.path.join(temp_dir, "test_get_files")
    file_system.validate_and_create_folder(test_folder)
    
    # Create files
    files = ["file1.txt", "file2.txt", "subdir"]
    for f in files[:2]:
        with open(os.path.join(test_folder, f), 'w') as file:
            file.write("test")
    os.makedirs(os.path.join(test_folder, files[2]))
    
    logger.colour_log("!file", f"Created test files in {test_folder}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    result = file_system.get_all_files(test_folder)
    expected = ["file1.txt", "file2.txt"]
    assert set(result) == set(expected), f"Expected {expected}, got {result}"
    logger.colour_log("!pass", f"Retrieved files: {result}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_get_all_files completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_validate_extension(function_log=None):
    logger.colour_log("!info", "Starting test_validate_extension", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    test_cases = [
        ("file.txt", ".txt", "file.txt"),
        ("file", ".txt", "file.txt"),
        ("file.jpg", ".txt", "file.jpg.txt"),
    ]
    
    for input_path, ext, expected in test_cases:
        logger.colour_log("!try", f"Validating extension for {input_path} with {ext}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        result = file_system.validate_extension(input_path, ext)
        assert result == expected, f"Expected {expected}, got {result}"
        logger.colour_log("!pass", f"Result: {result}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_validate_extension completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

def test_get_log_files_internal(function_log=None):
    logger.colour_log("!info", "Starting test_get_log_files_internal", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    # Test different categories
    categories = ["default", "error", "fs", "init"]
    for cat in categories:
        logger.colour_log("!try", f"Testing _get_log_files for category: {cat}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
        result = file_system._get_log_files(cat)
        assert isinstance(result, list), "Should return list"
        logger.colour_log("!pass", f"Log files for {cat}: {result}", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])
    
    logger.colour_log("!done", "test_get_log_files_internal completed", category="fs", log_files=[TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE])

# --- 5. TESTS tuple ---
TESTS = [
    (1, "test_validate_and_create_folder", test_validate_and_create_folder),
    (2, "test_remove_empty_folders", test_remove_empty_folders),
    (3, "test_no_overwrite", test_no_overwrite),
    (4, "test_backup_and_replace", test_backup_and_replace),
    (5, "test_sanitize_filename", test_sanitize_filename),
    (6, "test_get_all_files", test_get_all_files),
    (7, "test_validate_extension", test_validate_extension),
    (8, "test_get_log_files_internal", test_get_log_files_internal),
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