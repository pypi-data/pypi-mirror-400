"""
Convert escape control sequences to readable text.

Based on escape_filter.py from claude-logging project.
"""

import sys
from pathlib import Path
from typing import Optional, TextIO

ESC = "\x1b"


def screen_cursor_up(output_stream: TextIO) -> None:
    """Move cursor up one line"""
    output_stream.write("[cursor_up]")


def screen_clear(output_stream: TextIO) -> None:
    """Clear the screen"""
    output_stream.write("[screen_clear]")


def screen_cursor_to_bol(output_stream: TextIO) -> None:
    """Move cursor to beginning of line"""
    output_stream.write("[cursor_to_bol]")


def screen_cursor_to_home(output_stream: TextIO) -> None:
    """Move cursor to home position"""
    output_stream.write("[cursor_to_home]")


def hide_cursor(output_stream: TextIO) -> None:
    """Hide cursor (DECTCEM)"""
    # Commented out to reduce noise - uncomment if needed for debugging
    # output_stream.write("[hide_cursor]")
    pass


def show_cursor(output_stream: TextIO) -> None:
    """Show cursor (DECTCEM)"""
    # Commented out to reduce noise - uncomment if needed for debugging
    # output_stream.write("[show_cursor]")
    pass


def enable_bracketed_paste(output_stream: TextIO) -> None:
    """Enable bracketed paste mode"""
    output_stream.write("[bracketed_paste_on]")


def disable_bracketed_paste(output_stream: TextIO) -> None:
    """Disable bracketed paste mode"""
    output_stream.write("[bracketed_paste_off]")


def enable_sync_output(output_stream: TextIO) -> None:
    """Enable synchronized output mode"""
    output_stream.write("[sync_output_on]")


def disable_sync_output(output_stream: TextIO) -> None:
    """Disable synchronized output mode"""
    output_stream.write("[sync_output_off]")


def enable_focus_events(output_stream: TextIO) -> None:
    """Enable focus event mode"""
    output_stream.write("[focus_events_on]")


def disable_focus_events(output_stream: TextIO) -> None:
    """Disable focus event mode"""
    output_stream.write("[focus_events_off]")


def read_char(input_stream: TextIO) -> Optional[str]:
    """Read a single character from input stream, returns None on EOF"""
    c = input_stream.read(1)
    return c if c else None


def convert_string(s: str) -> str:
    """Convert a string, replacing multi-byte characters with [U+XXXX] tokens"""
    result: list[str] = []
    for c in s:
        code = ord(c)
        if code == 0xA0:  # Non-breaking space
            result.append("[NBSP]")
        elif code == 0x07:  # Bell/alert
            result.append("[BEL]")
        elif code > 0x7F:  # Multi-byte UTF-8 character (non-ASCII)
            result.append(f"[U+{code:04X}]")
        else:
            result.append(c)
    return "".join(result)


def write_char(output_stream: TextIO, c: str) -> None:
    """Write a single character to output stream"""
    output_stream.write(c)


def handle_escape_sequence(input_stream: TextIO, first_char: str, output_stream: TextIO) -> None:
    """
    Handle ANSI escape sequences.

    Args:
        input_stream: Input stream to read from
        first_char: First character after ESC
        output_stream: Output stream to write to
    """
    # ignoring: character set selection sequences ESC ( X, ESC ) X, etc.

    if first_char == "]":
        # OSC (Operating System Command) - first_char == ']' - read until BEL (0x07) or ST (ESC \)
        buf: list[str] = []
        while len(buf) < 256:  # Safety limit
            c = read_char(input_stream)
            if c is None:  # EOF
                break
            if ord(c) == 0x07:  # BEL terminates OSC
                break
            buf.append(c)

        # OSC sequences like ]0;title or ]2;title set window title
        buf_str = "".join(buf)
        if buf_str.startswith("0;"):
            # Set window title (icon + window)
            title = buf_str[2:]  # Skip "0;"
            title_converted = convert_string(title)
            output_stream.write(f"[window-title-icon:{title_converted}]")
        elif buf_str.startswith("2;"):
            # Set window title only
            title = buf_str[2:]  # Skip "2;"
            title_converted = convert_string(title)
            output_stream.write(f"[window-title:{title_converted}]")
        else:
            # Other OSC sequence - pass through as-is
            output_stream.write(ESC)
            output_stream.write("]")
            output_stream.write(buf_str)
            output_stream.write("\x07")  # BEL terminator that we consumed
        return

    if first_char == "[":
        # CSI (Control Sequence Introducer) - read until final byte
        buf: list[str] = []
        i = 0

        while i < 16:  # Increased to handle longer sequences like 38;5;174m
            c = read_char(input_stream)
            if c is None:  # EOF
                break
            buf.append(c)
            i += 1
            # CSI end: characters in range '@' to '~' (0x40 to 0x7E)
            if ord("@") <= ord(c) <= ord("~"):
                break

        buf_str = "".join(buf)

        if buf_str == "1A":
            screen_cursor_up(output_stream)
        elif buf_str == "2J":
            screen_clear(output_stream)
        elif buf_str == "2K":
            # Clear line
            output_stream.write("[clear_line]")
        elif buf_str == "3J":
            screen_clear(output_stream)
        elif buf_str == "F":
            screen_cursor_up(output_stream)
            screen_cursor_to_bol(output_stream)
        elif buf_str == "G":
            screen_cursor_to_bol(output_stream)
        elif buf_str == "H":
            screen_cursor_to_home(output_stream)
        elif buf_str == "?25l":
            hide_cursor(output_stream)
        elif buf_str == "?25h":
            show_cursor(output_stream)
        elif buf_str == "?2004h":
            enable_bracketed_paste(output_stream)
        elif buf_str == "?2004l":
            disable_bracketed_paste(output_stream)
        elif buf_str == "?2026h":
            enable_sync_output(output_stream)
        elif buf_str == "?2026l":
            disable_sync_output(output_stream)
        elif buf_str == "?1004h":
            enable_focus_events(output_stream)
        elif buf_str == "?1004l":
            disable_focus_events(output_stream)
        else:
            # Generic CSI sequence - pass through as-is (includes color/formatting)
            output_stream.write(ESC)
            output_stream.write("[")
            output_stream.write(buf_str)
    else:
        # Other escape sequences - pass through as-is
        output_stream.write(ESC)
        output_stream.write(first_char)


def process_stream(input_stream: TextIO, output_stream: TextIO) -> None:
    """
    Process input stream, handling escape sequences and writing to output.

    Args:
        input_stream: Input stream to read from
        output_stream: Output stream to write to
    """
    while True:
        c = read_char(input_stream)
        if c is None:  # EOF
            break

        if c == ESC:
            next_char = read_char(input_stream)
            if next_char is None:  # EOF
                break
            handle_escape_sequence(input_stream, next_char, output_stream)
        else:
            write_char(output_stream, c)


def decode_file(input_file: Path, output_file: Optional[Path] = None) -> None:
    """
    Decode escape sequences in a file.

    Args:
        input_file: Path to input file
        output_file: Path to output file (None = stdout)
    """
    with open(input_file, encoding="utf-8", errors="replace") as infile:
        if output_file:
            with open(output_file, "w", encoding="utf-8") as outfile:
                process_stream(infile, outfile)
        else:
            process_stream(infile, sys.stdout)
