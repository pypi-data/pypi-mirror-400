# Lumby

A CLI tool that wraps shell commands, streams output live, and provides AI-powered diagnosis when commands fail.

Named after **Lumbridge** in Old School RuneScape - where you respawn after death with knowledge of what killed you.

## Installation

```bash
pip install lumby
```

Or install from source:

```bash
git clone https://github.com/RasmusGodske/lumby.git
cd lumby
pip install -e .
```

## Usage

Lumby uses `--` to separate its flags from the wrapped command:

```bash
# Basic usage - wrap any command
lumby -- php artisan test --parallel
lumby -- npm run build
lumby -- cargo build

# With configuration
lumby --log-level=debug -- make test
lumby --response-guide="Keep it under 2 sentences" -- pytest
lumby --config=./lumby.json -- ./vendor/bin/phpstan
```

### What Happens

1. **Command runs normally** - You see output in real-time, just like running the command directly
2. **On success** - Lumby exits with the same exit code (0)
3. **On failure** - Lumby captures the output, sends it to Claude for diagnosis, and shows you a concise explanation of what went wrong

### Example Output

```
$ lumby -- php artisan test --filter=UserTest

   FAIL  Tests\Feature\UserServiceTest::test_user_creation_validates_email
   Expected exception [InvalidArgumentException] was not thrown.

   Tests:    1 failed, 15 passed
   Duration: 2.34s

════════════════════════════════════════════════════════════════════
   Diagnosis
════════════════════════════════════════════════════════════════════

The test expects InvalidArgumentException when creating a user with
invalid email, but UserService::create() doesn't validate email format.
Add email validation before line 45 in app/Services/UserService.php.

════════════════════════════════════════════════════════════════════
```

## Configuration

### CLI Flags

| Flag | Description |
|------|-------------|
| `--config PATH` | Path to JSON config file |
| `--log-file PATH` | Path to log file |
| `--log-level LEVEL` | Log level: debug, info, warning, error |
| `--response-guide TEXT` | Guide for AI response length/style |
| `--prompt-file PATH` | Path to custom prompt template |
| `--verbose` | Shortcut for detailed diagnosis |

### Config File

Create a `lumby.json`:

```json
{
  "log_file": "/tmp/lumby.log",
  "log_level": "info",
  "response_guide": "Keep it under 3 sentences"
}
```

Use it:

```bash
lumby --config=./lumby.json -- npm test
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LUMBY_LOG_FILE` | Path to log file |
| `LUMBY_LOG_LEVEL` | Log level |
| `LUMBY_RESPONSE_GUIDE` | Response guideline |
| `LUMBY_PROMPT_FILE` | Path to prompt template |

### Configuration Priority

CLI flags > Config file > Environment variables > Defaults

## Custom Prompts

Create a custom prompt template with these variables:

- `{command}` - The command that was run
- `{exit_code}` - The exit code
- `{output}` - The captured output
- `{response_guide}` - The response guideline

Example `my-prompt.md`:

```markdown
Analyze this failed command:

Command: {command}
Exit code: {exit_code}

Output:
{output}

{response_guide}
```

Use it:

```bash
lumby --prompt-file=./my-prompt.md -- make build
```

## Use Cases

### In CI/CD Pipelines

Get immediate diagnosis when builds fail:

```yaml
# GitHub Actions
- name: Run tests
  run: lumby -- npm test
```

### Wrapping Test Runners

```bash
# In your test script
#!/bin/bash
lumby -- php artisan test "$@"
```

### Development Workflow

```bash
# Quick iteration with diagnosis
lumby -- cargo build && ./target/debug/myapp
```

## Requirements

- Python 3.11+
- Claude API access (via `claude-agent-sdk`)

## Why "Lumby"?

The name comes from **Lumbridge**, the starting town in [Old School RuneScape](https://oldschool.runescape.com/).

In OSRS, when your character dies, you respawn in Lumbridge, affectionately called "Lumby" by players. You wake up at the castle, slightly confused, but with the knowledge of what killed you. Maybe it was that level 80 dragon you weren't ready for. Maybe you forgot to bring food. Either way, you learn from the experience.

That's exactly what this tool does. When your command "dies" (fails), you respawn with a diagnosis of what went wrong, so you can try again, smarter this time.

*Home teleport to Lumby.*

## License

MIT
