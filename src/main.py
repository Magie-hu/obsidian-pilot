#!/usr/bin/env python3
"""Obsidian Pilot - Main Entry Point"""
import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from init import show_welcome, create_folder_structure, create_templates, create_index_page, show_plugin_guide
from note_import import scan_notes, show_import_report, apply_changes
from link import extract_titles_and_slugs, find_missing_links, detect_isolated_notes, update_index_page
from route import check_local_knowledge, recommend_assistant
from maintain import find_expired_notes, find_duplicate_titles, find_orphaned_links


def cmd_init(vault_path, template):
    """Initialize a new vault."""
    print(f"\nInitializing vault: {vault_path}")
    create_folder_structure(vault_path, template)
    create_templates(vault_path)
    create_index_page(vault_path, template)
    print("\nInitialization complete!")
    print("Next steps:")
    print("  1. Open Obsidian and select this vault path")
    print("  2. Install recommended plugins (see below)")
    print("  3. Start creating notes with templates")
    show_plugin_guide()


def cmd_import(vault_path, apply=False):
    """Import and classify notes."""
    print(f"\nScanning notes in: {vault_path}")
    results, category_counts, uncategorized = scan_notes(vault_path)
    show_import_report(results, category_counts, uncategorized, dry_run=not apply)
    
    if apply:
        print("\nApplying changes...")
        updated = apply_changes(vault_path, results)
        print(f"\nUpdated {updated} notes.")


def cmd_link(vault_path, apply=False):
    """Automate links."""
    print(f"\nAnalyzing links in: {vault_path}")
    title_map = extract_titles_and_slugs(vault_path)
    
    results = []
    for title_key, info in title_map.items():
        try:
            content = info['file'].read_text(encoding='utf-8')
            missing = find_missing_links(content, title_map, info['slug'])
            results.append({
                'file': info['file'],
                'title': info['title'],
                'slug': info['slug'],
                'missing': missing,
            })
        except:
            pass
    
    isolated = detect_isolated_notes(vault_path, title_map)
    
    missing_count = sum(len(r['missing']) for r in results)
    isolated_count = sum(1 for i in isolated if not i['has_outgoing'] and not i['has_incoming'])
    
    print(f"\nMissing links: {missing_count}")
    print(f"Isolated notes: {isolated_count}")
    
    if missing_count > 0:
        print("\nSuggested links:")
        for r in results:
            if r['missing']:
                for m in r['missing']:
                    print(f"  [{m['current_file']}] -> [{m['suggested']}]")
    
    if apply:
        print("\nApplying link updates...")
        updated = apply_link_updates(vault_path, results, isolated)
        print(f"\nUpdated {updated} notes with suggested links.")


def cmd_route(vault_path, query):
    """Route query to local knowledge or AI assistant."""
    print(f"\nTesting query: '{query}'")
    result = check_local_knowledge(vault_path, query)
    
    if result['found']:
        print(f"\n✓ Found in local knowledge!")
        print(f"  Source: {result['source']}")
        print(f"  Answer preview: {result['answer'][:200]}...")
    else:
        print(f"\n✗ No local match found")
        assistant, desc = recommend_assistant(query)
        print(f"  Recommended: {assistant} ({desc})")


def cmd_maintain(vault_path, archive=False):
    """Run maintenance checks."""
    print(f"\nRunning maintenance check for: {vault_path}")
    
    expired = find_expired_notes(vault_path)
    duplicates, notes = find_duplicate_titles(vault_path)
    orphaned = find_orphaned_links(vault_path)
    
    print(f"\nTotal notes: {len(notes)}")
    print(f"Expired notes (> {30} days): {len(expired)}")
    print(f"Duplicate titles: {len(duplicates)}")
    print(f"Orphaned links: {len(orphaned)}")
    
    if expired:
        print("\nExpired Notes:")
        for note in expired[:10]:
            print(f"  - {note['title']} ({note['age_days']} days old)")
        if len(expired) > 10:
            print(f"  ... and {len(expired) - 10} more")
    
    if duplicates:
        print("\nDuplicate Titles:")
        for title, count in duplicates.items():
            print(f"  - \"{title}\" appears {count} times")
    
    if orphaned:
        print("\nOrphaned Links:")
        for item in orphaned[:10]:
            print(f"  - {item['file'].name}: [[{item['broken_link']}]]")
        if len(orphaned) > 10:
            print(f"  ... and {len(orphaned) - 10} more")
    
    if archive:
        print("\nArchiving expired notes...")
        archived = archive_expired_notes(vault_path, expired)
        print(f"\nArchived {archived} notes.")


def main():
    parser = argparse.ArgumentParser(
        description="Obsidian Pilot - Your First Obsidian Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 obsidian_pilot.py init /path/to/vault -t mixed
  python3 obsidian_pilot.py import /path/to/vault --dry-run
  python3 obsidian_pilot.py link /path/to/vault --apply
  python3 obsidian_pilot.py route /path/to/vault -q "Docker"
  python3 obsidian_pilot.py maintain /path/to/vault --archive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new vault")
    init_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    init_parser.add_argument("-t", "--template", choices=["llm-wiki", "minimal"],
                            default="llm-wiki", help="Folder template to use (default: llm-wiki)")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import and classify notes")
    import_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    import_parser.add_argument("--apply", "-a", action="store_true", help="Apply changes")
    
    # Link command
    link_parser = subparsers.add_parser("link", help="Automate wiki-links")
    link_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    link_parser.add_argument("--apply", "-a", action="store_true", help="Apply link suggestions")
    
    # Route command
    route_parser = subparsers.add_parser("route", help="AI assistant smart routing")
    route_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    route_parser.add_argument("-q", "--query", required=True, help="Query to test")
    
    # Maintain command
    maintain_parser = subparsers.add_parser("maintain", help="Daily maintenance")
    maintain_parser.add_argument("vault_path", help="Path to your Obsidian vault")
    maintain_parser.add_argument("--archive", "-a", action="store_true", help="Archive expired notes")
    
    args = parser.parse_args()
    
    if not args.command:
        show_welcome()
        parser.print_help()
        return
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"\nError: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    if not vault_path.is_dir():
        print(f"\nError: {vault_path} is not a directory")
        sys.exit(1)
    
    if args.command == "init":
        cmd_init(str(vault_path), args.template)
    elif args.command == "import":
        cmd_import(str(vault_path), apply=args.apply)
    elif args.command == "link":
        cmd_link(str(vault_path), apply=args.apply)
    elif args.command == "route":
        cmd_route(str(vault_path), args.query)
    elif args.command == "maintain":
        cmd_maintain(str(vault_path), archive=args.archive)


if __name__ == "__main__":
    main()
