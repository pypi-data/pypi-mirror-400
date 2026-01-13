"""Tests for escape_decoder module."""

import io

import pytest

from tui_delta.escape_decoder import (
    convert_string,
    decode_file,
    disable_bracketed_paste,
    disable_focus_events,
    disable_sync_output,
    enable_bracketed_paste,
    enable_focus_events,
    enable_sync_output,
    handle_escape_sequence,
    process_stream,
    read_char,
    screen_clear,
    screen_cursor_to_bol,
    screen_cursor_to_home,
    screen_cursor_up,
    write_char,
)


@pytest.mark.unit
class TestHelperFunctions:
    """Test helper functions."""

    def test_read_char_returns_character(self):
        """Test read_char returns a character"""
        stream = io.StringIO("a")
        assert read_char(stream) == "a"

    def test_read_char_returns_none_on_eof(self):
        """Test read_char returns None on EOF"""
        stream = io.StringIO("")
        assert read_char(stream) is None

    def test_write_char(self):
        """Test write_char writes character to stream"""
        stream = io.StringIO()
        write_char(stream, "x")
        assert stream.getvalue() == "x"


@pytest.mark.unit
class TestConvertString:
    """Test convert_string function."""

    def test_convert_string_ascii(self):
        """Test convert_string with ASCII characters"""
        assert convert_string("hello") == "hello"

    def test_convert_string_nbsp(self):
        """Test convert_string with non-breaking space"""
        assert convert_string("\xa0") == "[NBSP]"

    def test_convert_string_bell(self):
        """Test convert_string with bell character"""
        assert convert_string("\x07") == "[BEL]"

    def test_convert_string_multibyte(self):
        """Test convert_string with multi-byte UTF-8 characters"""
        # Test with various Unicode characters
        assert "[U+" in convert_string("€")  # Euro sign
        assert "[U+" in convert_string("→")  # Right arrow
        assert "[U+" in convert_string("✓")  # Check mark

    def test_convert_string_mixed(self):
        """Test convert_string with mixed characters"""
        result = convert_string("hello\xa0world\x07!")
        assert "hello" in result
        assert "[NBSP]" in result
        assert "world" in result
        assert "[BEL]" in result


@pytest.mark.unit
class TestScreenFunctions:
    """Test screen control functions."""

    def test_screen_cursor_up(self):
        """Test screen_cursor_up writes marker"""
        stream = io.StringIO()
        screen_cursor_up(stream)
        assert stream.getvalue() == "[cursor_up]"

    def test_screen_clear(self):
        """Test screen_clear writes marker"""
        stream = io.StringIO()
        screen_clear(stream)
        assert stream.getvalue() == "[screen_clear]"

    def test_screen_cursor_to_bol(self):
        """Test screen_cursor_to_bol writes marker"""
        stream = io.StringIO()
        screen_cursor_to_bol(stream)
        assert stream.getvalue() == "[cursor_to_bol]"

    def test_screen_cursor_to_home(self):
        """Test screen_cursor_to_home writes marker"""
        stream = io.StringIO()
        screen_cursor_to_home(stream)
        assert stream.getvalue() == "[cursor_to_home]"


@pytest.mark.unit
class TestModeFunctions:
    """Test terminal mode functions."""

    def test_enable_bracketed_paste(self):
        """Test enable_bracketed_paste writes marker"""
        stream = io.StringIO()
        enable_bracketed_paste(stream)
        assert stream.getvalue() == "[bracketed_paste_on]"

    def test_disable_bracketed_paste(self):
        """Test disable_bracketed_paste writes marker"""
        stream = io.StringIO()
        disable_bracketed_paste(stream)
        assert stream.getvalue() == "[bracketed_paste_off]"

    def test_enable_sync_output(self):
        """Test enable_sync_output writes marker"""
        stream = io.StringIO()
        enable_sync_output(stream)
        assert stream.getvalue() == "[sync_output_on]"

    def test_disable_sync_output(self):
        """Test disable_sync_output writes marker"""
        stream = io.StringIO()
        disable_sync_output(stream)
        assert stream.getvalue() == "[sync_output_off]"

    def test_enable_focus_events(self):
        """Test enable_focus_events writes marker"""
        stream = io.StringIO()
        enable_focus_events(stream)
        assert stream.getvalue() == "[focus_events_on]"

    def test_disable_focus_events(self):
        """Test disable_focus_events writes marker"""
        stream = io.StringIO()
        disable_focus_events(stream)
        assert stream.getvalue() == "[focus_events_off]"


