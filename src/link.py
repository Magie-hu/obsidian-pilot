#!/usr/bin/env python3
"""Obsidian Pilot - Phase 3: Link Automation & Index Maintenance"""
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Common technical terms mapped to likely note titles
COMMON_TERMS = {
    "claude code": "Claude Code vs Codex CLI",
    "codex": "Claude Code vs Codex CLI",
    "cursor": "AI Coding Tools Comparison 2026",
    "docker": "Docker Compose Multi-Service Orchestration",
    "kubernetes": "Kubernetes Production Best Practices",
    "nginx": "Nginx Advanced Configuration and Tuning",
    "linux": "Linux Network Diagnostic Command Guide",
    "go": "Go Concurrency Patterns",
    "rust": "Rust Async with Tokio",
    "ai agent": "AI Agent Framework Comparison",
    "hermes": "Hermes Agent Install Guide",
    "openclaw": "OpenClaw Install Guide",
}


def extract_links_from_content(content):
    """Extract all [[wiki-links]] from markdown content."""
    return re.findall(r'\[\[(.+?)\]\]', content)


def extract_titles_and_slugs(vault_path):
    """Build a mapping of titles to file paths."""
    vault = Path(vault_path).resolve()
    title_map = {}
    
    for md_file in vault.rglob('*.md'):
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
                slug = md_file.stem
                title_map[title.lower()] = {
                    'file': md_file,
                    'slug': slug,
                    'title': title,
                }
        except:
            pass
    
    return title_map


def find_missing_links(content, title_map, current_file_slug):
    """Find potential wiki-links that should be added to the note."""
    links_found = extract_links_from_content(content)
    missing = []
    
    # Check for common terms that should be linked
    content_lower = content.lower()
    for term, suggested_title in COMMON_TERMS.items():
        if term in content_lower:
            # Check if already linked
            linked = False
            for link in links_found:
                if suggested_title.lower() in link.lower():
                    linked = True
                    break
            
            if not linked:
                missing.append({
                    'term': term,
                    'suggested': suggested_title,
                    'current_file': current_file_slug,
                })
    
    # Check cross-references
    for title_key in title_map:
        if title_key in content_lower and title_key not in links_found:
            missing.append({
                'term': title_key,
                'suggested': title_map[title_key]['title'],
                'current_file': current_file_slug,
            })
    
    return missing


def detect_isolated_notes(vault_path, title_map):
    """Find notes with no outgoing or incoming links."""
    isolated = []
    
    for title_key, info in title_map.items():
        try:
            content = info['file'].read_text(encoding='utf-8')
            links = extract_links_from_content(content)
            
            # A note is isolated if it has no wiki-links
            if not links:
                isolated.append({
                    'file': info['file'],
                    'title': info['title'],
                    'has_outgoing': False,
                    'has_incoming': False,
                })
            else:
                # Check if any other note links to this one
                has_incoming = False
                for other_title, other_info in title_map.items():
                    if other_title == title_key:
                        continue
                    try:
                        other_content = other_info['file'].read_text(encoding='utf-8')
                        if info['title'] in other_content or title_key in other_content.lower():
                            has_incoming = True
                            break
                    except:
                        pass
                
                isolated.append({
                    'file': info['file'],
                    'title': info['title'],
                    'has_outgoing': True,
                    'has_incoming': has_incoming,
                })
        except:
            isolated.append({
                'file': info['file'],
                'title': info['title'],
                'has_outgoing': False,
                'has_incoming': False,
            })
    
    return isolated


def update_index_page(vault_path, title_map):
    """Update the master index page with new notes."""
    vault = Path(vault_path).resolve()
    index_path = vault / "00-Index.md"
    
    if not index_path.exists():
        print("No index page found. Skipping update.")
        return None
    
    try:
        content = index_path.read_text(encoding='utf-8')
        
        # Find the Recent Notes section
        recent_match = re.search(r'(## Recent Notes\n)(.*)', content, re.DOTALL)
        if not recent_match:
            print("Could not find Recent Notes section in index.")
            return None
        
        # Build updated recent notes section
        recent_section = recent_match.group(1)
        recent_section += "```dataview\nTABLE WITHOUT ID\nfile.link AS Note,\nfile.tags AS Tags,\nfile.ctime AS Created\nFROM \"\"\nSORT file.ctime DESC\nLIMIT 10\n```\n"
        
        # Replace the section
        new_content = content[:recent_match.start(2)] + recent_section + content[recent_match.end(2):]
        
        return new_content
    except Exception as e:
        print(f"Error updating index: {e}")
        return None


