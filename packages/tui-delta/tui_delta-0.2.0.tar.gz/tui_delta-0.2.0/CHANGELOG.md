# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes yet.

---

## [0.2.0] - 2026-01-04

### ⚠️ Breaking Changes

#### CLI Changes

- **Command renamed:** `tui-delta run` → `tui-delta into`
- **Output handling:** Output file is now a required positional argument instead of using stdout redirection
  - **Before (0.1.x):** `tui-delta run -- command > output.log`
  - **After (0.2.0):** `tui-delta into output.log -- command`
- **Argument naming:** Command argument renamed from `command` to `command-line` for clarity

#### Python API Changes

- **`run_tui_with_pipeline()` signature changed:**
  - Parameter renamed: `command` → `command_line`
  - New required parameter: `output_file: Path`
  - New optional parameter: `stage_outputs: bool = False`
  - **Before (0.1.x):** `run_tui_with_pipeline(command=['claude', 'code'])`
  - **After (0.2.0):** `run_tui_with_pipeline(command_line=['claude', 'code'], output_file=Path('session.log'))`

- **`build_script_command()` signature changed:**
  - Parameter renamed: `command` → `command_line`
  - New required parameter: `output_file: str`

### Features

- **Named pipe support:** Output file can now be a user-created named pipe (FIFO) for post-processing with other tools
- **Stage outputs:** New `--stage-outputs` option saves intermediate pipeline stage outputs for debugging
- **Escape decoder:** New `tui-delta decode-escapes` command to decode control sequences to readable text
- **Profile validation:** Validates profile names and provides helpful error messages with available profiles
- **Improved buffering:** Added `-u` flag to Python processes for better real-time output

### Migration Guide

**CLI Users:**

Update your scripts to use the new command syntax:
```bash
# Old (0.1.x)
tui-delta run --profile claude_code -- claude code > session.log

# New (0.2.0)
tui-delta into session.log --profile claude_code -- claude code
```

**Python API Users:**

Update function calls to include the output file:
```python
# Old (0.1.x)
from tui_delta import run_tui_with_pipeline
run_tui_with_pipeline(command=['claude', 'code'], profile='claude_code')

# New (0.2.0)
from pathlib import Path
from tui_delta import run_tui_with_pipeline
run_tui_with_pipeline(
    command_line=['claude', 'code'],
    output_file=Path('session.log'),
    profile='claude_code'
)
```

---

## [0.1.1] - 2025-12-11

Updated description.

## [0.1.0] - 2025-12-11

Initial release.

### Features
- TUI application capture and delta processing
- Profile-based processing with built-in profile for Claude Code
- Clear detection and consolidation for terminal output
- Real-time streaming output
- Deduplication of repeated content blocks via uniqseq
- Multi-line pattern recognition via patterndb-yaml
- Command-line interface with typer and rich
- Comprehensive test suite with property-based testing
- Documentation site with MkDocs Material
- GitHub Actions CI/CD pipeline
- PyPI and Homebrew distribution support

---

## Release Process

Releases are automated via GitHub Actions when a version tag is pushed:

1. Update CHANGELOG.md with release notes
2. Create and push Git tag: `git tag v0.1.0 && git push origin v0.1.0`
3. GitHub Actions automatically:
   - Creates GitHub Release
   - Publishes to PyPI (when configured)
4. Version number is automatically derived from Git tag

[Unreleased]: https://github.com/JeffreyUrban/tui-delta/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/JeffreyUrban/tui-delta/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/JeffreyUrban/tui-delta/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/JeffreyUrban/tui-delta/releases/tag/v0.1.0
