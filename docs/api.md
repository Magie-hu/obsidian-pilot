# API Documentation

Base URL: `http://localhost:8080`

## Endpoints

### POST /init

Initialize a vault with LLM-Wiki structure.

**Request:**
```json
{
  "vault_path": "/path/to/vault",
  "template_name": "llm-wiki"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Vault initialized...",
  "folders_created": 8,
  "templates_created": 1
}
```

### POST /import

Scan and classify all notes.

**Request:**
```json
{
  "vault_path": "/path/to/vault"
}
```

**Response:**
```json
{
  "total_notes": 150,
  "category_counts": {"tech": 45, "personal": 30, ...},
  "uncategorized": ["note1.md", ...],
  "results": [{"file": "...", "title": "...", "category": "tech", ...}]
}
```

### POST /import/apply

Apply classification changes to move notes into folders.

**Request:** Same as /import

**Response:**
```json
{
  "status": "success",
  "updated": 42
}
```

### POST /links/report

Analyze note links.

**Request:**
```json
{
  "vault_path": "/path/to/vault"
}
```

**Response:**
```json
{
  "missing_links": [...],
  "isolated_notes": [...],
  "total_notes": 150
}
```

### POST /links/apply

Apply link suggestions.

**Request:** Same as /links/report

**Response:**
```json
{
  "status": "success",
  "updated": 12
}
```

### POST /route

Recommend an AI model for a query.

**Request:**
```json
{
  "query": "What is machine learning?",
  "vault_path": "/path/to/vault"
}
```

**Response:**
```json
{
  "recommended_model": "seed-2.0-mini",
  "confidence": 0.85,
  "local_knowledge": "..."
}
```

### POST /maintain

Run maintenance checks.

**Request:**
```json
{
  "vault_path": "/path/to/vault",
  "archive": false
}
```

**Response:**
```json
{
  "total_notes": 150,
  "expired_count": 3,
  "duplicate_count": 2,
  "orphaned_count": 5,
  "archived": 0,
  "expired_notes": [...],
  "duplicate_titles": [...],
  "orphaned_links": [...]
}
```

### GET /health

Health check.

**Response:**
```json
{
  "status": "healthy"
}
```

## CLI Alternative

All endpoints can also be called via CLI:

```bash
obsidian-pilot init /path/to/vault -t llm-wiki
obsidian-pilot import /path/to/vault
obsidian-pilot link /path/to/vault
obsidian-pilot route "query here"
obsidian-pilot maintain /path/to/vault
```