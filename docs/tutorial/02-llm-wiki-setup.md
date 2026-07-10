# LLM-Wiki Standard Vault Setup

## Karpathy LLM-Wiki Standard

LLM-Wiki is a standardized local knowledge base structure designed for AI assistants:

```
vault/
├── raw/       # Raw materials
├── wiki/      # Structured entries
├── attachments/  # Attachments
└── scripts/   # Automation scripts
```

## Initialize with Obsidian Pilot

```bash
obsidian-pilot init /path/to/vault -t llm-wiki
```

## Template Descriptions

### Raw Material Template
For importing raw documents awaiting AI processing.

### Wiki Entry Template
Karpathy standard format with Summary, Core Concepts, Details, Related, References.

## Best Practices

1. Place raw materials in `raw/`
2. Move processed content to `wiki/`
3. Use `[[double-links]]` to establish connections
4. Regularly check index page `00-Index.md`
