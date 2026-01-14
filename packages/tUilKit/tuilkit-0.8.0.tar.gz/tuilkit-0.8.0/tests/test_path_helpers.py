import os
import sys
from pathlib import Path

# Ensure src on path
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tUilKit.utils.fs import normalize_path, detect_os, colourize_path
from tUilKit.utils.output import ColourManager
from tUilKit.config.config import ConfigLoader


def _colour_manager():
    cfg_loader = ConfigLoader()
    colours_path = SRC_DIR / "tUilKit" / "config" / "COLOURS.json"
    colour_cfg = cfg_loader.load_config(str(colours_path))
    return ColourManager(colour_cfg)


def test_normalize_path_posix():
    raw = r"C:\\Temp\\foo\\bar.txt"
    norm = normalize_path(raw, style="posix")
    assert norm == "C:/Temp/foo/bar.txt"


def test_normalize_path_windows():
    raw = r"C:/Temp/foo/bar.txt"
    norm = normalize_path(raw, style="windows")
    assert norm == "C:\\Temp\\foo\\bar.txt"


def test_colourize_path_auto_strips_to_original():
    cm = _colour_manager()
    raw = os.path.join("tmp", "folder", "file.txt")
    coloured = colourize_path(raw, cm, style="auto")
    stripped = cm.strip_ansi(coloured)
    # colour_path preserves separators for current platform
    assert stripped == raw


def test_detect_os_returns_known_value():
    assert detect_os() in {"Windows", "Linux", "Darwin"}