@pytest.mark.unit
class TestHandleEscapeSequence:
    """Test handle_escape_sequence function."""

    def test_handle_csi_cursor_up(self):
        """Test CSI cursor up sequence"""
        input_stream = io.StringIO("1A")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert output_stream.getvalue() == "[cursor_up]"

    def test_handle_csi_screen_clear_2j(self):
        """Test CSI screen clear 2J sequence"""
        input_stream = io.StringIO("2J")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert output_stream.getvalue() == "[screen_clear]"

    def test_handle_csi_screen_clear_3j(self):
        """Test CSI screen clear 3J sequence"""
        input_stream = io.StringIO("3J")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert output_stream.getvalue() == "[screen_clear]"

    def test_handle_csi_clear_line(self):
        """Test CSI clear line sequence"""
        input_stream = io.StringIO("2K")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert output_stream.getvalue() == "[clear_line]"

    def test_handle_csi_cursor_up_and_bol(self):
        """Test CSI cursor up and BOL sequence"""
        input_stream = io.StringIO("F")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert "[cursor_up]" in output_stream.getvalue()
        assert "[cursor_to_bol]" in output_stream.getvalue()

    def test_handle_csi_cursor_to_bol(self):
        """Test CSI cursor to BOL sequence"""
        input_stream = io.StringIO("G")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert output_stream.getvalue() == "[cursor_to_bol]"

    def test_handle_csi_cursor_to_home(self):
        """Test CSI cursor to home sequence"""
        input_stream = io.StringIO("H")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        assert output_stream.getvalue() == "[cursor_to_home]"

    def test_handle_csi_color_passthrough(self):
        """Test CSI color sequence passes through"""
        input_stream = io.StringIO("31m")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        # Color sequences should pass through as-is
        assert output_stream.getvalue() == "\x1b[31m"

    def test_handle_osc_window_title(self):
        """Test OSC window title sequence"""
        input_stream = io.StringIO("2;My Title\x07")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "]", output_stream)
        assert "[window-title:My Title]" in output_stream.getvalue()

    def test_handle_osc_window_title_with_icon(self):
        """Test OSC window title with icon sequence"""
        input_stream = io.StringIO("0;My Title\x07")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "]", output_stream)
        assert "[window-title-icon:My Title]" in output_stream.getvalue()

    def test_handle_osc_window_title_with_multibyte(self):
        """Test OSC window title with multibyte characters"""
        input_stream = io.StringIO("2;Test→Title\x07")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "]", output_stream)
        # Multibyte character should be converted
        result = output_stream.getvalue()
        assert "[window-title:" in result
        assert "[U+" in result  # Multibyte char converted

    def test_handle_osc_other_sequence(self):
        """Test OSC other sequence passes through"""
        input_stream = io.StringIO("9;test\x07")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "]", output_stream)
        # Other OSC sequences should pass through
        assert "\x1b]9;test\x07" in output_stream.getvalue()

    def test_handle_osc_eof(self):
        """Test OSC sequence with EOF"""
        input_stream = io.StringIO("2;Title")  # No terminator
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "]", output_stream)
        # Should handle gracefully without crashing

    def test_handle_csi_eof(self):
        """Test CSI sequence with EOF"""
        input_stream = io.StringIO("2")  # Incomplete sequence
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "[", output_stream)
        # Should handle gracefully without crashing

    def test_handle_other_escape(self):
        """Test other escape sequences pass through"""
        input_stream = io.StringIO("")
        output_stream = io.StringIO()
        handle_escape_sequence(input_stream, "X", output_stream)
        assert output_stream.getvalue() == "\x1bX"


@pytest.mark.unit
class TestProcessStream:
    """Test process_stream function."""

    def test_process_stream_plain_text(self):
        """Test processing plain text"""
        input_stream = io.StringIO("hello world")
        output_stream = io.StringIO()
        process_stream(input_stream, output_stream)
        assert output_stream.getvalue() == "hello world"

    def test_process_stream_with_clear_line(self):
        """Test processing text with clear line sequence"""
        input_stream = io.StringIO("line1\n\x1b[2Kline2\n")
        output_stream = io.StringIO()
        process_stream(input_stream, output_stream)
        assert "line1" in output_stream.getvalue()
        assert "[clear_line]" in output_stream.getvalue()
        assert "line2" in output_stream.getvalue()

    def test_process_stream_with_window_title(self):
        """Test processing text with window title sequence"""
        input_stream = io.StringIO("\x1b]2;Title\x07text")
        output_stream = io.StringIO()
        process_stream(input_stream, output_stream)
        assert "[window-title:Title]" in output_stream.getvalue()
        assert "text" in output_stream.getvalue()

    def test_process_stream_eof_after_escape(self):
        """Test processing stream with EOF immediately after ESC"""
        input_stream = io.StringIO("text\x1b")
        output_stream = io.StringIO()
        process_stream(input_stream, output_stream)
        assert "text" in output_stream.getvalue()


@pytest.mark.integration
class TestDecodeFile:
    """Test decode_file function."""

    def test_decode_file_to_output_file(self, tmp_path):
        """Test decoding file to output file"""
        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"

        # Write test content with escape sequences
        input_file.write_text("line1\n\x1b[2Kline2\n")

        # Decode
        decode_file(input_file, output_file)

        # Verify output
        result = output_file.read_text()
        assert "line1" in result
        assert "[clear_line]" in result
        assert "line2" in result

    def test_decode_file_to_stdout(self, tmp_path, capsys):
        """Test decoding file to stdout"""
        input_file = tmp_path / "input.txt"

        # Write test content with escape sequences
        input_file.write_text("test\x1b[2K\n")

        # Decode to stdout
        decode_file(input_file)

        # Capture stdout
        captured = capsys.readouterr()
        assert "test" in captured.out
        assert "[clear_line]" in captured.out

    def test_decode_file_preserves_colors(self, tmp_path):
        """Test decoding file preserves color sequences"""
        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"

        # Write test content with color escape sequences
        input_file.write_text("\x1b[31mred\x1b[0m")

        # Decode
        decode_file(input_file, output_file)

        # Verify colors are preserved
        result = output_file.read_text()
        assert "\x1b[31m" in result
        assert "red" in result
        assert "\x1b[0m" in result
