# Obsidian Pilot API

> FastAPI backend for LLM-Wiki ↔ Obsidian bridge

## Installation

```bash
pip install -e .
```

## Running

```bash
python -m obsidian_pilot_api.main
# or
obsidian-pilot-api
```

Server runs at http://127.0.0.1:8080

## API Endpoints

- `GET /` — Health check
- `POST /init` — Initialize vault
- `POST /import` — Import notes
- `POST /link` — Automate links
- `POST /route` — AI routing
- `POST /maintain` — Daily maintenance

## Docs

Swagger UI: http://127.0.0.1:8080/docs
