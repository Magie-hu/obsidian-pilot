# Pilot Assistant

> Initialize vaults, classify notes, automate links, and more. Your first Obsidian assistant.

## What is this?

Pilot Assistant is a complete toolkit for Obsidian knowledge management:

- **CLI** — `obsidian-pilot init/import/link/route/maintain`
- **API** — FastAPI backend at `obsidian-pilot-api/`
- **Plugin** — Obsidian community plugin at `obsidian-llm-wiki-plugin/`

## Quick Start

```bash
# 1. Install CLI
pip install -e obsidian-pilot-api/

# 2. Initialize a vault
obsidian-pilot init /path/to/vault -t llm-wiki

# 3. Start API server
cd obsidian-pilot-api
uvicorn obsidian_pilot_api.main:app --port 8080

# 4. Install plugin in Obsidian
# Download from: https://github.com/Magie-hu/obsidian-pilot/releases
```

## Features

| Feature | CLI Command | API Endpoint | Description |
|---------|------------|--------------|-------------|
| Init Vault | `obsidian-pilot init` | `POST /init` | Create LLM-Wiki structure |
| Import | `obsidian-pilot import` | `POST /import` | Scan and classify notes |
| Links | `obsidian-pilot link` | `POST /links/report` | Auto-link analysis |
| Route | `obsidian-pilot route` | `POST /route` | AI model recommendation |
| Maintain | `obsidian-pilot maintain` | `POST /maintain` | Expired/duplicate/orphan check |

## Architecture

```
obsidian-pilot/
├── src/                    # CLI core (init, import, link, route, maintain)
├── obsidian-pilot-api/     # FastAPI backend + CLI entry point
│   ├── obsidian_pilot_api/ # API server
│   └── obsidian_pilot_cli/ # CLI unified entry
├── obsidian-llm-wiki-plugin/ # Obsidian plugin source
└── obsidian-pilot-api/     # Built plugin dist
```

## License

MIT License - Copyright (c) 2026 NingXiaoBan
