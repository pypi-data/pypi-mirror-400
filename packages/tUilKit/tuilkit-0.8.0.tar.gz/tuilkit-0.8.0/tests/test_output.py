"""
Tests for tUilKit.utils.output (Logger, ColourManager) and tUilKit.utils.fs (FileSystem) functions.
"""

import sys
import os
import json
import time
import tempfile
import shutil
from datetime import datetime

# --- 1. Command line argument for log cleanup ---
import argparse
parser = argparse.ArgumentParser(description="Run tUilKit output/fs test suite.")
parser.add_argument('--clean', action='store_true', help='Remove all log files in the test log folder before running tests.')
args, unknown = parser.parse_known_args()

# --- 2. Imports and initialization ---
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from tUilKit.utils.output import Logger, ColourManager
from tUilKit.utils.fs import FileSystem
from tUilKit.config.config import ConfigLoader

# Change to project root before initializing ConfigLoader so paths resolve correctly
original_cwd = os.getcwd()
os.chdir(project_root)

COLOUR_CONFIG_PATH = os.path.join(base_dir, "tUilKit", "config", "COLOURS.json")

# Use ConfigLoader to load colour config
config_loader = ConfigLoader()
colour_config = config_loader.load_colour_config()
border_patterns_config = config_loader.load_border_patterns_config()

# Restore original working directory
os.chdir(original_cwd)

colour_manager = ColourManager(colour_config)
logger = Logger(colour_manager)
file_system = FileSystem(logger)

TEST_LOG_FOLDER = os.path.join(os.path.dirname(__file__), "testOutputLogs")
TEST_LOG_FILE = os.path.join(TEST_LOG_FOLDER, "test_output_output.log")

# Ensure all log folders exist
all_log_paths = list(logger.log_files.values()) + [TEST_LOG_FILE]
for path in all_log_paths:
    folder = os.path.dirname(path)
    if folder:
        file_system.validate_and_create_folder(folder, category="fs")
default_log_files = config_loader.global_config.get("LOG_FILES", {})
# add test log files to default_log_files

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

# --- 3. Test variables ---
temp_dir = tempfile.mkdtemp()

