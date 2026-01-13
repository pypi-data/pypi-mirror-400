# imc-prospector

[![PyPI](https://github.com/arJ-V/imc-prospector/actions/workflows/publish.yml/badge.svg)](https://github.com/arJ-V/imc-prospector/actions/workflows/publish.yml)
[![CI](https://github.com/arJ-V/imc-prospector/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/arJ-V/imc-prospector/actions/workflows/ci.yml)

CLI submitter and algorithm validator package for IMC Prosperity competition.

`imc-prospector` combines a static analysis checker with a command-line submitter to validate and submit your IMC Prosperity trading algorithms.

> **Note**: The CLI submitter is based on [jmerle/imc-prosperity-3-submitter](https://github.com/jmerle/imc-prosperity-3-submitter). [Jmerle](https://github.com/jmerle) is an incredible resource for getting started in IMC algo development.

## Features

- **Static Analysis Checker**: Validates your algorithm against IMC Prosperity requirements before submission
- **CLI Submitter**: Submit algorithms directly from the command line
- **Configurable**: Customize allowed imports and severity levels via YAML config

## Installation

```bash
pip install imc-prospector
```

## Quick Start

### Check an Algorithm

```bash
# Basic check
imc-prospector check my_trader.py

# Strict mode (warnings as errors)
imc-prospector check my_trader.py --strict

# Use custom config file
imc-prospector check my_trader.py --config my_config.yaml

# JSON output for CI
imc-prospector check my_trader.py --json

# Hide info messages
imc-prospector check my_trader.py --no-info

# Don't prompt, just exit with code
imc-prospector check my_trader.py --no-prompt
```

### Submit an Algorithm

```bash
# Submit with automatic checking (default)
imc-prospector submit my_trader.py

# Submit without running checker
imc-prospector submit my_trader.py --no-check

# Submit with custom config file
imc-prospector submit my_trader.py --config my_config.yaml

# Force submission even with errors/warnings (not recommended)
imc-prospector submit my_trader.py --force

# Specify output log file
imc-prospector submit my_trader.py --out logs/my_submission.log

# Don't download logs
imc-prospector submit my_trader.py --no-out

# Combine options: strict checking with custom config
imc-prospector submit my_trader.py --config custom.yaml --strict
```

## What Gets Checked

The checker validates several aspects of your algorithm:

- **Structure**: Ensures `Trader` class exists with a `run(self, state)` method
- **Imports**: Verifies only official allowed libraries are used (pandas, numpy, statistics, math, typing, jsonpickle)
- **Return**: Confirms the method returns a 3-tuple `(result, conversions, traderData)`
- **Timeouts**: Detects infinite loops, `time.sleep()` calls, and deep nesting that could cause timeouts
- **State**: Warns about instance variables that won't persist (Lambda is stateless)

## Configuration

Create `.prosperity.yaml` in your project root:

```yaml
# Override severity levels
severity:
  E001: error      # Forbidden import
  W040: warning    # Instance vars warning
  I030: off        # Disable print warnings

# Add custom allowed imports
imports:
  scipy: warn      # Allow with warning
  my_utils: true   # Custom module

# Adjust limits
limits:
  timeout_ms: 900
  max_loop_depth: 3
```

### Config Search Order

The checker searches for config files in this order:

1. `--config` argument (if provided via `check` or `submit` command)
2. `.prosperity.yaml` (current directory)
3. `.prosperity.yml` (current directory)
4. `prosperity.yaml` (current directory)
5. `prosperity_config.yaml` (current directory)
6. `~/.prosperity.yaml` (home directory)

The first config file found is used, with values merged into the default configuration.

**Note:** You can use `--config` with both `check` and `submit` commands to override the config file.

See `prosperity_config.yaml` for all available options.

## Submitting to Prosperity

### First Time Setup

On first submission, you'll be prompted for your Prosperity ID token. This token is stored securely in your system's keyring.

**How to get your token:**
1. Open the Prosperity website in your browser
2. Press F12 to open developer tools
3. Go to Application (Chrome) or Storage (Firefox) tab
4. Click on Local Storage → select the Prosperity website
5. Find the key: `CognitoIdentityServiceProvider.<some id>.<email>.idToken`
6. Copy the token value

The token is stored securely and you'll only need to update it when it expires.

### Submission Process

1. **Check** (optional, runs by default): Validates your algorithm
   - Errors block submission by default (use `--force` to bypass)
   - Warnings prompt for confirmation (use `--force` to skip prompt)
2. **Submit**: Uploads to Prosperity API
3. **Monitor**: Watches submission status
4. **Download**: Saves logs to `submissions/<timestamp>.log` (unless `--no-out`)

### Submission Options

| Option | Description |
|--------|-------------|
| `--no-check` | Skip running the checker before submission |
| `--config`, `-c` | Use a custom YAML config file for the checker |
| `--strict` | Treat checker warnings as errors |
| `--force` | Force submission even if checker finds errors/warnings (not recommended) |
| `--out`, `-o` | Specify output log file path |
| `--no-out` | Don't download submission logs |

## Handling Errors and Warnings

When submitting, the checker runs automatically. By default:

- **Errors** block submission. Use `--force` to bypass (not recommended).
- **Warnings** prompt for confirmation. Use `--force` to skip the prompt.

Example when errors are found:

```bash
$ imc-prospector submit my_trader.py
Running algorithm checker...
Checker found 2 error(s) and 1 warning(s):
  [E001]:5 Forbidden import: 'os'
  [E033]:45 run() returns only a dict, must return 3-tuple
  [W040]:10 Instance vars {'position'} may not persist

Submission aborted due to errors. Fix issues and try again.
   Use --force to bypass errors (not recommended).
```

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| E001 | Error | Forbidden/unsupported import |
| E002 | Error | Missing datamodel import |
| E003 | Error | Missing Trader class |
| E004 | Error | Missing run method |
| E010 | Error | Invalid run() signature |
| E020 | Error | Infinite loop detected |
| E021 | Error | time.sleep() detected |
| E030 | Error | Missing return statement |
| E031 | Error | Returns None |
| E032 | Error | Wrong return tuple size |
| E033 | Error | Returns dict instead of tuple |
| W020 | Warning | Risky while True loop |
| W021 | Warning | Loop variable not modified |
| W022 | Warning | Deep loop nesting |
| W030 | Warning | Can't verify return tuple |
| W040 | Warning | Instance variables won't persist |

## Example Output

```
============================================================
  IMC Prosperity Checker: my_trader.py
============================================================

ERRORS (2):
----------------------------------------
  [E001]:2 Forbidden import: 'os'
   Remove 'import os'. Official allowed: pandas, numpy, statistics, math, typing, jsonpickle

  [E033]:45 run() returns only a dict, must return 3-tuple
   return result, conversions, traderData

============================================================
Official requirements:
  • Imports: pandas, numpy, statistics, math, typing, jsonpickle
  • Return: (result, conversions, traderData)
  • Timeout: <900ms per run() call
============================================================
```

## Minimal Valid Trader

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    
    def run(self, state: TradingState):
        result = {}
        
        for product in state.order_depths:
            orders: List[Order] = []
            # Your trading logic here
            result[product] = orders
        
        traderData = ""  # Use jsonpickle to persist state
        conversions = 0
        
        return result, conversions, traderData
```

## Development

```bash
# Clone the repository
git clone https://github.com/arJ-V/imc-prospector.git
cd imc-prospector

# Install in development mode
pip install -e ".[dev]"

# Run linter
ruff check imcprospector/

# Run type checker
mypy imcprospector/
```

## License

MIT

## Acknowledgments

Built on top of the submitter structure from `imc-prosperity-3-submitter`. Uses the same API endpoint as the official Prosperity platform.
