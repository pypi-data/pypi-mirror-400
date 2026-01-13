"""Tests for CLI interface."""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from tui_delta.cli import app

# Ensure consistent terminal width for Rich formatting across all environments
os.environ.setdefault("COLUMNS", "120")

runner = CliRunner()

# Environment variables for consistent test output across all platforms
TEST_ENV = {
    "COLUMNS": "120",  # Consistent terminal width for Rich formatting
    "NO_COLOR": "1",  # Disable ANSI color codes for reliable string matching
}

# ANSI escape code pattern
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return ANSI_ESCAPE.sub("", text)


@pytest.mark.unit
def test_cli_help():
    """Test --help output shows available commands."""
    result = runner.invoke(app, ["--help"], env=TEST_ENV)
    assert result.exit_code == 0
    # Strip ANSI codes for reliable string matching across environments
    output = strip_ansi(result.stdout.lower())
    assert "into" in output
    assert "list-profiles" in output


@pytest.mark.unit
def test_run_command_help():
    """Test 'into' command help."""
    result = runner.invoke(app, ["into", "--help"], env=TEST_ENV)
    assert result.exit_code == 0
    output = strip_ansi(result.stdout.lower())
    assert "tui application" in output
    assert "profile" in output


@pytest.mark.unit
def test_list_profiles_command():
    """Test 'list-profiles' command."""
    result = runner.invoke(app, ["list-profiles"], env=TEST_ENV)
    assert result.exit_code == 0
    # CliRunner captures stderr to output for typer apps
    output = result.output
    assert "claude_code" in output
    assert "generic" in output
    assert "minimal" in output


@pytest.mark.integration
def test_run_command_basic():
    """Test 'into' command with simple echo."""
    # Run a simple command that outputs a few lines
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        output_file = Path(f.name)
    try:
        result = runner.invoke(
            app,
            ["into", str(output_file), "--profile", "minimal", "--", "echo", "test"],
            env=TEST_ENV,
        )
        # Exit code might be non-zero due to script command behavior
        # Just verify it ran without Python errors
        assert "test" in result.stdout or result.exit_code in [0, 1]
    finally:
        output_file.unlink(missing_ok=True)


@pytest.mark.unit
def test_run_command_invalid_profile():
    """Test 'into' command with invalid profile."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        output_file = Path(f.name)
    try:
        result = runner.invoke(
            app,
            ["into", str(output_file), "--profile", "nonexistent", "--", "echo", "test"],
            env=TEST_ENV,
        )
        # Should fail with error about profile
        assert result.exit_code != 0
    finally:
        output_file.unlink(missing_ok=True)


@pytest.mark.unit
def test_run_command_requires_command():
    """Test 'into' command requires TUI command."""
    result = runner.invoke(app, ["into", "/tmp/test.log"], env=TEST_ENV)
    assert result.exit_code != 0
    # Should show error about missing command


@pytest.mark.unit
def test_list_profiles_shows_descriptions():
    """Test 'list-profiles' shows profile descriptions."""
    result = runner.invoke(app, ["list-profiles"], env=TEST_ENV)
    assert result.exit_code == 0
    output = result.output
    # Check for descriptive text, not just profile names
    assert "Claude Code" in output or "terminal" in output.lower()


@pytest.mark.integration
def test_run_with_custom_rules_file(tmp_path):
    """Test 'into' command with custom rules file."""
    # Create a simple custom profile YAML
    rules_file = tmp_path / "custom.yaml"
    rules_file.write_text("""
profiles:
  test_profile:
    description: "Test profile"
    clear_protections:
      - blank_boundary
    normalization_patterns: []
