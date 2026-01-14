
# CHANGELOG

## [0.8.0] - 2026-01-06

### Added
- **Path Helper Functions**: New `normalize_path()`, `colourize_path()`, and `detect_os()` functions in FileSystem for cross-platform path handling and colored path display in logs.
- **Multi-Color Border Gradients**: Border rendering now supports separate gradient options for borders and text with `border_fg_gradient`, `border_bg_gradient`, `border_rainbow`, `text_fg_gradient`, `text_bg_gradient`, and `text_rainbow` parameters.
- **Multiline Border Support**: New `apply_border_multiline()` method wraps multiple text lines in borders with full gradient support.
- **Background Color Support**: Full background color rendering with `BG_` prefix (e.g., `BG_BLUE`, `BG_RED`) now works correctly in terminal output.
- **Border Pattern List Format**: BORDER_PATTERNS.json now supports lists for TOP/LEFT/RIGHT/BOTTOM patterns enabling multi-character borders.
- **Comprehensive Border Tests**: Added 18 test cases in test_output.py covering all gradient combinations, justification options, and multiline rendering.

### Changed
- **Background Color Initialization**: ColourManager constructor now correctly uses color values for backgrounds when raw color names (BLUE, RED, etc.) have no `|` separator, instead of defaulting to BLACK. Config keys like `!info` still get BLACK backgrounds as intended.
- **Consistent Timestamp Coloring**: `log_message()` now applies colored timestamps using `!date` and `!time` config keys with proper ANSI resets, ensuring all timestamps render consistently.
- **FileSystem Logging Integration**: All FileSystem methods (validate_and_create_folder, remove_empty_folders, no_overwrite, backup_and_replace) now use `colourize_path()` for colored path display in logs.

### Fixed
- **Background Colors Not Displaying**: Resolved issue where background colors generated correct ANSI codes but weren't rendering due to ANSI_BG_COLOUR_SET storing BLACK for all raw color names.
- **Inconsistent Timestamp Colors**: Fixed timestamps appearing with and without colors by ensuring `log_message()` consistently applies color codes via `colour_fstr()`.

### Technical Details
- RGB dictionary values include 'm' terminator (e.g., '255;0;0m').
- ANSI codes: Foreground `\033[38;2;R;G;Bm`, Background `\033[48;2;R;G;Bm`, Reset FG `39m`, Reset BG `49m`.
- Border methods support all three justification options: left, center, right.

## [0.7.1] - 2026-01-01

### Changed
- Bumped version metadata to 0.7.1 across packaging files and GLOBAL_CONFIG.
- Realigned README to factory-first initialization, corrected direct FileSystem example, and updated folder/test listings with new docs.

### Added
- Linked new ColourKey and FileSystem usage addenda from README and comprehensive guide.

## [0.7.0] - 2025-12-31

### Added
- **Factory functions** for simplified component initialization: `get_logger()`, `get_config_loader()`, `get_colour_manager()`, and `get_file_system()`.
- **Module-level singleton pattern**: Factory functions maintain internal singleton instances, ensuring components are created once and reused throughout the application lifecycle.
- **reset_factories() utility**: For testing purposes, allows complete reset of all singleton instances.
- **factories.py module**: New `src/tUilKit/factories.py` with comprehensive factory implementations and docstrings.
- **Top-level exports**: Updated `src/tUilKit/__init__.py` to export all factory functions for convenient top-level imports.

### Changed
- **README quick-start guide**: Now features factory functions as the recommended approach with direct initialization as an advanced alternative.
- **Version unified**: Synchronized `setup.py` and `pyproject.toml` versions to 0.7.0.

### Benefits
- **Zero-boilerplate initialization**: Single import and function call replaces manual config loading, colour manager creation, and logger instantiation.
- **Automatic dependency injection**: Factory functions handle all internal wiring transparently.
- **Backwards compatible**: Direct initialization still fully supported for advanced use cases.

### Example
```python
from tUilKit import get_logger

logger = get_logger()
logger.colour_log("!info", "App started")
```

## [0.6.1] - 2025-12-30

