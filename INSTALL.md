# Installation Guide

## Quick Start (3 steps)

### Step 1: Install API Backend

```bash
pip install obsidian-pilot-api
```

Or install from source:

```bash
cd obsidian-pilot-api
pip install -e .
```

### Step 2: Start the API Server

```bash
obsidian-pilot-api --port 8080
```

Or:

```bash
uvicorn obsidian_pilot_api.main:app --port 8080
```

### Step 3: Install the Plugin

1. Open Obsidian
2. Go to Settings → Third-party plugins
3. Click "Browse"
4. Search for "Pilot Assistant"
5. Click Install → Enable

## Manual Installation (if not in community store)

1. Download the latest release zip from GitHub
2. Extract to `.obsidian/plugins/obsidian-pilot/` in your vault
3. Enable the plugin in settings

## CLI Usage

```bash
# Initialize a vault
obsidian-pilot init /path/to/vault

# Import and classify notes
obsidian-pilot import /path/to/vault

# Analyze links
obsidian-pilot link /path/to/vault

# Get AI routing advice
obsidian-pilot route "What's the weather today?"

# Run maintenance
obsidian-pilot maintain /path/to/vault
```

## Requirements

- Obsidian Desktop 1.6.0+
- Python 3.10+ (for API backend)

## Troubleshooting

**Plugin says "API not connected"**
- Make sure the API server is running: `obsidian-pilot-api --port 8080`
- Check that the plugin's API URL matches: `http://localhost:8080`

**Import fails with "Template not found"**
- Use `obsidian-pilot init /path/to/vault -t llm-wiki`

**Links not working**
- Ensure all notes have proper frontmatter with `title:` field