# --- 4. Test functions ---
def test_colour_manager(function_log=None):
    # Test get_fg_colour
    red_code = colour_manager.get_fg_colour("RED")
    assert red_code == "\033[38;2;255;0;0m", f"Expected red ANSI code, got {red_code}"
    
    # Test colour_fstr
    coloured = colour_manager.colour_fstr("RED", "Hello", "BLUE", "World")
    assert "Hello" in coloured and "World" in coloured, "colour_fstr should include text"
    
    # Test interpret_codes
    interpreted = colour_manager.interpret_codes("This is {RED}red{RESET} text.")
    assert "{RED}" not in interpreted, "interpret_codes should replace {RED}"
    assert "\033[38;2;255;0;0m" in interpreted, "Should include ANSI code"
    
    logger.colour_log("!proc", "ColourManager tests passed.", log_files=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("!proc", "ColourManager tests passed.", log_files=function_log, log_to="file")

def test_logger_basic(function_log=None):
    # Test colour_log
    logger.colour_log("!info", "Basic logger test.", log_files=TEST_LOG_FILE)
    
    # Test colour_log_text
    logger.colour_log_text("Interpreted {GREEN}green{RESET} text.", log_files=TEST_LOG_FILE)
    
    # Test multiple files
    if function_log:
        logger.colour_log("!file", colour_manager.colour_path(TEST_LOG_FILE), colour_manager.colour_path(function_log),"!info", "Logging to multiple files.", log_files=[TEST_LOG_FILE, function_log])
    else:
        logger.colour_log("!file", colour_manager.colour_path(TEST_LOG_FILE), "!info", "Logging to primary test log file.", log_files=TEST_LOG_FILE)
    
    logger.colour_log("!file", colour_manager.colour_path(TEST_LOG_FILE), "!proc", "Logger basic tests passed.", log_files=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("!file", colour_manager.colour_path(function_log), "!proc", "Logger basic tests passed.", log_files=function_log)

def test_file_system(function_log=None):
    test_folder = os.path.join(temp_dir, "test_folder")
    
    # Test validate_and_create_folder
    file_system.validate_and_create_folder(test_folder)
    assert os.path.exists(test_folder), "Folder should be created"
    
    # Test with subfolder
    subfolder = os.path.join(test_folder, "sub")
    file_system.validate_and_create_folder(subfolder)
    assert os.path.exists(subfolder), "Subfolder should be created"
    
    # Clean up
    shutil.rmtree(test_folder)
    
    logger.colour_log("!proc", "FileSystem tests passed.", log_files=TEST_LOG_FILE)
    if function_log:
        logger.colour_log("!proc", "FileSystem tests passed.", log_files=function_log, log_to="file")

"""
test_apply_border function to test the ConfigLoader loading the border patterns from the BORDER_PATTERNS.json file 
whose location is specified in the GLOBAL_CONFIG.json file.
and test the apply_border application in logger and log results to function_log and all log_files.
Tests multiple color options: single color, foreground gradient, background gradient, rainbow, separate border/text gradients, and multiline borders.
"""
def test_apply_border(function_log=None):
    # Use BORDER_PATTERNS from config file
    pattern = border_patterns_config.get("BORDER_PATTERNS", {
        "TOP": ["<>"],
        "LEFT": ["|>"],
        "RIGHT": ["<|"], 
        "BOTTOM": ["<>"]
    })
    
    log_targets = [TEST_LOG_FILE, function_log] if function_log else [TEST_LOG_FILE]
    
    # Test 1: Single color border (default)
    logger.colour_log("!info", "Test 1: Single color border", log_files=log_targets)
    logger.apply_border("Default Single Color", pattern, 50, index=0, border_colour='!proc', text_colour='!info', log_files=log_targets)
    
    # Test 1b: Direct background color tests
    logger.colour_log("!info", "Test 1b: Direct BG color tests", log_files=log_targets)
    logger.colour_log("BG_BLUE", "Blue background", log_files=log_targets)
    logger.colour_log("BG_RED", "Red background", log_files=log_targets)
    logger.colour_log("BG_GREEN", "Green background", log_files=log_targets)
    logger.colour_log("YELLOW", "BG_MAGENTA", "Yellow text on magenta background", log_files=log_targets)
    
    # Test 1c: colour_fstr direct test
    logger.colour_log("!info", "Test 1c: colour_fstr BG test", log_files=log_targets)
    test_msg = colour_manager.colour_fstr("BG_CYAN", "Cyan BG test")
    logger.log_message(test_msg, log_files=log_targets, time_stamp=True, log_to="both")
    test_msg2 = colour_manager.colour_fstr("RED", "BG_YELLOW", "Red text", "on yellow BG")
    logger.log_message(test_msg2, log_files=log_targets, time_stamp=True, log_to="both")
    
    # Test 1d: Debug raw ANSI codes
    logger.colour_log("!info", "Test 1d: Raw ANSI debug", log_files=log_targets)
    from tUilKit.dict.DICT_COLOURS import RGB
    print(f"RGB['BLUE'] = {RGB['BLUE']}")
    print(f"ANSI_BG_COLOUR_SET['BLUE'] = {repr(colour_manager.ANSI_BG_COLOUR_SET['BLUE'])}")
    bg_result = colour_manager.get_bg_colour('BLUE')
    print(f"get_bg_colour('BLUE') = {repr(bg_result)}")
    debug_msg = colour_manager.colour_fstr("BG_BLUE", "Background test")
    print(f"Raw ANSI output: {repr(debug_msg)}")
    logger.log_message(debug_msg, log_files=log_targets, time_stamp=True, log_to="both")
    
    # Test 2: Border foreground gradient only
    logger.colour_log("!info", "Test 2: Border FG gradient", log_files=log_targets)
    logger.apply_border("Border FG Gradient", pattern, 50, index=1, 
                       border_fg_gradient=['RED', 'ORANGE', 'YELLOW', 'GREEN', 'CYAN', 'BLUE'], 
                       text_colour='!proc', log_files=log_targets)
    
    # Test 3: Border background gradient
    logger.colour_log("!info", "Test 3: Border BG gradient", log_files=log_targets)
    logger.apply_border("Border BG Gradient", pattern, 50, index=0,
                       border_bg_gradient=['BLUE', 'CYAN', 'GREEN'],
                       text_colour='!info', log_files=log_targets)
    
    # Test 4: Border rainbow
    logger.colour_log("!info", "Test 4: Border rainbow", log_files=log_targets)
    logger.apply_border("Border Rainbow", pattern, 50, index=1, border_rainbow=True, text_colour='!done', log_files=log_targets)
    
    # Test 5: Text foreground gradient (border solid)
    logger.colour_log("!info", "Test 5: Text FG gradient", log_files=log_targets)
    logger.apply_border("Text FG Gradient", pattern, 50, index=0, 
                       border_colour='!proc', 
                       text_fg_gradient=['MAGENTA', 'VIOLET', 'BLUE'], 
                       log_files=log_targets)
    
    # Test 6: Text background gradient (border solid)
    logger.colour_log("!info", "Test 6: Text BG gradient", log_files=log_targets)
    logger.apply_border("Text BG Gradient", pattern, 50, index=1,
                       border_colour='!info',
                       text_bg_gradient=['GOLD', 'ORANGE', 'CRIMSON'],
                       log_files=log_targets)
    
    # Test 7: Text rainbow (border solid)
    logger.colour_log("!info", "Test 7: Text rainbow", log_files=log_targets)
    logger.apply_border("Text Rainbow!", pattern, 50, index=0,
                       border_colour='!pass',
                       text_rainbow=True,
                       log_files=log_targets)
    
    # Test 8: Both border and text with FG gradients
    logger.colour_log("!info", "Test 8: Border + Text FG gradients", log_files=log_targets)
    logger.apply_border("Dual FG Gradients", pattern, 55, index=1,
                       border_fg_gradient=['RED', 'CRIMSON', 'MAGENTA'],
                       text_fg_gradient=['CYAN', 'BLUE', 'INDIGO'],
                       log_files=log_targets)
    
    # Test 9: Border rainbow + text gradient
    logger.colour_log("!info", "Test 9: Border rainbow + Text gradient", log_files=log_targets)
    logger.apply_border("Rainbow + Gradient Combo", pattern, 60, index=0,
                       border_rainbow=True,
                       text_fg_gradient=['GOLD', 'YELLOW', 'CHARTREUSE'],
                       log_files=log_targets)
    
    # Test 10: Both border and text rainbow
    logger.colour_log("!info", "Test 10: Full rainbow (border + text)", log_files=log_targets)
    logger.apply_border("Double Rainbow!!", pattern, 50, index=1,
                       border_rainbow=True,
                       text_rainbow=True,
                       log_files=log_targets)
    
    # Test 11: Text justification - left
    logger.colour_log("!info", "Test 11: Justify left", log_files=log_targets)
    logger.apply_border("Left Aligned", pattern, 60, index=0, 
                       border_fg_gradient=['GREEN', 'CHARTREUSE'], 
                       text_colour='!info', justify='left', log_files=log_targets)
    
    # Test 12: Text justification - center
    logger.colour_log("!info", "Test 12: Justify center", log_files=log_targets)
    logger.apply_border("Center Aligned", pattern, 60, index=1, 
                       border_rainbow=True, 
                       text_colour='!done', justify='center', log_files=log_targets)
    
    # Test 13: Text justification - right
    logger.colour_log("!info", "Test 13: Justify right", log_files=log_targets)
    logger.apply_border("Right Aligned", pattern, 60, index=0, 
                       border_fg_gradient=['RED', 'YELLOW', 'GREEN'], 
                       text_colour='!pass', justify='right', log_files=log_targets)
    
    # Test 14: Multiline border - simple
    logger.colour_log("!info", "Test 14: Multiline border (simple)", log_files=log_targets)
    logger.apply_border_multiline(
        ["First line", "Second line", "Third line"],
        pattern, 50, index=0,
        border_colour='!proc',
        text_colour='!info',
        log_files=log_targets
    )
    
    # Test 15: Multiline border with border gradient
    logger.colour_log("!info", "Test 15: Multiline with border gradient", log_files=log_targets)
    logger.apply_border_multiline(
        ["Gradient Border", "Multiple Lines", "Cool Effect"],
        pattern, 55, index=1,
        border_fg_gradient=['BLUE', 'CYAN', 'GREEN', 'YELLOW', 'ORANGE', 'RED'],
        text_colour='!proc',
        justify='center',
        log_files=log_targets
    )
    
    # Test 16: Multiline border with text rainbow
    logger.colour_log("!info", "Test 16: Multiline with text rainbow", log_files=log_targets)
    logger.apply_border_multiline(
        ["Rainbow Text!", "Line Two", "Line Three", "Even More Lines"],
        pattern, 60, index=0,
        border_colour='!pass',
        text_rainbow=True,
        justify='left',
        log_files=log_targets
    )
    
    # Test 17: Multiline with both border and text rainbows
    logger.colour_log("!info", "Test 17: Multiline full rainbow", log_files=log_targets)
    logger.apply_border_multiline(
        ["Everything Rainbow", "So Much Color", "Maximum Vibes"],
        pattern, 65, index=1,
        border_rainbow=True,
        text_rainbow=True,
        justify='center',
        log_files=log_targets
    )
    
    # Test 18: Complex multiline with different justifications
    logger.colour_log("!info", "Test 18: Multiline justified right", log_files=log_targets)
    logger.apply_border_multiline(
        ["Right aligned", "Multiple", "Lines"],
        pattern, 50, index=0,
        border_fg_gradient=['MAGENTA', 'VIOLET'],
        text_fg_gradient=['GOLD', 'ORANGE'],
        justify='right',
        log_files=log_targets
    )

    logger.colour_log("!proc", "Apply border tests passed.", log_files=log_targets)


# --- 5. TESTS tuple ---
TESTS = [
    (1, "test_colour_manager", test_colour_manager),
    (2, "test_logger_basic", test_logger_basic),
    (3, "test_file_system", test_file_system),
    (4, "test_apply_border", test_apply_border)
]

# --- 6. Test runner ---
if __name__ == "__main__":
    results = []
    successful = []
    unsuccessful = []

    # Use BORDER_PATTERNS from config (using index 1 for second pattern)
    border_pattern = border_patterns_config.get("BORDER_PATTERNS", {
        "TOP": ["=="],
        "LEFT": ["| "],
        "RIGHT": [" |"],
        "BOTTOM": ["=="]
    })

    for num, name, func in TESTS:
        function_log = os.path.join(TEST_LOG_FOLDER, f"{name}.log")
        try:
            logger.print_rainbow_row(pattern="X-O-", spacer=2, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            logger.print_top_border(border_pattern, 40, log_files=[TEST_LOG_FILE, function_log], log_to="both")
            logger.colour_log("!test", "Running test", "!int", num, "!info", ":", "!proc", name, log_files=[TEST_LOG_FILE, function_log], log_to="both")
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