# OpenClaw Amazon Bot 🛒🤖

AI-powered browser automation for Amazon shopping using [OpenClaw](https://github.com/openclaw/openclaw) and Google Gemini.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🧠 **AI-Powered** - Uses Gemini AI for intelligent browser navigation
- 🌍 **Multi-Region** - Supports Amazon NL, DE, FR, ES, IT, UK, US
- 🧪 **Dry Run Mode** - Test without making real purchases
- 💰 **Budget Control** - Strict price limit enforcement
- ⭐ **Quality Filters** - Minimum rating requirements
- 🔒 **Safety First** - Stops on 2FA, CAPTCHA, or budget exceeded

## Quick Start

```bash
# Install dependencies
uv sync

# Run in dry-run mode (no purchase)
uv run amazon-bot run --dry-run

# Run with live purchase
uv run amazon-bot run --yes
```

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** - Fast Python package manager
- **Node.js 22+** - For OpenClaw
- **[OpenClaw](https://github.com/openclaw/openclaw)** - AI assistant platform

## Installation

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install OpenClaw

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### 3. Setup project

```bash
uv sync
```

### 4. Configure credentials

Create a `.env` file:

```env
AMAZON_NL_USERNAME=your@email.com
AMAZON_NL_PASSWORD=your-password
GOOGLE_API_KEY=your-gemini-api-key
```

## Usage

### Commands

```bash
# Show help
uv run amazon-bot --help

# Run with dry-run (default: pencil sharpener, €10, Amazon.nl)
uv run amazon-bot run --dry-run

# Run with custom product
uv run amazon-bot run --dry-run --product "mechanical keyboard" --max-price 50

# Run on different region
uv run amazon-bot run --dry-run --region de

# Run in headless mode
uv run amazon-bot run --dry-run --headless

# Live purchase (with confirmation)
uv run amazon-bot run

# Live purchase (skip confirmation)
uv run amazon-bot run --yes

# Check prerequisites
uv run amazon-bot check

# Show configuration
uv run amazon-bot config
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--dry-run` | `-d` | Test without purchasing | `False` |
| `--product` | `-p` | Product to search for | `pencil sharpener` |
| `--max-price` | `-m` | Maximum price in EUR | `10.00` |
| `--region` | `-r` | Amazon region (nl/de/fr/es/it/uk/us) | `nl` |
| `--headless` | | Run browser invisibly | `False` |
| `--skip-checks` | | Skip pre-flight checks | `False` |
| `--yes` | `-y` | Skip confirmation prompt | `False` |

### Supported Regions

| Region | URL | Language |
|--------|-----|----------|
| `nl` 🇳🇱 | amazon.nl | Dutch/English |
| `de` 🇩🇪 | amazon.de | German |
| `fr` 🇫🇷 | amazon.fr | French |
| `es` 🇪🇸 | amazon.es | Spanish |
| `it` 🇮🇹 | amazon.it | Italian |
| `uk` 🇬🇧 | amazon.co.uk | English |
| `us` 🇺🇸 | amazon.com | English |

## Project Structure

```
openclaw-amazon-bot/
├── .env                    # Credentials (git-ignored)
├── .gitignore
├── pyproject.toml          # Python project configuration
├── openclaw.json           # OpenClaw configuration (auto-generated)
├── README.md
├── src/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI application
│   ├── config.py           # Pydantic settings management
│   └── openclaw.py         # OpenClaw integration
├── skills/
│   └── amazon-shopper/
│       └── SKILL.md        # AI skill instructions
├── workspace/
│   └── AGENTS.md           # Agent behavior configuration
└── tests/
    └── ...
```

## How It Works

```
┌─────────────────┐
│   CLI (Typer)   │  ← User runs: amazon-bot run --dry-run
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Config (Pydantic)│  ← Validates settings from .env
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ OpenClaw Agent  │  ← Builds task message with instructions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Gemini AI     │  ← Interprets task and controls browser
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Browser (CDP)   │  ← Automates Amazon website
└─────────────────┘
```

## Safety Features

### Budget Protection
- Total cost (item + shipping) must be under specified limit
- Bot stops immediately if budget would be exceeded
- Price verified at multiple stages

### Dry Run Mode
- Full workflow testing without purchase
- Reports what would be bought
- No payment processed

### Security Handling
- Pauses on 2FA/MFA requests
- Stops on CAPTCHA challenges
- Reports unusual security prompts

## Troubleshooting

### OpenClaw not found

```bash
npm install -g openclaw@latest
```

### Gateway issues

```bash
openclaw doctor
openclaw gateway --status
```

### Browser problems

```bash
openclaw agent --message "Open browser and go to google.com"
```

### Configuration errors

```bash
# Verify settings
uv run amazon-bot config

# Check .env file exists
cat .env
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AMAZON_NL_USERNAME` | Yes | Amazon account email |
| `AMAZON_NL_PASSWORD` | Yes | Amazon account password |
| `GOOGLE_API_KEY` | Yes | Google Gemini API key |
| `MAX_PRICE_EUR` | No | Default maximum price |
| `PRODUCT_SEARCH` | No | Default product to search |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Linting
uv run ruff check src/
```

## License

MIT License

## Disclaimer

⚠️ **Use at your own risk.** This bot can make real purchases on your Amazon account. Always:

- Test with `--dry-run` first
- Review the order before confirming
- Set appropriate budget limits
- Monitor the bot during execution
