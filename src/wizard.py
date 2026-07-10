#!/usr/bin/env python3
"""Obsidian Pilot - Interactive Wizard"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from init import show_welcome, create_folder_structure, create_templates, create_index_page, show_plugin_guide, FOLDER_TEMPLATES
from note_import import scan_notes, show_import_report, apply_changes
from link import extract_titles_and_slugs, find_missing_links, detect_isolated_notes, apply_link_updates
from route import check_local_knowledge, recommend_assistant
from maintain import find_expired_notes, find_duplicate_titles, find_orphaned_links, archive_expired_notes


def interactive_init(vault_path):
    """Interactive wizard for vault initialization."""
    print("\n📁 Step 1: Choose a folder template")
    for key, template in FOLDER_TEMPLATES.items():
        print(f"  {key:12} - {template['name']:20} ({template['description']})")
    
    choice = input("\nSelect template (default: mixed): ").strip() or "mixed"
    if choice not in FOLDER_TEMPLATES:
        print(f"Invalid choice, defaulting to mixed")
        choice = "mixed"
    
    print(f"\n📁 Step 2: Creating folder structure for '{FOLDER_TEMPLATES[choice]['name']}'")
    create_folder_structure(vault_path, choice)
    
    print(f"\n📁 Step 3: Creating templates")
    create_templates(vault_path)
    
    print(f"\n📁 Step 4: Generating index page")
    create_index_page(vault_path, choice)
    
    print(f"\n✅ Initialization complete!")
    show_plugin_guide()


def interactive_import(vault_path):
    """Interactive wizard for note import."""
    print("\n📋 Step 1: Scanning notes...")
    results, category_counts, uncategorized = scan_notes(vault_path)
    
    print(f"\n📋 Step 2: Found {len(results)} notes")
    print("\nCategory distribution:")
    for category, count in category_counts.most_common():
        print(f"  {category:20} {count} notes")
    
    if uncategorized:
        print(f"\n⚠️  {len(uncategorized)} notes could not be categorized")
        for f, t in uncategorized[:5]:
            print(f"  - {f.name}: {t[:50]}")
    
    apply = input("\nApply changes? (y/N): ").strip().lower() == "y"
    if apply:
        print("\n📋 Step 3: Applying changes...")
        updated = apply_changes(vault_path, results)
        print(f"\n✅ Updated {updated} notes.")
    else:
        print("\nSkipped. Run with --apply to apply changes.")


def interactive_route(vault_path):
    """Interactive wizard for AI routing."""
    print("\n🔍 Step 1: Enter your query")
    query = input("Query: ").strip()
    
    if not query:
        print("Empty query, exiting.")
        return
    
    print(f"\n🔍 Step 2: Checking local knowledge for '{query}'...")
    result = check_local_knowledge(vault_path, query)
    
    if result['found']:
        print(f"\n✅ Found in local knowledge!")
        print(f"  Source: {result['source']}")
        print(f"  Score: {result['score']}")
        print(f"  Answer preview:")
        print(f"  {result['answer'][:500]}")
    else:
        print(f"\n❌ No local match found")
        assistant, desc = recommend_assistant(query)
        print(f"  Recommended assistant: {assistant}")
        print(f"  Description: {desc}")


def interactive_maintain(vault_path):
    """Interactive wizard for maintenance."""
    print("\n🧹 Step 1: Running maintenance checks...")
    
    expired = find_expired_notes(vault_path)
    duplicates, notes = find_duplicate_titles(vault_path)
    orphaned = find_orphaned_links(vault_path)
    
    print(f"\n🧹 Step 2: Results")
    print(f"  Total notes: {len(notes)}")
    print(f"  Expired notes (>30 days): {len(expired)}")
    print(f"  Duplicate titles: {len(duplicates)}")
    print(f"  Orphaned links: {len(orphaned)}")
    
    if expired:
        print(f"\n🧹 Step 3: Expired notes")
        for note in expired[:5]:
            print(f"  - {note['title']} ({note['age_days']} days old)")
        if len(expired) > 5:
            print(f"  ... and {len(expired) - 5} more")
    
    archive = input("\nArchive expired notes? (y/N): ").strip().lower() == "y"
    if archive:
        print("\n🧹 Step 4: Archiving...")
        archived = archive_expired_notes(vault_path, expired)
        print(f"\n✅ Archived {archived} notes.")


def main():
    parser = argparse.ArgumentParser(
        description="Obsidian Pilot - Interactive Wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Wizard command")
    
    # Init wizard
    init_parser = subparsers.add_parser("wizard-init", help="Interactive vault initialization")
    init_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    
    # Import wizard
    import_parser = subparsers.add_parser("wizard-import", help="Interactive note import")
    import_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    
    # Route wizard
    route_parser = subparsers.add_parser("wizard-route", help="Interactive AI routing")
    route_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    
    # Maintain wizard
    maintain_parser = subparsers.add_parser("wizard-maintain", help="Interactive maintenance")
    maintain_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    
    args = parser.parse_args()
    
    if not args.command:
        show_welcome()
        print("\n🎯 Choose a wizard:")
        print("  wizard-init     - Interactive vault initialization")
        print("  wizard-import   - Interactive note import")
        print("  wizard-route    - Interactive AI routing")
        print("  wizard-maintain - Interactive maintenance")
        return
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"\nError: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    if args.command == "wizard-init":
        interactive_init(str(vault_path))
    elif args.command == "wizard-import":
        interactive_import(str(vault_path))
    elif args.command == "wizard-route":
        interactive_route(str(vault_path))
    elif args.command == "wizard-maintain":
        interactive_maintain(str(vault_path))


if __name__ == "__main__":
    main()
