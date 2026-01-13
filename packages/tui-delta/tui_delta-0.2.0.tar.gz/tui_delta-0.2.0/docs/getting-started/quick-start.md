# Quick Start

Get started with `tui-delta` in 5 minutes.

## Prerequisites

!!! warning "syslog-ng Required"
    `tui-delta` requires syslog-ng to be installed. See the [Installation Guide](installation.md) for detailed setup instructions.

## Installation

**Recommended (automatically installs syslog-ng):**
```bash
brew tap jeffreyurban/tui-delta
brew install tui-delta
```

**Alternative (requires manual syslog-ng installation):**
```bash
# First install syslog-ng (see Installation Guide), then:
pip install tui-delta
```

## Basic Usage

### Test with Simple Commands

To understand how tui-delta works, you can test with simple commands:

```bash
echo "test" | tui-delta into /tmp/output.log --profile minimal -- cat
```

The `minimal` profile passes input through with minimal processing.

### List Available Profiles

See what profiles are available:

```bash
tui-delta list-profiles
```

This shows the built-in profiles: `claude_code`, `generic`, and `minimal`.

### Log an AI Assistant Session

<!-- interactive-only -->
The primary use case - wrap Claude Code and capture the session:

```console
$ tui-delta into session.log --profile claude_code -- claude code
```

This:

1. Runs Claude Code normally (you can interact with it)
2. Captures all terminal output
3. Processes it to remove duplicates and cleared lines
4. Streams clean output to `session.log`

See [AI Assistant Logging](../use-cases/ai-assistants/ai-assistants.md) for complete examples.

### View Captured Logs

Logs preserve terminal formatting:

<!-- interactive-only -->
```console
$ less -R session.log
```

The `-R` flag preserves colors and formatting.

### Plain Text Logs (Strip ANSI Formatting)

For clean plain text logs without colors or formatting, pipe through a filter:

**Using sed (most portable):**
```bash
# Create a named pipe for post-processing
mkfifo /tmp/tui-pipe
tui-delta into /tmp/tui-pipe --profile claude_code -- claude &
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' < /tmp/tui-pipe > clean.log
```

**Using ansifilter (recommended if available):**
```bash
# Install
brew install ansifilter  # macOS
apt install ansifilter   # Ubuntu/Debian

# Create a named pipe for post-processing
mkfifo /tmp/tui-pipe
tui-delta into /tmp/tui-pipe --profile claude_code -- claude &
ansifilter < /tmp/tui-pipe > clean.log
```

## Common Patterns

### Save to File

```console
$ tui-delta into output.log --profile minimal -- echo "test output"
```

### Use with Different Profiles

Start with `generic` profile for non-Claude-Code applications, then customize as needed. See [Custom Profiles](../guides/custom-profiles.md) for creating profiles tailored to your TUI.

## Debugging

If you need to understand how tui-delta processes output or debug pipeline issues:

**Capture stage outputs:**
<!-- interactive-only -->
```console
$ tui-delta into out.log --stage-outputs --profile claude_code -- claude
# Creates: out.log-0-script.bin, out.log-1-clear_lines.bin, etc.
```

**Decode escape sequences:**
<!-- interactive-only -->
```console
$ tui-delta decode-escapes session.log-0-script.bin
# Shows readable text like [clear_line] instead of escape codes
```

See the [CLI Reference](../reference/cli.md) for complete details.

## Next Steps

- **[Basic Concepts](basic-concepts.md)** - Understand how tui-delta works
- **[AI Assistant Logging](../use-cases/ai-assistants/ai-assistants.md)** - Examples with Claude Code and other AI assistants
- **[CLI Reference](../reference/cli.md)** - Complete command-line options
- **[Custom Profiles](../guides/custom-profiles.md)** - Create profiles for your TUI apps