### Added
- **Multi-category logging support**: Enhanced `_get_log_files()` methods in `Logger` and `FileSystem` classes to accept both string and list categories, enabling simultaneous logging to multiple log files (e.g., `category=["fs", "error"]`).
- **DataFrame logging integration**: Added optional `logger` parameter to `load_column_mapping()` and `smart_merge()` functions in `sheets.py` with category-based logging for info and error messages.
- **Comprehensive usage documentation**: Created `docs/tUilKit_Comprehensive_Usage_Guide.md` with complete initialization instructions, interface breakdowns, and advanced feature examples.
- **Multi-category logging tests**: New `test_multi_category.py` with comprehensive tests for single-category, multi-category, filesystem integration, backwards compatibility, and log file deduplication.
- **Documentation folder**: Added `/docs` directory to project structure for comprehensive guides.

### Changed
- Updated `README.md` with new folder structure including `/docs` and updated test files.
- Clarified "4 Primary Interfaces" section in README to distinguish core interfaces (Logger, Colour, FileSystem, ConfigLoader) from additional DataFrameInterface.
- Enhanced `SmartDataFrameHandler.merge()` to pass logger parameter through to underlying functions.
- Improved backwards compatibility for single string categories while adding list support.

### Fixed
- Ensured log file deduplication when multiple categories map to the same log files.
- Maintained existing API compatibility for all logging methods.

### Notes
- Multi-category logging allows complex operations to be logged to multiple relevant log files simultaneously (e.g., filesystem errors logged to both `FS` and `ERROR` logs).
- All existing code continues to work unchanged; new multi-category features are opt-in.
- New comprehensive documentation provides complete usage examples for all interfaces and features.

## [0.5.2] - 2025-12-28

### Added
- New test file `test_interfaces.py` for comprehensive testing of ConfigLoader, ColourManager, Logger, and FileSystem interfaces.

### Changed
- Updated `ConfigLoader.ensure_folders_exist` to create folders based on `LOG_FILES` paths instead of non-existent `MAKE_FOLDERS`.
- Removed broken code in `config.py` that referenced invalid config keys.

### Fixed
- ConfigLoader now properly handles folder creation for log files.

## [0.5.1] - 2025-12-27

### Added
- New colour key system with `!` prefixed keys (e.g., `!date`, `!time`, `!proc`) for improved readability and consistency.
- Support for foreground and background color combinations in `COLOUR_KEY` using `FG|BG` format (e.g., `GREEN|BLACK`).
- `interpret_codes` method in `ColourManager` to interpret colour codes in text strings using `{colour}` syntax.
- Support for multiple log files in all logging methods by changing `log_file` parameter to `log_files` (list of strings).
- Updated interfaces (`ColourInterface`, `FileSystemInterface`, `LoggerInterface`) to reflect new method signatures.

### Changed
- Updated `COLOUR_KEY` in `COLOURS.json` with new keys and marked old keys as deprecated for migration.
- Modified `ColourManager` to parse `FG|BG` colour values and set both foreground and background ANSI codes.
- Changed logging methods to accept `log_files` as a list, allowing simultaneous logging to multiple files.
- Updated test files to use new colour keys and multiple log file support.
- Enhanced `colour_path` to use new `!` prefixed keys for path components.

### Fixed
- Improved colour reset handling to reset both foreground and background colours.

### Notes
- Old colour keys (e.g., `ARGS`, `COMMAND`) are deprecated; migrate to new `!` prefixed keys (e.g., `!args`, `!cmd`).
- Logging methods now expect `log_files` as a list; single file can be passed as `[file_path]`.
- Ensure `COLOURS.json` is updated to use the new format for full background colour support.

## [0.4.2] - 2025-11-29

### Added
- Agent-enabled code edits: enable controlled AI agent-assisted code edits across the `Projects/tUilKit` workspace (non-binary files only). Updates are intended to be applied with review and version control.

## [0.4.1] - 2025-06-04

