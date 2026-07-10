#!/usr/bin/env python3
"""Obsidian Pilot - Phase 1: New User Guide & One-Click Initialization"""
import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import platform

# Platform detection
SYSTEM = platform.system()  # Windows, Darwin, Linux
IS_WINDOWS = SYSTEM == "Windows"
IS_MAC = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"

# Recommended plugins with descriptions
PLUGIN_RECOMMENDATIONS = {
    "dataview": {
        "name": "Dataview",
        "desc": "Query notes with SQL-like syntax, generate tables and lists",
        "install": "Obsidian Settings -> Community Plugins -> Browse -> Search Dataview",
    },
    "templater": {
        "name": "Templater",
        "desc": "Advanced template engine with variable substitution and auto-execution",
        "install": "Obsidian Settings -> Community Plugins -> Browse -> Search Templater",
    },
    "periodic-notes": {
        "name": "Periodic Notes",
        "desc": "Auto-create daily/weekly/monthly notes, great for daily digests",
        "install": "Obsidian Settings -> Community Plugins -> Browse -> Search Periodic Notes",
    },
    "calendar": {
        "name": "Calendar",
        "desc": "Calendar view to browse notes by date",
        "install": "Obsidian Settings -> Community Plugins -> Browse -> Search Calendar",
    },
    "obsidian-git": {
        "name": "Obsidian Git",
        "desc": "Auto-backup notes to GitHub/GitLab",
        "install": "Obsidian Settings -> Community Plugins -> Browse -> Search Obsidian Git",
    },
    "meta-bind": {
        "name": "Meta Bind",
        "desc": "Visual editor for frontmatter, no YAML needed",
        "install": "Obsidian Settings -> Community Plugins -> Browse -> Search Meta Bind",
    },
}

# Folder templates
FOLDER_TEMPLATES = {
    "llm-wiki": {
        "name": "LLM-Wiki Standard",
        "folders": [
            "raw",
            "wiki",
            "attachments",
            "scripts",
            "00-Index",
            "_templates",
        ],
        "description": "Karpathy LLM-Wiki standard structure for AI knowledge base",
    },
    "minimal": {
        "name": "Minimal",
        "folders": [
            "Inbox",
            "Projects",
            "Archive",
        ],
        "description": "For beginners: start simple, grow later",
    },
}


def create_folder_structure(vault_path, template_name):
    """Create folder structure based on selected template."""
    vault = Path(vault_path).resolve()
    template = FOLDER_TEMPLATES[template_name]
    
    print(f"\nCreating folder structure: {template['name']}")
    print(f"Description: {template['description']}")
    
    for folder in template["folders"]:
        folder_path = vault / folder
        folder_path.mkdir(exist_ok=True)
        print(f"  OK {folder}/")
    
    return vault


def create_templates(vault_path):
    """Create LLM-Wiki standard templates for Obsidian."""
    vault = Path(vault_path).resolve()
    templates_dir = vault / "_templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Raw material template (for imported documents)
    raw_tmpl = """---
tags: [raw, imported]
date: {{date}}
source: {{source}}
status: pending
---

# {{title}}

> Raw material from {{source}}, awaiting processing

## Content

{{content}}
"""
    with open(templates_dir / "raw-material.md", "w", encoding="utf-8") as f:
        f.write(raw_tmpl)
    
    # Wiki entry template (Karpathy LLM-Wiki standard)
    wiki_tmpl = """---
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
- Concept 3

## Details

{{content}}

## Related

- [[ ]]
- [[ ]]

## References

- 
"""
    with open(templates_dir / "wiki-entry.md", "w", encoding="utf-8") as f:
        f.write(wiki_tmpl)
    
    # Index template (master index page)
    index_tmpl = """---
tags: [index, meta]
date: {{date}}
status: published
---

# Knowledge Base Index

> Auto-generated index for LLM-Wiki knowledge base

## Directories

- [[raw]] — Raw materials awaiting processing
- [[wiki]] — Processed wiki entries
- [[attachments]] — Media and attachments
- [[scripts]] — Automation scripts

## Recent Updates

```dataview
TABLE WITHOUT ID
file.link AS Note,
file.tags AS Tags,
file.mtime AS Modified
FROM ""
SORT file.mtime DESC
LIMIT 20
```

## Statistics

- Total entries: {{total_entries}}
- Last updated: {{last_updated}}
"""
    with open(templates_dir / "index.md", "w", encoding="utf-8") as f:
        f.write(index_tmpl)
    
    print("\nLLM-Wiki templates created:")
    for tmpl in templates_dir.glob("*.md"):
        print(f"  OK {tmpl.name}")
    
    return templates_dir


