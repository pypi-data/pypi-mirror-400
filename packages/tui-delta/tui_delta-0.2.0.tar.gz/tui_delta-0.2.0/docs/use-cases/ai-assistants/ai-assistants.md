# Logging AI Assistant Sessions

Primary use case: capturing and logging AI assistant interactive sessions.

## AI Assistant Compatibility

- **Claude Code** - Fully supported with optimized profile
- **Cline, Cursor, Aider, etc.** - Expected to work; likely requires profile customization for best results

**Note:** Only Claude Code is supported. Other assistants are expected to work, with custom profiles necessary for optimal results. Community contributions welcome.

## Claude Code Sessions

### Basic Logging

<!-- interactive-only -->
```console
$ tui-delta into session.log --profile claude_code -- claude code
```

Captures the full session with everything visible in the view and scrollback:

- User prompts and assistant responses
- Tool use (file reads, writes, commands)
- Ephemeral content (status reports, active files, etc.)
- Dialog interactions
- Window titles

### Real-time Monitoring + Logging

<!-- interactive-only -->
```console
$ tui-delta into session.log --profile claude_code -- claude code
```

Interact in terminal AND save to file simultaneously.

### Review Logged Session

<!-- interactive-only -->
```console
$ less -R session.log
```

The `-R` flag may be necessary to preserve ANSI colors and formatting on some systems.

### Plain Text Logs

For clean plain text logs without ANSI colors or formatting:

**Using sed (most portable):**
```bash
# Create a named pipe for post-processing
mkfifo /tmp/tui-pipe
tui-delta into /tmp/tui-pipe --profile claude_code -- claude code &
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' < /tmp/tui-pipe > clean-session.log
```

**Using ansifilter (recommended if available):**
```bash
# Install
brew install ansifilter  # macOS
apt install ansifilter   # Ubuntu/Debian

# Create a named pipe for post-processing
mkfifo /tmp/tui-pipe
tui-delta into /tmp/tui-pipe --profile claude_code -- claude code &
ansifilter < /tmp/tui-pipe > clean-session.log
```

This is useful for:
- Processing logs with tools that don't handle ANSI codes
- Reducing log file size
- Clean text for documentation or sharing
- Simpler grep/analysis without color codes

## Other AI Assistants

Start with the `generic` profile:

<!-- interactive-only -->
```console
$ tui-delta into aider.log --profile generic -- aider
$ tui-delta into cursor.log --profile generic -- cursor
$ tui-delta into cline.log --profile generic -- cline
```

For best results, you'll likely need to create a custom profile. See [Custom Profiles](../../guides/custom-profiles.md).

**Community contributions:** We welcome profile contributions for other AI assistants!

## Use Cases

### Session Archival

Keep records of AI-assisted development sessions:

<!-- interactive-only -->
```console
$ tui-delta into "$(date +%Y%m%d).log" --profile claude_code -- claude code
```

Creates timestamped log files for each session.

### Review and Learning

Review past sessions to:

- Understand what changes were made
- Learn from assistant's suggestions
- Document project decisions
- Share examples with team

### Debugging

When unexpected behavior occurs:

<!-- interactive-only -->
```console
$ tui-delta into full-session.log --profile claude_code -- claude code
```

Captures both stdout and stderr for debugging.

## Log Format

Logged sessions:

- Preserve original terminal appearance
- Include all meaningful content changes
- Remove redundant screen redraws
- Viewable with standard Unix tools (`less`, `grep`, etc.)

!!! tip "Monitoring output while logging"
    To monitor output while logging, use `tail -f` in another terminal:

    ```bash
    tui-delta into session.log --profile claude_code -- claude
    # Then in another terminal:
    tail -f session.log
    ```

### Searching Session History

Search through your session while Claude is running:

```bash
# In one terminal: run Claude
tui-delta into session.log --profile claude_code -- claude code

# In another terminal: view and search
less +F session.log
```

In `less`:
- Press `Ctrl+C` to stop following and enter search mode
- Search with `/pattern` (e.g., `/error`, `/function`)
- Navigate with `n` (next) and `N` (previous)
- Press `F` to resume following mode

This lets you search the entire session history while Claude continues running.

## Integration with Logging Tools

### Append to Daily Log

<!-- interactive-only -->
```console
$ tui-delta into daily-$(date +%Y%m%d).log --profile claude_code -- claude code
```

Note: To append rather than overwrite, manually append to the file after the session.

### Pipe to Analysis Tools

**Process after session:**
```bash
# Capture session first
tui-delta into session.log --profile claude_code -- claude code

# Then analyze
grep -i "error" session.log
```

**Real-time filtering with named pipe:**
```bash
# Create pipe and filter in background
mkfifo /tmp/claude-pipe
grep -i "error" < /tmp/claude-pipe > errors.log &

# Run session
tui-delta into /tmp/claude-pipe --profile claude_code -- claude code
```

### Stream to Remote Logging

```bash
# Create pipe for syslog streaming
mkfifo /tmp/claude-pipe
logger -t claude-code < /tmp/claude-pipe &
tui-delta into /tmp/claude-pipe --profile claude_code -- claude code
```

## Next Steps

- **[Quick Start](../../getting-started/quick-start.md)** - Get started quickly
- **[Custom Profiles](../../guides/custom-profiles.md)** - Create profiles for other assistants
