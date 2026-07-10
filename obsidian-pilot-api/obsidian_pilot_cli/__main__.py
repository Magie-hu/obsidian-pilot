"""Obsidian Pilot CLI - Unified entry point."""
from pathlib import Path
import sys

# Add src directory to path for CLI modules
repo_root = Path(__file__).parent.parent.parent / "obsidian pilot" / "src"
if not repo_root.exists():
    repo_root = Path(__file__).parent.parent.parent / "src"
if not repo_root.exists():
    repo_root = Path.cwd() / "src"
sys.path.insert(0, str(repo_root))

from init import show_welcome, FOLDER_TEMPLATES
from note_import import scan_notes, show_import_report, apply_changes
from link import extract_titles_and_slugs, find_missing_links, detect_isolated_notes, show_link_report
from route import recommend_assistant, check_local_knowledge
from maintain import find_expired_notes, find_duplicate_titles, find_orphaned_links, generate_maintenance_report

import argparse
import json


def cmd_init(args):
    """Initialize vault."""
    from init import create_folder_structure, create_templates, create_index_page
    create_folder_structure(args.vault_path, args.template)
    create_templates(args.vault_path)
    create_index_page(args.vault_path, args.template)
    print("\nDone! Vault initialized.")


def cmd_import(args):
    """Import and classify notes."""
    results, category_counts, uncategorized = scan_notes(args.vault_path, dry_run=not args.apply)
    show_import_report(results, category_counts, uncategorized, dry_run=not args.apply)
    if args.apply:
        updated = apply_changes(args.vault_path, results)
        print(f"\nUpdated {updated} notes.")


def cmd_link(args):
    """Link analysis."""
    title_map = extract_titles_and_slugs(args.vault_path)
    results = []
    for title_key, info in title_map.items():
        try:
            content = info['file'].read_text(encoding='utf-8')
            missing = find_missing_links(content, title_map, info['slug'])
            results.append({'file': info['file'], 'title': info['title'], 'slug': info['slug'], 'missing': missing})
        except:
            pass
    isolated = detect_isolated_notes(args.vault_path, title_map)
    show_link_report(results, isolated, dry_run=not args.apply)
    if args.apply:
        updated = 0
        for r in results:
            if r.get('missing'):
                content = r['file'].read_text(encoding='utf-8')
                for m in r['missing']:
                    link = f"[[{m['suggested']}]]"
                    if link not in content:
                        content = content.rstrip() + f"\n\nRelated: {link}"
                        updated += 1
                r['file'].write_text(content, encoding='utf-8')
        print(f"\nUpdated {updated} notes with links.")


def cmd_route(args):
    """AI routing."""
    if args.query:
        if args.vault_path:
            result = check_local_knowledge(args.vault_path, args.query)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        assistant, desc = recommend_assistant(args.query)
        print(f"Recommended: {assistant} - {desc}")


def cmd_maintain(args):
    """Maintenance."""
    expired = find_expired_notes(args.vault_path)
    duplicates, notes = find_duplicate_titles(args.vault_path)
    orphaned = find_orphaned_links(args.vault_path)
    generate_maintenance_report(expired, duplicates, orphaned, notes)


def main():
    parser = argparse.ArgumentParser(description="Obsidian Pilot CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init
    p_init = subparsers.add_parser("init", help="Initialize vault")
    p_init.add_argument("vault_path", help="Path to vault")
    p_init.add_argument("-t", "--template", choices=list(FOLDER_TEMPLATES.keys()), default="llm-wiki")

    # import
    p_import = subparsers.add_parser("import", help="Import and classify notes")
    p_import.add_argument("vault_path", help="Path to vault")
    p_import.add_argument("--apply", "-a", action="store_true", help="Apply changes")

    # link
    p_link = subparsers.add_parser("link", help="Link analysis")
    p_link.add_argument("vault_path", help="Path to vault")
    p_link.add_argument("--apply", "-a", action="store_true", help="Apply link suggestions")

    # route
    p_route = subparsers.add_parser("route", help="AI routing")
    p_route.add_argument("vault_path", nargs="?", default=None, help="Path to vault (optional)")
    p_route.add_argument("--query", "-q", required=True, help="Query to route")

    # maintain
    p_maintain = subparsers.add_parser("maintain", help="Maintenance check")
    p_maintain.add_argument("vault_path", help="Path to vault")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "import":
        cmd_import(args)
    elif args.command == "link":
        cmd_link(args)
    elif args.command == "route":
        cmd_route(args)
    elif args.command == "maintain":
        cmd_maintain(args)
    else:
        show_welcome()
        parser.print_help()


if __name__ == "__main__":
    main()
