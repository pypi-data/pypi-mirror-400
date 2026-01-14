# prompt-cheater

[![PyPI version](https://badge.fury.io/py/prompt-cheater.svg)](https://pypi.org/project/prompt-cheater/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert natural language to Claude-friendly XML prompts and inject into Tmux.

## Overview

prompt-cheater is a CLI tool designed for developers who use Claude Code in a Tmux environment. It transforms your natural language instructions into structured XML prompts using Gemini AI, then automatically sends them to a Claude Code session running in another Tmux pane.

## Features

- Natural language to XML prompt conversion via Gemini 1.5 Flash
- Automatic Tmux pane discovery and text injection
- Beautiful TUI with Rich library
- Preview mode for generated prompts
- Dry-run mode for testing
- Korean (CJK) character support with proper backspace handling

## Installation

### pip (Recommended)

```bash
pip install prompt-cheater
```

### pipx (Isolated environment)

```bash
pipx install prompt-cheater
```

### Homebrew (macOS)

```bash
brew tap KIMGYUDONG/prompt-cheater
brew install prompt-cheater
```

### From source

```bash
git clone https://github.com/KIMGYUDONG/prompt-cheater.git
cd prompt-cheater
pip install -e .
```

## Configuration

Set your Gemini API key:

```bash
# Option 1: Environment variable
export GEMINI_API_KEY="your_api_key_here"

# Option 2: .env file
echo 'GEMINI_API_KEY=your_api_key_here' > .env
```

Get your API key from: https://aistudio.google.com/apikey

## Usage

Run from within a Tmux session with at least 2 panes:

```bash
# Basic usage (single-line input, press Enter to send)
cheater

# Multiline input mode (press Enter twice to send)
cheater -m

# Preview generated XML before sending
cheater -p

# Dry run (don't send to Tmux)
cheater -n

# Combine options
cheater -m -p

# Show version
cheater -v
```

## Requirements

- Python 3.10+
- Tmux
- Gemini API key
- macOS or Linux

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
