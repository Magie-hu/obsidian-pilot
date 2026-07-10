# Obsidian Pilot

> Your First Obsidian Assistant - Bidirectional bridge between LLM-Wiki and Obsidian

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/obsidian-pilot/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/obsidian-pilot/actions)

## Overview

Obsidian Pilot is a lightweight, modular toolkit designed to bridge the gap between
LLM-Wiki (Karpathy's LLM knowledge base standard) and Obsidian, making it easy to
build, maintain, and leverage AI-ready knowledge bases.

## Features

- **One-click Vault Initialization** — LLM-Wiki standard folder structure
- **Smart Note Classification** — Auto-categorize notes by content and tags
- **Bidirectional Link Automation** — Find missing links, detect isolated notes
- **AI Assistant Routing** — Route queries to the right AI model based on content
- **Vault Maintenance** — Find expired, duplicate, and orphaned notes
- **Interactive Wizard** — Step-by-step guided setup for new users
- **Extensible Plugin Architecture** — Easy to add new modules

## Quick Start

```bash
# Install
pip install obsidian-pilot

# Initialize a new vault
obsidian-pilot init /path/to/vault

# Classify notes
obsidian-pilot import /path/to/vault

# Automate links
obsidian-pilot link /path/to/vault

# Route a query
obsidian-pilot route "How do I set up a new vault?"
```

## Architecture

```
obsidian-pilot/
├── src/
│   ├── init.py          # Vault initialization
│   ├── note_import.py   # Note classification & import
│   ├── link.py          # Link automation
│   ├── route.py         # AI routing
│   ├── maintain.py      # Vault maintenance
│   ├── main.py          # CLI entry point
│   └── wizard.py        # Interactive setup
├── tests/
│   ├── test_init.py
│   ├── test_import.py
│   ├── test_link.py
│   ├── test_route.py
│   └── test_maintain.py
├── pyproject.toml
└── README.md
```

## Installation

```bash
# From PyPI (when published)
pip install obsidian-pilot

# From source
git clone https://github.com/Magie-hu/obsidian-pilot.git
cd obsidian-pilot
pip install -e .
```

## Requirements

- Python 3.11+
- No heavy dependencies (uses only standard library + argparse)
- Works on Windows, macOS, and Linux

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Inspired by Andrej Karpathy's [LLM-Wiki](https://github.com/karpathy/llm-wiki) standard
- Built for the Obsidian and LLM-Wiki communities
- Special thanks to all contributors
