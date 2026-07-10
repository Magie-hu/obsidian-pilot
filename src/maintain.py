#!/usr/bin/env python3
"""Obsidian Pilot - Phase 5: Daily Maintenance & Expiry Alerts"""
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# Days before marking as expired
EXPIRY_DAYS = 30
DAILY_DIGEST_DAYS = 7

# Patterns for detecting daily notes
DAILY_PATTERNS = [
    r'(\d{4}-\d{2}-\d{2})',
    r'(\d{4}/\d{2}/\d{2})',
    r'(\d{4}\.\d{2}\.\d{2})',
    r'(\d{4}年\d{1,2}月\d{1,2}日)',
]


def extract_date_from_content(content, filepath):
    """Extract date from content or filename."""
    # Try frontmatter first
    fm_match = re.search(r'date:\s*(.+)', content)
    if fm_match:
        date_str = fm_match.group(1).strip()
        # Try parsing various formats
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
    
    # Try filename
    stem = filepath.stem
    for pattern in DAILY_PATTERNS:
        match = re.search(pattern, stem)
        if match:
            date_str = match.group(1)
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
    
    # Fallback: file modification date
    try:
        mtime = filepath.stat().st_mtime
        return datetime.fromtimestamp(mtime)
    except:
        return None


def find_expired_notes(vault_path, days=EXPIRY_DAYS):
    """Find notes older than specified days."""
    vault = Path(vault_path).resolve()
    expired = []
    
    for md_file in vault.rglob('*.md'):
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            # Skip index pages and templates
            if '00-Index' in md_file.name or 'template' in md_file.name.lower():
                continue
            
            file_date = extract_date_from_content(content, md_file)
            if file_date:
                age = datetime.now() - file_date
                if age.days > days:
                    expired.append({
                        'file': md_file,
                        'title': md_file.stem,
                        'date': file_date.strftime('%Y-%m-%d'),
                        'age_days': age.days,
                    })
        except:
            pass
    
    return expired


def find_duplicate_titles(vault_path):
    """Find notes with similar titles."""
    vault = Path(vault_path).resolve()
    notes = []
    
    for md_file in vault.rglob('*.md'):
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
                notes.append({
                    'file': md_file,
                    'title': title,
                })
        except:
            pass
    
    # Simple duplicate detection (exact match)
    title_counts = Counter(n['title'] for n in notes)
    duplicates = {title: count for title, count in title_counts.items() if count > 1}
    
    return duplicates, notes


def find_orphaned_links(vault_path):
    """Find wiki-links that point to non-existent notes."""
    vault = Path(vault_path).resolve()
    orphaned = []
    
    # Build set of all note slugs
    all_slugs = set()
    for md_file in vault.rglob('*.md'):
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        all_slugs.add(md_file.stem.lower())
    
    # Check for broken links
    for md_file in vault.rglob('*.md'):
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            links = re.findall(r'\[\[(.+?)\]\]', content)
            
            for link in links:
                if link.lower() not in all_slugs:
                    orphaned.append({
                        'file': md_file,
                        'broken_link': link,
                    })
        except:
            pass
    
    return orphaned


def generate_maintenance_report(expired, duplicates, orphaned, notes):
    """Generate maintenance report."""
    print("\n" + "=" * 60)
    print("Maintenance Report")
    print("=" * 60)
    
    print(f"\nTotal notes: {len(notes)}")
    print(f"Expired notes (> {EXPIRY_DAYS} days): {len(expired)}")
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
    
    print("\n" + "-" * 60)
    print("Recommendations:")
    print(f"  1. Archive {len(expired)} expired notes")
    print(f"  2. Merge {len(duplicates)} duplicate titles")
    print(f"  3. Fix {len(orphaned)} orphaned links")
    print("=" * 60)


def archive_expired_notes(vault_path, expired):
    """Move expired notes to Archive folder."""
    vault = Path(vault_path).resolve()
    archive_dir = vault / "Archive"
    archive_dir.mkdir(exist_ok=True)
    
    archived = 0
    for note in expired:
        try:
            dest = archive_dir / note['file'].name
            if not dest.exists():
                note['file'].rename(dest)
                archived += 1
                print(f"  Archived: {note['file'].name} -> Archive/")
            else:
                print(f"  Skipped (already exists): {note['file'].name}")
        except Exception as e:
            print(f"  Error archiving {note['file'].name}: {e}")
    
    return archived


def main():
    parser = argparse.ArgumentParser(description="Obsidian Pilot - Daily Maintenance")
    parser.add_argument("vault_path", help="Path to your Obsidian vault")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show report without modifying files")
    parser.add_argument("--archive", "-a", action="store_true", help="Archive expired notes")
    parser.add_argument("--merge", "-m", action="store_true", help="Merge duplicate titles")
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print(f"Maintenance check for: {vault_path}")
    
    # Find expired notes
    expired = find_expired_notes(str(vault_path))
    
    # Find duplicates
    duplicates, notes = find_duplicate_titles(str(vault_path))
    
    # Find orphaned links
    orphaned = find_orphaned_links(str(vault_path))
    
    # Generate report
    generate_maintenance_report(expired, duplicates, orphaned, notes)
    
    # Apply changes if requested
    if args.archive:
        print("\nArchiving expired notes...")
        archived = archive_expired_notes(str(vault_path), expired)
        print(f"\nArchived {archived} notes.")
    
    if args.merge:
        print("\nMerging duplicate titles...")
        # TODO: Implement merge logic
        print("Merge functionality coming soon.")


if __name__ == "__main__":
    main()
