"""Command-line interface for tui-delta."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .run import run_tui_with_pipeline

app = typer.Typer(
    name="tui-delta",
    help=(
        "Run TUI applications with real-time delta processing "
        "for monitoring and logging AI assistant sessions.\n\n"
        "Example: tui-delta into session.log --profile claude_code -- claude"
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

console = Console(stderr=True)  # All output to stderr to preserve stdout for data


def version_callback(value: bool) -> None:
    """Print version and exit if --version flag is provided."""
    if value:
        typer.echo(f"tui-delta version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    Run TUI applications with real-time delta processing for monitoring
    and logging AI assistant sessions.
    """
    pass


@app.command()
def into(
    output_file: Path = typer.Argument(
        ...,  # type: ignore[arg-type]  # Ellipsis is valid Typer syntax for required args
        help="Output file to write processed deltas (can be a named pipe)",
        metavar="OUTPUT-FILE",
    ),
    command_line: list[str] = typer.Argument(
        ...,  # type: ignore[arg-type]  # Ellipsis is valid Typer syntax for required args
        help="Full command-line to run, including arguments and options",
        metavar="COMMAND-LINE...",
    ),
    profile: Optional[str] = typer.Option(
        None,
        "--profile",
        "-p",
        help="Clear rules profile (claude_code, generic, minimal, or custom)",
    ),
    rules_file: Optional[Path] = typer.Option(
        None,
        "--rules-file",
        help="Path to custom clear_rules.yaml file",
        exists=True,
        dir_okay=False,
    ),
    stage_outputs: bool = typer.Option(
        False,
        "--stage-outputs",
        help="Save output from each pipeline stage to OUTPUT-FILE-N-stage.bin",
    ),
) -> None:
    """
    Run a TUI application and pipe processed output into a file.

    Wraps the TUI application to capture all terminal output, processes it through
    the pipeline, and writes processed deltas to the output file.

    The TUI displays and operates normally - the user can interact with it as if
    it weren't wrapped. Meanwhile, the processed output streams to the file in real-time.

    The output file can be a regular file or a user-created named pipe for
    post-processing with other tools.

    \b
    Examples:
        # Run claude and save processed deltas
        tui-delta into session.log --profile claude_code -- claude

        # Use a different profile
        tui-delta into test.log --profile generic -- npm test

        # Run with command-line options
        tui-delta into output.txt -- python script.py --verbose

        # Use a named pipe for post-processing
        mkfifo /tmp/my-pipe
        cat /tmp/my-pipe | other-tool > final.txt &
        tui-delta into /tmp/my-pipe --profile claude_code -- claude

    \b
    Pipeline:
        clear_lines → consolidate → uniqseq → cut → uniqseq
    """
    # Validate profile if specified
    if profile:
        from .clear_rules import ClearRules

        available_profiles = ClearRules.list_profiles(rules_file)
        if profile not in available_profiles:
            console.print(
                f"[red]Error:[/red] Profile '{profile}' not found.\n"
                f"Available profiles: {', '.join(sorted(available_profiles.keys()))}\n"
                f"Use 'tui-delta list-profiles' to see descriptions."
            )
            raise typer.Exit(1)

    exit_code = run_tui_with_pipeline(
        command_line=command_line,
        output_file=output_file,
        profile=profile,
        rules_file=rules_file,
        stage_outputs=stage_outputs,
    )
    raise typer.Exit(exit_code)


@app.command(name="list-profiles")
def list_profiles_cmd(
    rules_file: Optional[Path] = typer.Option(
        None,
        "--rules-file",
        help="Path to custom clear_rules.yaml file",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """
    List available clear rules profiles.

    Shows all available profiles from the default clear_rules.yaml
    or a custom rules file.
    """
    from .clear_rules import ClearRules

    profiles = ClearRules.list_profiles(rules_file)
    console.print("[bold]Available profiles:[/bold]")
    for name, description in profiles.items():
        console.print(f"  [cyan]{name}[/cyan]: {description}")


@app.command(name="decode-escapes")
def decode_escapes_cmd(
    input_file: Path = typer.Argument(
        ...,  # type: ignore[arg-type]  # Ellipsis is valid Typer syntax for required args
        help="Input file with escape sequences",
        exists=True,
        dir_okay=False,
        metavar="INPUT-FILE",
    ),
    output_file: Optional[Path] = typer.Argument(
        None,
        help="Output file (default: stdout)",
        metavar="OUTPUT-FILE",
    ),
) -> None:
    """
    Decode escape control sequences to readable text.

    Converts control sequences like clear-line, cursor movement, and window title
    to readable text markers like [clear_line], [cursor_up], [window-title:...].

    Color and formatting sequences (SGR) are passed through unchanged.

    \b
    Examples:
        # Decode to stdout
        tui-delta decode-escapes session.log-0-script.bin

        # Decode to file
        tui-delta decode-escapes session.log-0-script.bin decoded.txt

        # Pipe to less for viewing
        tui-delta decode-escapes session.log-0-script.bin | less -R
    """
    from .escape_decoder import decode_file

    try:
        decode_file(input_file, output_file)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
