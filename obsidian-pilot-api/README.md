# Obsidian Pilot API

> FastAPI backend for LLM-Wiki bridge — automated note classification, link analysis, and AI routing for Obsidian vaults.

## Installation

```bash
pip install -e .
```

Or with a virtual environment:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Running

```bash
# CLI entry
obsidian-pilot-api

# Or directly
python -m obsidian_pilot_api.main
```

Server runs at `http://127.0.0.1:8080`

### Configuration (Environment Variables)

| Variable | Default | Description |
|---|---|---|
| `OBSIDIAN_PILOT_API_HOST` | `0.0.0.0` | Bind address |
| `OBSIDIAN_PILOT_API_PORT` | `8080` | Bind port |
| `OBSIDIAN_PILOT_API_LOG_LEVEL` | `info` | Logging level |
| `OBSIDIAN_PILOT_API_DEFAULT_VAULT_PATH` | *(empty)* | Default vault path |
| `OBSIDIAN_PILOT_API_CORS_ORIGINS` | `*` | CORS allowed origins |
| `OBSIDIAN_PILOT_API_DEFAULT_PAGE_SIZE` | `50` | Default pagination size |
| `OBSIDIAN_PILOT_API_MAX_PAGE_SIZE` | `200` | Max pagination size |

## API Endpoints

### Status

- `GET /` — Service info
- `GET /health` — Health check

### Vault Management

- `POST /init` — Initialize a new LLM-Wiki vault (creates folders, templates, index)
- `POST /import` — Scan and classify all notes (paginated)
- `POST /import/apply` — Apply classification changes to notes

### Link Analysis

- `POST /links/report` — Get link analysis report (paginated)
- `POST /links/apply` — Apply suggested wiki-link updates

### AI Routing

- `POST /route` — Route a query to local knowledge or recommend an AI assistant

### Maintenance

- `POST /maintain` — Run daily maintenance (expired, duplicates, orphaned links)

## Pagination

All list endpoints support pagination via query parameters:

```
POST /import?page=1&page_size=20
POST /links/report?page=1&page_size=50
POST /maintain?page=1&page_size=50
```

Response includes `total`, `page`, `page_size`, and `items`.

## Swagger UI

Interactive API docs at: http://127.0.0.1:8080/docs

## Architecture

```
obsidian-pilot-api/ (this directory)
    └── imports from ../src/ (core)
            ├── init.py      — folder/template/index creation
            ├── note_import.py — note scanning & classification
            ├── link.py       — link extraction & analysis
            ├── route.py      — local knowledge & AI routing
            └── maintain.py   — expiry, duplicates, archiving
```

The API is a thin FastAPI layer over the core Python modules. It adds:
- HTTP interface for the Obsidian plugin to call
- Input validation via Pydantic models
- Structured logging
- CORS for cross-origin plugin requests
- Pagination for large vaults

## License

MIT — Copyright (c) 2026 NingXiaoBan
