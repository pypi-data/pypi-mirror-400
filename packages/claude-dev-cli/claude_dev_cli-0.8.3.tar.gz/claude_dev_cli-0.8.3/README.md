# Claude Dev CLI

[![PyPI version](https://badge.fury.io/py/claude-dev-cli.svg)](https://badge.fury.io/py/claude-dev-cli)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-257%20passing-brightgreen.svg)](https://github.com/thinmanj/claude-dev-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Homebrew](https://img.shields.io/badge/homebrew-available-orange.svg)](https://github.com/thinmanj/homebrew-tap)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful command-line tool for developers using Claude AI with multi-API routing, test generation, code review, and comprehensive usage tracking.

## Features

### 🔑 Multi-API Key Management
- **Secure Storage**: API keys stored in system keyring (macOS Keychain, Linux Secret Service, Windows Credential Locker)
- Route tasks to different Claude API keys (personal, client, enterprise)
- Automatic API selection based on project configuration
- Automatic migration from plaintext to secure storage

### 🧪 Developer Tools
- **Test Generation**: Automatic pytest test generation for Python code
- **Code Review**: Comprehensive code reviews with security, performance, and best practice checks
- **Debug Assistant**: Analyze errors and get fixes with explanations
- **Documentation**: Generate docstrings and README documentation
- **Refactoring**: Get suggestions for code improvements
- **Git Integration**: Generate conventional commit messages from diffs

### 📊 Usage Tracking
- Track token usage per API key
- Cost estimation based on current pricing
- Filter by date range and API config
- Detailed breakdowns by model, date, and API

### 💬 Interaction Modes
- **Single-shot**: Quick questions with piping support
- **Interactive**: Chat mode with conversation history
- **Streaming**: Real-time responses

### 📝 Custom Templates
- **Built-in Templates**: 8 pre-built templates for common tasks (code review, testing, debugging, etc.)
- **User Templates**: Create and manage your own reusable prompt templates
- **Variable Substitution**: Use {{variable}} placeholders for dynamic content
- **Categories**: Organize templates by category (review, testing, debugging, etc.)

### 🧠 Context Intelligence (v0.8.0+)
- **Auto-Context**: `--auto-context` flag on 7 commands for intelligent context gathering
  - `ask`, `review`, `debug`, `refactor` (v0.8.0)
  - `git commit`, `generate tests`, `generate docs` (v0.8.1)
- **Git Integration**: Automatically include branch, commits, modified files
- **Dependency Analysis**: Parse imports and include related files
- **Multi-Language Error Parsing** (v0.8.2): Python, JavaScript/TypeScript, Go, Rust, Java
- **Context Summary** (v0.8.2): Preview context before API calls with `cdc context summary`
- **Smart Truncation**: Prevent token limits with configurable file size limits
- **Project Memory**: Remember preferences per project
- **Global Config**: Set context defaults in `~/.claude-dev-cli/config.json`

### 🎒 TOON Format Support (Optional)
- **Token Reduction**: 30-60% fewer tokens than JSON
- **Cost Savings**: Reduce API costs significantly
- **Format Conversion**: JSON ↔ TOON with CLI tools
- **Auto-fallback**: Works without TOON installed

## Installation

### Via Homebrew (macOS/Linux)

```bash
# Add the tap
brew tap thinmanj/tap

# Install
brew install claude-dev-cli

# Or in one command
brew install thinmanj/tap/claude-dev-cli
```

### Via pip

```bash
# Basic installation
pip install claude-dev-cli

# With TOON support (30-60% token reduction)
pip install claude-dev-cli[toon]
```

### Via pipx (Recommended for CLI tools)

```bash
# Isolated installation
pipx install claude-dev-cli

# With TOON support
pipx install claude-dev-cli[toon]
```

## Quick Start

### 1. Set Up API Keys

```bash
# Add your personal API key
export PERSONAL_ANTHROPIC_API_KEY="sk-ant-..."
cdc config add personal --default --description "My personal API key"
# 🔐 Stored securely in system keyring

# Add client's API key
export CLIENT_ANTHROPIC_API_KEY="sk-ant-..."
cdc config add client --description "Client's Enterprise API"

# List configured APIs (shows storage method)
cdc config list

# Manually migrate existing keys (automatic on first run)
cdc config migrate-keys
```

### 2. Basic Usage

```bash
# Ask a question
cdc ask "explain asyncio in Python"

# With file context
cdc ask -f mycode.py "review this code"

# Pipe input
cat error.log | cdc ask "what's causing this error?"

# Interactive mode
cdc interactive

# Use specific API
cdc ask -a client "generate tests for this function"
```

### 3. Developer Commands

```bash
# Generate tests
cdc generate tests mymodule.py -o tests/test_mymodule.py

# Generate tests with interactive refinement
cdc generate tests mymodule.py --interactive

# Generate tests with context (includes dependencies, related files) - NEW in v0.8.1
cdc generate tests mymodule.py --auto-context

# Code review
cdc review mymodule.py

# Code review with auto-context (includes git, dependencies, tests)
cdc review mymodule.py --auto-context

# Code review with interactive follow-up questions
cdc review mymodule.py --interactive

# Debug errors with intelligent error parsing
python script.py 2>&1 | cdc debug --auto-context

# Generate documentation
cdc generate docs mymodule.py

# Generate docs with interactive refinement
cdc generate docs mymodule.py --interactive

# Generate docs with context (includes dependencies) - NEW in v0.8.1  
cdc generate docs mymodule.py --auto-context

# Refactor with context (includes related files)
cdc refactor legacy_code.py --auto-context

# Refactor with interactive refinement
cdc refactor legacy_code.py --interactive

# Git commit message
git add .
cdc git commit

# Git commit message with context (includes history, branch) - NEW in v0.8.1
git add .
cdc git commit --auto-context
```

### 4. Context-Aware Operations (v0.8.0+)

```bash
# Auto-context includes: git info, dependencies, related files

# Review with full project context
cdc review mymodule.py --auto-context
# ✓ Context gathered (git, dependencies, tests)

# Debug with parsed error details (multi-language support)
python broken.py 2>&1 | cdc debug -f broken.py --auto-context
node app.js 2>&1 | cdc debug --auto-context  # JavaScript/TypeScript
go run main.go 2>&1 | cdc debug --auto-context  # Go
# ✓ Context gathered (error details, git context)
# Supports: Python, JavaScript, TypeScript, Go, Rust, Java

# Preview context before making API calls - NEW in v0.8.2
cdc context summary mymodule.py
# Shows: files, sizes, lines, estimated tokens, truncation warnings

# Ask questions with file context
cdc ask -f mycode.py --auto-context "how can I improve this?"
# ✓ Context gathered

# Refactor with related files
cdc refactor app.py --auto-context
# Automatically includes imported modules and dependencies
```

### 5. Custom Templates

```bash
# List all templates (built-in and user)
cdc template list

# Show template details
cdc template show code-review

# Add a custom template
cdc template add my-review -c "Review this code for {{focus}}: {{code}}" \
  -d "Custom review template" --category review

# Use a template (interactive variable input)
cdc template use debug-error

# Delete a user template
cdc template delete my-review

# Filter by category
cdc template list --category review

# Show only user templates
cdc template list --user
```

#### Built-in Templates

- **code-review**: Comprehensive code review with customizable focus
- **code-review-security**: Security-focused code review
- **test-strategy**: Generate testing strategy and test cases
- **debug-error**: Debug error with context
- **optimize-performance**: Performance optimization analysis
- **refactor-clean**: Clean code refactoring
- **explain-code**: Detailed code explanation
- **api-design**: API design assistance

### 6. Conversation History & Summarization (NEW in v0.8.3)

```bash
# List recent conversations
cdc history list

# Search conversations
cdc history list --search "python decorators"

# Export conversation
cdc history export 20240109_143022 -o chat.md

# Summarize to reduce token usage
cdc history summarize --latest
cdc history summarize 20240109_143022 --keep-recent 6

# Delete old conversations
cdc history delete 20240109_143022
```

**Auto-Summarization** in interactive mode:
- Automatically triggers when conversation exceeds 8,000 tokens
- Keeps recent messages (default: 4 pairs), summarizes older ones
- Reduces API costs by ~30-50% in long conversations
- Shows token savings after summarization

### 7. Usage Tracking

```bash
# View all usage
cdc usage

# Last 7 days
cdc usage --days 7

# Filter by API
cdc usage --api client
```

### 7. TOON Format (Optional - Reduces Tokens by 30-60%)

```bash
# Check if TOON is installed
cdc toon info

# Convert JSON to TOON
echo '{"users": [{"id": 1, "name": "Alice"}]}' | cdc toon encode
# Output:
# users[1]{id,name}:
# 1,Alice

# Convert file
cdc toon encode data.json -o data.toon

# Convert TOON back to JSON
cdc toon decode data.toon -o data.json

# Use in workflows
cat large_data.json | cdc toon encode | cdc ask "analyze this data"
```

## Configuration

### Secure API Key Storage

**🔐 Your API keys are stored securely and never in plain text.**

- **macOS**: Keychain
- **Linux**: Secret Service API (GNOME Keyring, KWallet)
- **Windows**: Windows Credential Locker
- **Fallback**: Encrypted file (if keyring unavailable)

Keys are automatically migrated from plaintext on first run. You can also manually migrate:

```bash
cdc config migrate-keys
```

### Global Configuration

Configuration metadata is stored in `~/.claude-dev-cli/config.json` (API keys are NOT in this file):

```json
{
  "api_configs": [
    {
      "name": "personal",
      "api_key": "",  // Empty - actual key in secure storage
      "description": "My personal API key",
      "default": true
    },
    {
      "name": "client",
      "api_key": "",  // Empty - actual key in secure storage
      "description": "Client's Enterprise API",
      "default": false
    }
  ],
  "default_model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096
}
```

### Project-Specific Configuration

Create `.claude-dev-cli` in your project root:

```json
{
  "name": "My Project",
  "api_config": "client",
  "system_prompt": "You are a Python expert focused on data science.",
  "allowed_commands": ["all"]
}
```

The tool will automatically use the client's API when you run commands in that project!

## API Routing Strategy

### Scenario: Client Work with Enterprise API

```bash
# 1. Set up client's API
export CLIENT_ANTHROPIC_API_KEY="sk-ant-..."
cdc config add client --description "Client Enterprise API"

# 2. Create project config
cd /path/to/client/project
cat > .claude-dev-cli << 'EOF'
{
  "name": "Client Project",
  "api_config": "client",
  "system_prompt": "You are a senior Python developer."
}
EOF

# 3. All commands in this directory now use client's API
cdc generate tests app.py  # Uses client's API
cdc review code.py         # Uses client's API

# 4. Your personal projects use your API
cd ~/my-personal-project
cdc generate tests app.py  # Uses your personal API
```

## What the Client Can See

When using a client's Enterprise API:

✅ **They CAN see:**
- Total API calls and token usage
- Costs associated with the API key
- Potentially conversation history (if enabled by admin)

❌ **They CANNOT see:**
- Which machine you used
- Your other API keys or projects
- Local files unless you sent the content

## Command Reference

### Core Commands

| Command | Description |
|---------|-------------|
| `cdc ask <prompt>` | Ask Claude a question |
| `cdc interactive` | Start interactive chat |
| `cdc usage` | Show usage statistics |

### Configuration

| Command | Description |
|---------|-------------|
| `cdc config add <name>` | Add API configuration |
| `cdc config list` | List all API configs |

### Code Generation

| Command | Description |
|---------|-------------|
| `cdc generate tests <file>` | Generate pytest tests |
| `cdc generate docs <file>` | Generate documentation |

### Code Analysis

| Command | Description |
|---------|-------------|
| `cdc review <file>` | Review code |
| `cdc debug -f <file> -e <error>` | Debug code |
| `cdc refactor <file>` | Refactoring suggestions |

### Templates

| Command | Description |
|---------|-------------|
| `cdc template list` | List all templates |
| `cdc template show <name>` | Show template details |
| `cdc template add <name>` | Add new template |
| `cdc template delete <name>` | Delete user template |
| `cdc template use <name>` | Use template interactively |

### Git Helpers

| Command | Description |
|---------|-------------|
| `cdc git commit` | Generate commit message |

## Options

### Common Options

- `-a, --api <name>`: Use specific API config
- `-m, --model <name>`: Use specific Claude model
- `-s, --system <prompt>`: Set system prompt
- `-f, --file <path>`: Include file in prompt
- `-o, --output <path>`: Save output to file

### Models

- `claude-3-5-sonnet-20241022` (default)
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

## Examples

### Test Generation

```bash
# Generate tests for a module
cdc generate tests src/calculator.py -o tests/test_calculator.py

# Review the tests
cdc review tests/test_calculator.py
```

### Code Review Workflow

```bash
# Review before committing
cdc review mycode.py

# Fix issues, then generate commit message
git add mycode.py
cdc git commit
```

### Debugging

```bash
# Run script and analyze errors
python buggy_script.py 2>&1 | cdc debug

# Or debug a specific file
cdc debug -f buggy_script.py -e "NameError: name 'x' is not defined"
```

### Using Multiple APIs

```bash
# Personal work
cdc ask "explain decorators" -a personal

# Client work
cdc generate tests client_code.py -a client

# Check usage per API
cdc usage --api personal
cdc usage --api client
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `{NAME}_ANTHROPIC_API_KEY` | API key for config named "name" |
| `ANTHROPIC_API_KEY` | Default API key |

## Usage Log Format

Usage logs are stored in `~/.claude-dev-cli/usage.jsonl`:

```json
{
  "timestamp": "2024-12-28T03:00:00.000000",
  "api_config": "client",
  "model": "claude-3-5-sonnet-20241022",
  "prompt_preview": "Generate tests for...",
  "input_tokens": 1523,
  "output_tokens": 2847,
  "duration_ms": 3421
}
```

## Development

```bash
# Clone the repository
git clone https://github.com/thinmanj/claude-dev-cli
cd claude-dev-cli

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Julio ([@thinmanj](https://github.com/thinmanj))

## Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com/)
- CLI powered by [Click](https://click.palletsprojects.com/)
- Beautiful terminal output with [Rich](https://rich.readthedocs.io/)

## Support

- 🐛 [Report bugs](https://github.com/thinmanj/claude-dev-cli/issues)
- 💡 [Request features](https://github.com/thinmanj/claude-dev-cli/issues)
- 📖 [Documentation](https://github.com/thinmanj/claude-dev-cli)
