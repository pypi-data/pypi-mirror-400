#!/usr/bin/env python3
"""
Run a TUI application with real-time delta processing.

Wraps a TUI application using `script` to capture all terminal output
(including escape sequences), then processes through the pipeline:
  clear_lines → consolidate → uniqseq → cut → uniqseq

The TUI displays normally to the user while processed deltas stream to stdout.

The command-line can be any executable with arguments and options, such as:
  claude
  npm test
  python script.py --verbose
"""

import os
import platform
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def build_script_command(
    command_line: list[str],
    output_file: str,
    system: Optional[str] = None,
) -> list[str]:
    """
    Build platform-specific script command.

    Args:
        command_line: The command-line to run (e.g., ['claude'], ['npm', 'test'])
        output_file: Path where script writes its output (can be a FIFO)
        system: Platform identifier ('Darwin' or 'Linux'). Auto-detected if None.

    Returns:
        Complete script command as list
    """
    if system is None:
        system = platform.system()

    if system == "Darwin":  # macOS
        # macOS syntax: script -q -F file command args...
        return ["script", "-q", "-F", output_file] + command_line
    else:  # Linux and others
        # Linux syntax: script --flush --quiet --return --command "cmd" file
        # --return: return exit code of child process
        # --command: command-line to execute
        cmdline_str = shlex.join(command_line)
        return [
            "script",
            "--flush",
            "--quiet",
            "--return",
            "--command",
            cmdline_str,
            output_file,
        ]


def build_pipeline_commands(
    profile: Optional[str] = None,
    rules_file: Optional[Path] = None,
) -> list[list[str]]:
    """
    Build the processing pipeline command list.

    Standard pipeline: clear_lines → consolidate → uniqseq → cut
    Optional: additional_pipeline command from profile

    Args:
        profile: Clear rules profile (claude_code, generic, etc.)
        rules_file: Custom rules YAML file

    Returns:
        List of command lists for the pipeline
    """
    from .clear_rules import ClearRules

    pipeline: list[list[str]] = []

    # Step 1: clear_lines --prefixes
    clear_cmd = [sys.executable, "-u", "-m", "tui_delta.clear_lines", "--prefixes"]
    if profile:
        clear_cmd.extend(["--profile", profile])
    if rules_file:
        clear_cmd.extend(["--rules-file", str(rules_file)])
    pipeline.append(clear_cmd)

    # Step 2: consolidate_clears
    consolidate_cmd = [sys.executable, "-u", "-m", "tui_delta.consolidate_clears"]
    pipeline.append(consolidate_cmd)

    # Step 3: uniqseq --track '^\+: ' --quiet
    uniqseq1_cmd = [
        sys.executable,
        "-u",
        "-m",
        "uniqseq",
        "--track",
        r"^\+: ",
        "--quiet",
    ]
    pipeline.append(uniqseq1_cmd)

    # Step 4: cut -b 4- (strip prefix)
    # Using Python one-liner to strip first 4 characters
    # Use end='' to avoid adding extra newlines (stdin lines already have them)
    # Use -u for unbuffered output to prevent buffering in the pipeline
    cut_cmd = [
        sys.executable,
        "-u",
        "-c",
        "import sys; [print(line[3:], end='') for line in sys.stdin]",
    ]
    pipeline.append(cut_cmd)

    # Step 5 (optional): additional_pipeline from profile
    try:
        profile_config = ClearRules.get_profile_config(profile, rules_file)
        additional_pipeline = profile_config.get("additional_pipeline")
        if additional_pipeline:
            # Parse shell command into list for subprocess
            # Shell will handle the command string, so pass it as-is
            pipeline.append(["sh", "-c", additional_pipeline])
    except (FileNotFoundError, ValueError):
        # If profile not found or file missing, continue without additional pipeline
        pass

    return pipeline


