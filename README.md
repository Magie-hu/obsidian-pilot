# Obsidian Pilot

> Your First Obsidian Assistant - Bidirectional bridge between LLM-Wiki and Obsidian

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/obsidian-pilot/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/obsidian-pilot/actions)

## Overview

Obsidian Pilot is a bidirectional bridge between [Karpathy's LLM-Wiki](https://github.com/karpathy/llm-wiki) and Obsidian. It helps developers and Obsidian power users organize their AI knowledge base automatically.

**Perfect for:**
- Developers using Hermes/Codex for local AI knowledge bases
- Obsidian double-link power users who want AI to auto-organize notes

## Features

- **LLM-Wiki Standard** — Auto-initialize `raw/`, `wiki/`, `attachments/`, `scripts/` directories
- **Note Import & Classification** — Auto-classify notes into raw/wiki/attachment/script
- **Bidirectional Links** — Generate `[[double-links]]` between related wiki entries
- **Template Engine** — LLM-Wiki compatible templates for raw materials and wiki entries
- **Smart Routing** — Route queries to local knowledge or AI assistants

## Installation

### From Source

```bash
git clone https://github.com/yourusername/obsidian-pilot.git
cd obsidian-pilot
pip install -e .
```

## Quick Start

```bash
# Initialize LLM-Wiki standard vault
obsidian-pilot init /path/to/vault -t llm-wiki

# Import and classify notes
obsidian-pilot import /path/to/vault --dry-run

# Apply changes
obsidian-pilot import /path/to/vault --apply

# Automate links
obsidian-pilot link /path/to/vault --apply
```

## Directory Structure

```
your-vault/
├── raw/              # Raw materials awaiting AI processing
├── wiki/             # Processed wiki entries with [[double-links]]
├── attachments/      # Media and file attachments
├── scripts/          # Automation scripts
├── 00-Index.md       # Master index page
└── _templates/       # LLM-Wiki templates
    ├── raw-material.md
    ├── wiki-entry.md
    └── index.md
```

## Templates

### Raw Material Template
For imported documents awaiting processing:
```markdown
---
tags: [raw, imported]
date: {{date}}
source: {{source}}
status: pending
---

# {{title}}

> Raw material from {{source}}, awaiting processing

## Content

{{content}}
```

### Wiki Entry Template
Karpathy LLM-Wiki standard format:
```markdown
---
tags: [wiki, entry]
date: {{date}}
aliases: [{{aliases}}]
related: [{{related}}]
status: published
---

# {{title}}

## Summary

> One-sentence summary of this concept

## Core Concepts

- Concept 1
- Concept 2

## Details

{{content}}

## Related

- [[ ]]
- [[ ]]

## References

- 
```

## Roadmap

- [x] Phase 1: LLM-Wiki vault initialization
- [x] Phase 2: Note import & classification
- [x] Phase 3: Link automation
- [x] Phase 4: AI routing
- [x] Phase 5: Daily maintenance
- [ ] Obsidian plugin version
- [ ] Desktop GUI
- [ ] Cloud sync support

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the Obsidian and LLM-Wiki communities
- Inspired by Karpathy's LLM-Wiki standard
- Special thanks to all contributors