def create_index_page(vault_path, template_name="llm-wiki"):
    """Create the main index page for the vault."""
    vault = Path(vault_path).resolve()
    index_file = vault / "000 Index.md"
    
    # Normalize template name
    if template_name in ("default", "mixed"):
        template_name = "llm-wiki"
    
    template = FOLDER_TEMPLATES.get(template_name, FOLDER_TEMPLATES["llm-wiki"])
    
    index_content = f"""# 🏠 {template_name.title()} Vault
> Auto-generated by Obsidian Pilot

## Directory Structure

| Directory | Description |
|-----------|-------------|
| [[raw]] | Raw materials awaiting AI processing |
| [[wiki]] | Processed wiki entries with [[double-links]] |
| [[attachments]] | Media and file attachments |
| [[scripts]] | Automation scripts |
| [[00-Index]] | This index page |

## Quick Links

- [[wiki]] — Browse all wiki entries
- [[raw]] — Pending raw materials
- [[_templates]] — LLM-Wiki templates

## Recent Updates

```dataview
TABLE WITHOUT ID
file.link AS Note,
file.tags AS Tags,
file.mtime AS Modified
FROM ""
SORT file.mtime DESC
LIMIT 20
```

## Recommended Plugins

- [[Dataview]] — Query notes with SQL-like syntax
- [[Templater]] — Advanced template engine with LLM-Wiki support
- [[Obsidian Git]] — Auto-backup to GitHub/GitLab

---
*Generated on {datetime.now().strftime('%Y-%m-%d')} by Obsidian Pilot*
"""
    
    index_path = vault / "00-Index.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)
    
    print(f"\nIndex page created: {index_path.name}")
    return index_path


def recommend_plugins(vault_path):
    """Show plugin recommendations based on template."""
    vault = Path(vault_path).resolve()
    
    print("\n" + "=" * 50)
    print("Recommended Plugins")
    print("=" * 50)
    
    for key, plugin in PLUGIN_RECOMMENDATIONS.items():
        print(f"\n  {plugin['name']}")
        print(f"    Purpose: {plugin['desc']}")
        print(f"    Install: {plugin['install']}")
    
    print("\n" + "=" * 50)
    print("Tip: Start with Dataview and Templater, others as needed")
    print("=" * 50)


def show_welcome():
    """Display welcome message and instructions."""
    print("\n" + "=" * 60)
    print("Welcome to Obsidian Pilot")
    print("=" * 60)
    print("\nObsidian Pilot is your first Obsidian assistant,")
    print("helping you build an organized knowledge base from scratch.")
    print("\nFeatures:")
    print("  1. One-click initialization (folders + templates + index)")
    print("  2. Note import and auto-classification")
    print("  3. Link automation and index maintenance")
    print("  4. AI assistant smart routing")
    print("  5. Daily maintenance and expiry alerts")
    print("\nVersion: Phase 1 - New User Guide")
    print("=" * 60)


