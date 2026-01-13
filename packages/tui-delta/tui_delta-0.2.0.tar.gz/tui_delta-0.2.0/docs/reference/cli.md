# CLI Reference

Complete command-line reference for `tui-delta`.

## Commands

### `tui-delta into`

Run a TUI application and pipe processed output into a file.

**Usage:**

```console
$ tui-delta into OUTPUT-FILE [OPTIONS] -- COMMAND...
```

**Arguments:**

- `OUTPUT-FILE` - Output file to write processed deltas (can be a named pipe)
- `COMMAND...` - The TUI command to run (e.g., `claude code`, `npm test`)

**Options:**

- `--profile`, `-p` TEXT - Clear rules profile (claude_code, generic, minimal, or custom)
- `--rules-file` FILE - Path to custom clear_rules.yaml file
- `--stage-outputs` - Save output from each pipeline stage to OUTPUT-FILE-N-stage.bin
- `--help`, `-h` - Show help message

**Examples:**

Basic usage with Claude Code:

```console
$ tui-delta into session.log --profile claude_code -- claude code
```

Use generic profile for other TUI apps:

```console
$ tui-delta into aider.log --profile generic -- aider
```

Custom rules file:

```console
$ tui-delta into output.log --rules-file my-rules.yaml -- ./myapp
```

Use a named pipe for post-processing:

```console
$ mkfifo /tmp/my-pipe
$ cat /tmp/my-pipe | other-tool > final.txt &
$ tui-delta into /tmp/my-pipe --profile claude_code -- claude
```

Capture pipeline stage outputs for debugging:

```console
$ tui-delta into out.log --stage-outputs --profile claude_code -- claude
# Creates: out.log-0-script.bin, out.log-1-clear_lines.bin, etc.
```

**Pipeline:**

The `into` command processes output through:

```
script → clear_lines → consolidate → uniqseq → cut → additional_pipeline
```

Where `additional_pipeline` is profile-specific (e.g., final uniqseq for claude_code).

**Stage Outputs:**

When `--stage-outputs` is enabled, the command captures output from each pipeline stage:

- `OUTPUT-FILE-0-script.bin` - Raw script output (before any processing)
- `OUTPUT-FILE-1-clear_lines.bin` - After clear_lines processing (with prefixes)
- `OUTPUT-FILE-2-consolidate.bin` - After consolidate_clears (deduplicated blocks)
- `OUTPUT-FILE-3-uniqseq.bin` - After first uniqseq (deduplicated kept lines)
- `OUTPUT-FILE-4-cut.bin` - After cut (prefixes removed)
- `OUTPUT-FILE-5-additional.bin` - After additional_pipeline (if present)
- `OUTPUT-FILE` - Final processed output

Use stage outputs to:
- Debug pipeline processing issues
- Understand how each stage transforms the data
- Develop custom profiles by examining intermediate results
- Verify clear detection and consolidation behavior

### `tui-delta decode-escapes`

Decode escape control sequences to readable text.

**Usage:**

```console
$ tui-delta decode-escapes INPUT-FILE [OUTPUT-FILE]
```

**Arguments:**

- `INPUT-FILE` - Input file with escape sequences (required)
- `OUTPUT-FILE` - Output file for decoded text (optional, defaults to stdout)

**Description:**

Converts control sequences like clear-line, cursor movement, and window title to readable text markers. Color and formatting sequences (SGR) are passed through unchanged.

**Examples:**

Decode to stdout:

```console
$ tui-delta decode-escapes session.log-0-script.bin
```

Decode to file:

```console
$ tui-delta decode-escapes session.log-0-script.bin decoded.txt
```

Pipe to less for viewing:

```console
$ tui-delta decode-escapes session.log-0-script.bin | less -R
```

Examine raw script output with decoded escapes:

```console
$ tui-delta into out.log --stage-outputs --profile claude_code -- claude
$ tui-delta decode-escapes out.log-0-script.bin
```

**Decoded sequences:**

- `[clear_line]` - Clear line (ESC[2K)
- `[cursor_up]` - Cursor up (ESC[1A)
- `[cursor_to_bol]` - Cursor to beginning of line (ESC[G)
- `[cursor_to_home]` - Cursor to home position (ESC[H)
- `[screen_clear]` - Clear screen (ESC[2J, ESC[3J)
- `[window-title:...]` - Window title sequences
- `[window-title-icon:...]` - Window title with icon
- `[bracketed_paste_on/off]` - Bracketed paste mode
- `[sync_output_on/off]` - Synchronized output mode
- `[focus_events_on/off]` - Focus event mode

Color and formatting sequences (bold, italic, colors) are preserved unchanged.

### `tui-delta list-profiles`

List available clear rules profiles.

**Usage:**

```console
$ tui-delta list-profiles
```

**Example output:**

```console
$ tui-delta list-profiles
Available profiles:
  claude_code: Claude Code terminal UI (claude.ai/code)
  generic: Generic TUI with only universal rules
  minimal: Minimal - only base rule, no protections
```

## Profiles

### claude_code

Optimized for Claude Code terminal UI sessions.

**Features:**

- Preserves submitted user input (final occurrence)
- Normalizes dialog questions and choices
- Handles activity spinners
- Tracks thinking indicators
- Maintains scrollback output
- Deduplicates task progress updates
  - (keeping the last instance shown... e.g. generally the total token count for an action)

**Use when:** Logging Claude Code sessions

### generic

Basic processing for most TUI applications.

**Features:**

- Universal clear detection
- Blank line boundary protection
- No pattern normalization

**Use when:** Logging any TUI application, or as starting point for custom profiles

### minimal

Minimal processing with only base clear detection.

**Features:**

- Base clear count formula (N-1)
- No protections
- No pattern normalization

**Use when:** Debugging or maximum raw output

## Output

The `into` command writes processed output to the specified file:

```console
$ tui-delta into session.log --profile claude_code -- claude  # Save to file
```

For post-processing, use a named pipe:

```console
$ mkfifo /tmp/pipe
$ tui-delta into /tmp/pipe -- claude &
$ cat /tmp/pipe | your-tool > final.txt
```

## Exit Codes

- `0` - Success
- `1` - Error in pipeline stage
- TUI application's exit code is preserved

## Environment

### Terminal Size

The `script` command used by tui-delta respects terminal size. Set `COLUMNS` and `LINES` for consistent output:

```console
$ COLUMNS=120 LINES=40 tui-delta into s.log --profile claude_code -- claude
```

## Next Steps

- **[Quick Start](../getting-started/quick-start.md)** - Get started quickly
- **[Custom Profiles](../guides/custom-profiles.md)** - Create your own profiles
