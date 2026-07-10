# Obsidian LLM-Wiki Plugin

> Obsidian community plugin for LLM-Wiki ↔ Obsidian bidirectional bridge

## Installation

1. Open Obsidian Settings → Community Plugins → Browse
2. Search "LLM-Wiki Bridge"
3. Install and Enable

**Or manual install:**
1. Download `main.js`, `manifest.json`, `styles.css`
2. Place in `.obsidian/plugins/obsidian-llm-wiki/`
3. Enable in Settings

## Requirements

- Obsidian 1.5.0+
- Python 3.11+ (for backend API)
- Local API service running at `http://127.0.0.1:8080`

## Setup Backend

```bash
pip install obsidian-pilot-api
obsidian-pilot-api
```

## Usage

1. Click the book icon in sidebar
2. Enter vault path
3. Click buttons to operate

## Commands

- **Initialize Vault** — Create LLM-Wiki standard structure
- **Import Notes** — Scan and classify notes
- **Auto Links** — Generate wiki-links
- **Daily Maintenance** — Check expired/duplicate notes

## License

MIT