def show_plugin_guide():
    """Show detailed plugin installation guide."""
    print("\n" + "=" * 50)
    print("Plugin Installation Guide")
    print("=" * 50)
    
    for key, plugin in PLUGIN_RECOMMENDATIONS.items():
        print(f"\n{'-' * 40}")
        print(f"  {plugin['name']}")
        print(f"{'-' * 40}")
        print(f"Purpose: {plugin['desc']}")
        print(f"Install: {plugin['install']}")
        print(f"Config:")
        
        if key == "dataview":
            print(f"  1. Enable Dataview plugin")
            print(f"  2. Use dataview syntax in notes")
            print(f"  3. Example: {{#dataview LIST FROM \"Daily Digest\"}}")
        elif key == "templater":
            print(f"  1. Enable Templater plugin")
            print(f"  2. Set template folder to _templates/")
            print(f"  3. Use {{<% tp.file.title %>}} syntax in notes")
        elif key == "periodic-notes":
            print(f"  1. Enable Periodic Notes plugin")
            print(f"  2. Set daily notes folder to Daily Digest/")
            print(f"  3. Click calendar icon in bottom nav bar")
        elif key == "calendar":
            print(f"  1. Enable Calendar plugin")
            print(f"  2. Click calendar icon in bottom nav bar")
            print(f"  3. Click a date to create a note")
        elif key == "obsidian-git":
            print(f"  1. Enable Obsidian Git plugin")
            print(f"  2. Set Git repo path")
            print(f"  3. Configure backup frequency (hourly recommended)")
        elif key == "meta-bind":
            print(f"  1. Enable Meta Bind plugin")
            print(f"  2. Use meta-bind syntax in frontmatter")
            print(f"  3. Visually edit tags, dates, status fields")
    
    print("\n" + "=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Obsidian Pilot - Your First Obsidian Assistant")
    parser.add_argument("vault_path", help="Path to your Obsidian vault")
    parser.add_argument("--template", "-t", choices=list(FOLDER_TEMPLATES.keys()), default="mixed",
                        help="Folder template to use (default: mixed)")
    parser.add_argument("--recommend-plugins", action="store_true",
                        help="Show plugin recommendations")
    parser.add_argument("--show-plugins", action="store_true",
                        help="Show detailed plugin installation guide")
    parser.add_argument("--init", action="store_true",
                        help="Run initialization (create folders, templates, index)")
    
    args = parser.parse_args()
    
    # Show welcome
    show_welcome()
    
    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"\nError: Vault path does not exist: {vault_path}")
        print("Please check the path and try again")
        sys.exit(1)
    
    if not vault_path.is_dir():
        print(f"\nError: {vault_path} is not a directory")
        sys.exit(1)
    
    # Check if it's a valid Obsidian vault
    if not (vault_path / ".obsidian").exists():
        print(f"\nWarning: {vault_path} does not look like a valid Obsidian Vault")
        print("Please confirm this is an Obsidian vault path")
        response = "y"  # Auto-accept in non-interactive mode
        if response.lower() != "y":
            sys.exit(0)
    
    # Run initialization if requested
    if args.init:
        print(f"\nInitializing vault: {vault_path}")
        
        # Step 1: Create folder structure
        create_folder_structure(vault_path, args.template)
        
        # Step 2: Create templates
        create_templates(vault_path)
        
        # Step 3: Create index page
        create_index_page(vault_path, args.template)
        
        print("\nInitialization complete!")
        print("Next steps:")
        print("  1. Open Obsidian and select this vault path")
        print("  2. Install recommended plugins (see below)")
        print("  3. Start creating notes with templates")
    
    # Show plugin recommendations
    if args.recommend_plugins or args.show_plugins:
        show_plugin_guide()
    
    # If no action specified, show usage
    if not args.init and not args.recommend_plugins and not args.show_plugins:
        print("\nUsage examples:")
        print("  python3 obsidian_pilot.py /path/to/vault --init -t mixed")
        print("  python3 obsidian_pilot.py /path/to/vault --recommend-plugins")
        print("  python3 obsidian_pilot.py /path/to/vault --show-plugins")


if __name__ == "__main__":
    main()