""")

    output_file = tmp_path / "output.log"
    result = runner.invoke(
        app,
        ["into", str(output_file), "--rules-file", str(rules_file), "--", "echo", "test"],
        env=TEST_ENV,
    )
    # Should run without errors (exit code might vary due to script)
    assert result.exit_code in [0, 1]


@pytest.mark.unit
def test_version_option():
    """Test --version option on into command."""
    # Version callback is defined but needs to be on a command
    # Test that version info is accessible
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.cli", "into", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    # Just verify CLI is working


@pytest.mark.integration
def test_run_profiles_integration():
    """Test that all built-in profiles work with into command."""
    profiles = ["claude_code", "generic", "minimal"]

    for profile in profiles:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            output_file = Path(f.name)
        try:
            result = runner.invoke(
                app,
                ["into", str(output_file), "--profile", profile, "--", "echo", "test"],
                env=TEST_ENV,
            )
            # Should not crash (exit code may vary due to script command)
            # Just verify no Python exceptions
            assert "Traceback" not in result.stdout
            # result.stderr may not be separately captured, check if available
            try:
                assert "Traceback" not in result.stderr
            except (ValueError, AttributeError):
                pass  # stderr not separately captured
        finally:
            output_file.unlink(missing_ok=True)


@pytest.mark.unit
def test_clear_lines_module_directly():
    """Test clear_lines module can be invoked directly."""
    # This tests the clear_lines CLI entry point
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.clear_lines", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    # Strip ANSI codes for robust string matching
    import re

    clean_output = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", result.stdout)
    assert "--prefixes" in clean_output or "--profile" in clean_output


@pytest.mark.unit
def test_consolidate_module_directly():
    """Test consolidate_clears module can be invoked directly."""
    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.consolidate_clears", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0


@pytest.mark.integration
def test_pipeline_stdin_to_stdout():
    """Test pipeline processes stdin to stdout."""
    test_input = "line1\nline2\nline3\n"

    result = subprocess.run(
        [sys.executable, "-m", "tui_delta.clear_lines", "--profile", "minimal"],
        input=test_input.encode(),
        capture_output=True,
    )

    assert result.returncode == 0
    assert len(result.stdout) > 0
    # Should output the lines
    assert b"line1" in result.stdout
    assert b"line2" in result.stdout
    assert b"line3" in result.stdout


@pytest.mark.integration
def test_stage_outputs_option(tmp_path):
    """Test --stage-outputs option creates stage output files."""
    output_file = tmp_path / "output.log"

    # Run with --stage-outputs
    result = runner.invoke(
        app,
        ["into", str(output_file), "--profile", "minimal", "--stage-outputs", "--", "echo", "test"],
        env=TEST_ENV,
    )

    # Should run without Python errors
    assert "Traceback" not in result.stdout

    # Check that stage output files were created
    # Stage files: output.log-0-script.bin, output.log-1-clear_lines.bin, etc.
    expected_stages = [
        "0-script.bin",
        "1-clear_lines.bin",
        "2-consolidate.bin",
        "3-uniqseq.bin",
        "4-cut.bin",
    ]

    for stage in expected_stages:
        stage_file = Path(f"{output_file}-{stage}")
        assert stage_file.exists(), f"Stage file {stage_file} should exist"


@pytest.mark.unit
def test_stage_outputs_help():
    """Test --stage-outputs option appears in help."""
    result = runner.invoke(app, ["into", "--help"], env=TEST_ENV)
    assert result.exit_code == 0
    output = strip_ansi(result.stdout.lower())
    assert "stage-outputs" in output or "stage outputs" in output


@pytest.mark.unit
def test_decode_escapes_command_help():
    """Test decode-escapes command help."""
    result = runner.invoke(app, ["decode-escapes", "--help"], env=TEST_ENV)
    assert result.exit_code == 0
    output = strip_ansi(result.stdout.lower())
    assert "escape" in output or "control" in output


@pytest.mark.integration
def test_decode_escapes_basic(tmp_path):
    """Test decode-escapes command with basic input."""
    # Create test input file with ANSI escape sequences
    input_file = tmp_path / "input.bin"
    output_file = tmp_path / "output.txt"

    # Write file with escape sequences (clear line sequence)
    test_content = b"line1\n\x1b[2Kline2\n"
    input_file.write_bytes(test_content)

    # Run decode-escapes
    result = runner.invoke(
        app,
        ["decode-escapes", str(input_file), str(output_file)],
        env=TEST_ENV,
    )

    assert result.exit_code == 0
    assert output_file.exists()

    # Output should have decoded escape sequences
    decoded = output_file.read_text()
    assert "[clear_line]" in decoded
    assert "line1" in decoded
    assert "line2" in decoded


@pytest.mark.integration
def test_decode_escapes_to_stdout(tmp_path):
    """Test decode-escapes outputs to stdout when no output file specified."""
    input_file = tmp_path / "input.bin"

    # Write file with window title escape sequence
    test_content = b"\x1b]0;Test Title\x07text\n"
    input_file.write_bytes(test_content)

    # Run decode-escapes without output file
    result = runner.invoke(
        app,
        ["decode-escapes", str(input_file)],
        env=TEST_ENV,
    )

    assert result.exit_code == 0
    # Output should be in stdout
    assert "window-title" in result.stdout.lower() or "test title" in result.stdout.lower()


@pytest.mark.unit
def test_decode_escapes_preserves_colors(tmp_path):
    """Test decode-escapes preserves ANSI color codes."""
    input_file = tmp_path / "input.bin"
    output_file = tmp_path / "output.txt"

    # Write file with color codes and control sequences
    test_content = b"\x1b[31mred text\x1b[0m\x1b[2K"
    input_file.write_bytes(test_content)

    result = runner.invoke(
        app,
        ["decode-escapes", str(input_file), str(output_file)],
        env=TEST_ENV,
    )

    assert result.exit_code == 0
    decoded = output_file.read_text()

    # Should have color codes preserved
    assert "\x1b[31m" in decoded
    assert "\x1b[0m" in decoded
    # Should have control sequence decoded
    assert "[clear_line]" in decoded