def run_tui_with_pipeline(
    command_line: list[str],
    output_file: Path,
    profile: Optional[str] = None,
    rules_file: Optional[Path] = None,
    stage_outputs: bool = False,
) -> int:
    """
    Run a TUI application with real-time delta processing.

    Creates a named pipe, runs script writing to it, and processes the output
    through the pipeline. The TUI displays normally while processed output
    streams to the output file.

    Args:
        command_line: The command-line to run (e.g., ['claude'], ['npm', 'test'])
        output_file: File to write processed deltas (can be a named pipe)
        profile: Clear rules profile
        rules_file: Custom rules YAML file
        stage_outputs: If True, save output from each stage to output_file-N-stage.bin

    Returns:
        Exit code from the TUI application
    """
    # Create a temporary named pipe (FIFO)
    with tempfile.TemporaryDirectory() as tmpdir:
        fifo_path = os.path.join(tmpdir, "tui-delta.fifo")
        os.mkfifo(fifo_path)

        # Build script command writing to the FIFO
        script_cmd = build_script_command(command_line, fifo_path)

        # Build pipeline commands
        pipeline_cmds = build_pipeline_commands(profile, rules_file)

        script_proc: Optional[subprocess.Popen[bytes]] = None
        try:
            # Start script process in background
            # The script command handles PTY creation and inherits stdin/stderr from parent
            # This allows the TUI to interact with the user even when stdout is redirected
            script_proc = subprocess.Popen(script_cmd)

            # Open FIFO for reading and build pipeline
            # Note: Opening FIFO blocks until writer (script) also opens it
            with open(fifo_path, "rb") as fifo:
                # Build pipeline: fifo | cmd1 | cmd2 | ... | stdout
                processes: list[subprocess.Popen[bytes]] = []
                current_stdin: object = fifo  # file object for first command

                # Set PYTHONUNBUFFERED for all processes to ensure real-time output
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"

                # Stage names for debug output
                stage_names = ["script", "clear_lines", "consolidate", "uniqseq", "cut"]
                if len(pipeline_cmds) > 4:  # Has additional_pipeline
                    stage_names.append("additional")

                # Add tee for stage 0 (script output) if stage_outputs enabled
                if stage_outputs:
                    stage_file = f"{output_file}-0-script.bin"
                    tee_proc = subprocess.Popen(
                        ["tee", stage_file],
                        stdin=current_stdin,  # type: ignore
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    processes.append(tee_proc)
                    current_stdin = tee_proc.stdout

                # Chain pipeline commands
                for i, cmd in enumerate(pipeline_cmds):
                    proc = subprocess.Popen(
                        cmd,
                        stdin=current_stdin,  # type: ignore
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                    )
                    processes.append(proc)
                    current_stdin = proc.stdout

                    # Add tee for this stage's output if stage_outputs enabled
                    if stage_outputs and i < len(stage_names) - 1:
                        stage_num = i + 1  # +1 because stage 0 is script
                        stage_file = f"{output_file}-{stage_num}-{stage_names[stage_num]}.bin"
                        tee_proc = subprocess.Popen(
                            ["tee", stage_file],
                            stdin=current_stdin,  # type: ignore
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                        )
                        processes.append(tee_proc)
                        current_stdin = tee_proc.stdout

                # Read from final process and write to output file
                if current_stdin and current_stdin != fifo:
                    try:
                        with open(output_file, "wb") as outfile:
                            for line in current_stdin:  # type: ignore
                                outfile.write(line)
                                outfile.flush()
                    except KeyboardInterrupt:
                        # User interrupted - clean up
                        pass
                    finally:
                        current_stdin.close()  # type: ignore

                # Wait for script process
                script_exit_code = script_proc.wait()

                # Wait for pipeline processes and collect errors
                errors: list[str] = []
                for i, proc in enumerate(processes):
                    proc.wait()
                    if proc.returncode != 0 and proc.stderr:
                        stderr_output = proc.stderr.read().decode("utf-8", errors="replace")
                        errors.append(
                            f"pipeline stage {i} (exit {proc.returncode}):\n{stderr_output}"
                        )

                # Report errors
                if errors:
                    print("Pipeline errors:", file=sys.stderr)
                    for error in errors:
                        print(error, file=sys.stderr)

                return script_exit_code

        except Exception as e:
            print(f"Error running pipeline: {e}", file=sys.stderr)
            # Clean up
            if script_proc is not None:
                try:
                    script_proc.terminate()
                except Exception:
                    pass
            return 1
