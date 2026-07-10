# Hermes MEMORY.md Configuration

## What is MEMORY.md

MEMORY.md is Hermes Agent's persistent memory file, stored in `~/.hermes/memory/` directory.

## Setup Steps

1. Create `~/.hermes/memory/MEMORY.md`
2. Add user preferences, project info, common commands
3. Restart Hermes Agent to apply

## Template

```markdown
# User Memory

## Preferences
- Language: English (primary), Chinese (secondary)
- Style: Concise and practical

## Projects
- Obsidian Pilot: LLM-Wiki ↔ Obsidian bidirectional bridge

## Common Commands
- obsidian-pilot init: Initialize knowledge base
- obsidian-pilot import: Import notes
```

## Best Practices

- Keep it concise, only record persistent information
- Group by topic
- Clean up outdated content regularly