### Added
- `smart_diff` function to intelligently compare dataframes, ignoring row order and detecting unexpected changes via hashing.
- `find_common_columns` function to identify matching fields based on **strict column name matching** (now separated from fuzzy matching).
- `find_fuzzy_columns` function to identify similar columns based on data patterns using fuzzy matching.
- `find_composite_keys` function to determine potential multi-part key fields when no obvious single keys exist.
- `smart_merge` function with support for manual merging (`left`, `right`, `inner`, `outer`) via command-line arguments.
- JSON-based column header mapping using `tUilKit/config/COLUMN_MAPPING.json`, leveraging the existing `ConfigLoader` interface.
- JSON-based column width mapping to dynamically adjust dataframe column widths based on predefined configurations.
- `DataFrameInterface` abstract class in `tUilKit/interfaces/df_interface.py` to standardize merging and comparison operations.
- `SmartDataFrameHandler` implementation of `DataFrameInterface` to perform intelligent merging and comparisons.
- `apply_column_format` function in `formatter.py` to format dataframe columns according to known width configurations.
- **Unified test framework**: All test modules now accept a `--clean` argument for log cleanup, use consistent logging (including rainbow rows and borders), track successful/unsuccessful tests, and log exceptions in a standardized way. This framework is ready to be reused across other projects for consistent testing and reporting.

### Changed
- Improved merging logic in `smart_merge` to ensure all column mappings are applied before concatenation.
- Enhanced hashing logic in `smart_diff` to ensure row comparisons remain unaffected by column order.
- Updated `find_common_columns` to use strict column name matching; fuzzy logic is now in `find_fuzzy_columns`.
- Standardized interface methods across `df_interface.py` for easier extensibility.
- Adjusted logging configuration to support dataframe operations and new test framework.

### Fixed
- Resolved inconsistencies in dataframe merging where unknown columns disrupted the alignment.
- Fixed errors in row comparison by ensuring hashing is column-order independent.
- Addressed data formatting bugs in `apply_column_format` by properly adjusting padding rules.

### Notes
- Ensure `COLUMN_MAPPING.json` includes mappings for known data header transformations.
- Confirm `COLUMN_WIDTHS.json` is configured to handle automatic column resizing.
- All dataframe utilities are now fully integrated with `ConfigLoader` for dynamic configuration management.
- The new test framework is now the standard for all future and existing tUilKit projects.

This release significantly enhances dataframe handling capabilities and introduces a robust, reusable test framework for consistent testing and reporting across all projects. 🚀

## [0.3.1] - 2025-05-08

### Added
- `colour_path` method to `ColourManager` and `ColourInterface` for multi-colour path formatting using COLOUR_KEYs (`DRIVE`, `BASEFOLDER`, `MIDFOLDER`, `THISFOLDER`, `FILE`).
- Optional `log_to` parameter to all logging and printing functions, allowing output to terminal, file, both, or queue.
- Optional `function_log` parameter to all test functions in `test_output.py` for duplicate log file testing.
- Optional `time_stamp` parameter to logging functions for toggling timestamp display.

### Changed
- Shifted timestamp logic from `colour_log` to `log_message` in `Logger`. Now, `colour_log` passes `time_stamp=False` to `log_message` and prepends a coloured timestamp using `colour_fstr`.
- Updated `Logger` and `FileSystem` to consistently use the new `log_to` parameter.
- Updated test suite to use `logger.Colour_Mgr.colour_path(...)` for coloured path output in logs.
- Updated `colour_interface.py` to include `colour_fstr` and `colour_path` as abstract methods.
- Improved test cleanup and logging in `test_output.py` to use coloured paths and new logging features.

### Fixed
- Ensured all logging and printing functions in `Logger` accept and respect the `log_to` parameter.
- Fixed AttributeError in tests by referencing `colour_path` via `logger.Colour_Mgr.colour_path`.
- Removed redundant `time.sleep` calls from test functions, now handled in the test loop.

### Notes
- Ensure your `COLOUR_KEY` in `COLOURS.json` includes keys for `DATE`, `TIME`, `DRIVE`, `BASEFOLDER`, `MIDFOLDER`, `THISFOLDER`, and `FILE` for full colour path and timestamp support.
- All log output destinations and timestamp formatting are now fully configurable at the call site.