def show_link_report(results, isolated, dry_run=True):
    """Display link automation report."""
    print("\n" + "=" * 60)
    print("Link Automation Report")
    print("=" * 60)
    
    print(f"\nTotal notes analyzed: {len(results) + len(isolated)}")
    
    # Missing links
    missing_count = sum(len(r['missing']) for r in results)
    print(f"Potential links to add: {missing_count}")
    
    if missing_count > 0:
        print("\nSuggested links:")
        for r in results:
            if r['missing']:
                for m in r['missing']:
                    print(f"  [{m['current_file']}] -> [{m['suggested']}]")
    
    # Isolated notes
    isolated_count = sum(1 for i in isolated if not i['has_outgoing'] and not i['has_incoming'])
    print(f"\nFully isolated notes: {isolated_count}")
    
    if isolated_count > 0:
        print("\nIsolated notes:")
        for i in isolated:
            if not i['has_outgoing'] and not i['has_incoming']:
                print(f"  - {i['title']} ({i['file'].name})")
    
    # Incoming links
    no_incoming = sum(1 for i in isolated if i['has_outgoing'] and not i['has_incoming'])
    print(f"\nNotes with no incoming links: {no_incoming}")
    
    print("\n" + "-" * 60)
    if dry_run:
        print("DRY RUN: No changes will be made.")
        print("Run with --apply to apply suggested links.")
    else:
        print("Changes would be applied:")
        for r in results:
            if r['missing']:
                for m in r['missing']:
                    print(f"  Add [[{m['suggested']}]] to {m['current_file']}")
    print("=" * 60)


def apply_link_updates(vault_path, results, isolated):
    """Apply suggested link updates to notes."""
    vault = Path(vault_path).resolve()
    updated = 0
    
    for r in results:
        if not r.get('missing'):
            continue
        
        try:
            content = r['file'].read_text(encoding='utf-8')
            modified = False
            
            for m in r['missing']:
                suggested_link = f"[[{m['suggested']}]]"
                if suggested_link not in content:
                    # Add link to the end of the content
                    content = content.rstrip() + f"\n\nRelated: {suggested_link}"
                    modified = True
                    print(f"  Added link to {r['file'].name}: {suggested_link}")
            
            if modified:
                r['file'].write_text(content, encoding='utf-8')
                updated += 1
        except Exception as e:
            print(f"  Error updating {r['file'].name}: {e}")
    
    return updated


def main():
    parser = argparse.ArgumentParser(description="Obsidian Pilot - Link Automation & Index Maintenance")
    parser.add_argument("vault_path", help="Path to your Obsidian vault")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show report without modifying files")
    parser.add_argument("--apply", "-a", action="store_true", help="Apply link suggestions")
    parser.add_argument("--update-index", action="store_true", help="Update index page")
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print(f"Analyzing links in: {vault_path}")
    
    # Build title map
    title_map = extract_titles_and_slugs(str(vault_path))
    
    # Analyze each note
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
    
    # Detect isolated notes
    isolated = detect_isolated_notes(str(vault_path), title_map)
    
    # Show report
    show_link_report(results, isolated, dry_run=not args.apply)
    
    # Apply changes if requested
    if args.apply:
        print("\nApplying link updates...")
        updated = apply_link_updates(str(vault_path), results, isolated)
        print(f"\nUpdated {updated} notes with suggested links.")
    
    # Update index if requested
    if args.update_index:
        print("\nUpdating index page...")
        new_content = update_index_page(str(vault_path), title_map)
        if new_content:
            index_path = vault_path / "00-Index.md"
            index_path.write_text(new_content, encoding='utf-8')
            print(f"Index page updated: {index_path.name}")


if __name__ == "__main__":
    main()
