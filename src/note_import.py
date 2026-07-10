#!/usr/bin/env python3
"""Obsidian Pilot - Phase 2: Note Import & Auto-Classification"""
import os
import sys
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

# Category definitions with keywords for auto-classification
CATEGORY_DEFINITIONS = {
    "raw": {
        "keywords": ["raw", "imported", "pending", "untreated", "source material"],
        "tags": ["raw", "imported"],
        "subfolder": "raw",
    },
    "wiki": {
        "keywords": ["wiki", "entry", "concept", "definition", "knowledge", "tutorial", "guide", "how to"],
        "tags": ["wiki", "entry"],
        "subfolder": "wiki",
    },
    "attachment": {
        "keywords": ["attachment", "media", "image", "video", "audio", "file"],
        "tags": ["attachment", "media"],
        "subfolder": "attachments",
    },
    "script": {
        "keywords": ["script", "automation", "shell", "python script", "workflow", "pipeline"],
        "tags": ["script", "automation"],
        "subfolder": "scripts",
    },
}


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        fm = {}
        for line in fm_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Handle list values
                if value.startswith('[') and value.endswith(']'):
                    items = [item.strip().strip('"').strip("'") for item in value[1:-1].split(',')]
                    fm[key] = items
                else:
                    fm[key] = value
        return fm, fm_match.end()
    return {}, 0


def extract_title(content, filepath):
    """Extract title from H1 or filename."""
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()
    # Fallback: use filename
    return filepath.stem.replace('-', ' ').replace('_', ' ').title()


def classify_note(content, frontmatter):
    """Classify note based on content and frontmatter tags."""
    combined = content.lower()
    
    # If frontmatter already has category, use it
    if 'category' in frontmatter and frontmatter['category']:
        return frontmatter['category']
    
    # If frontmatter has tags, map them
    if 'tags' in frontmatter and frontmatter['tags']:
        for tag in frontmatter['tags']:
            for category, info in CATEGORY_DEFINITIONS.items():
                if tag in info['tags']:
                    return category
    
    # Score each category by keyword matches
    scores = {}
    for category, info in CATEGORY_DEFINITIONS.items():
        score = 0
        for keyword in info['keywords']:
            if keyword in combined:
                score += 1
        scores[category] = score
    
    # Return highest scoring category
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best
    
    # Default: Uncategorized
    return "Uncategorized"


def extract_date(content, frontmatter, filepath):
    """Extract or infer date from frontmatter, title, or filename."""
    # Check frontmatter first
    if 'date' in frontmatter and frontmatter['date']:
        return frontmatter['date']
    
    # Try to extract from title
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        return date_match.group(1)
    
    # Try filename
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filepath.stem)
    if date_match:
        return date_match.group(1)
    
    # Fallback: file modification date
    try:
        mtime = filepath.stat().st_mtime
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
    except:
        return datetime.now().strftime('%Y-%m-%d')


def generate_frontmatter(category, title, date, tags=None):
    """Generate standardized frontmatter."""
    if tags is None:
        tags = CATEGORY_DEFINITIONS.get(category, {}).get('tags', [])
    
    fm = {
        'tags': tags,
        'date': date,
        'category': category,
        'status': 'published',
    }
    
    fm_lines = ['---']
    for key, value in fm.items():
        if isinstance(value, list):
            fm_lines.append(f'{key}: [{", ".join(value)}]')
        else:
            fm_lines.append(f'{key}: {value}')
    fm_lines.append('---')
    
    return '\n'.join(fm_lines)


def scan_notes(vault_path, dry_run=True):
    """Scan all markdown files in the vault and classify them."""
    vault = Path(vault_path).resolve()
    md_files = list(vault.rglob('*.md'))
    
    results = []
    category_counts = Counter()
    uncategorized = []
    
    for md_file in md_files:
        # Skip hidden files and templates
        if md_file.name.startswith('.') or '_templates' in str(md_file):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            if not content.strip():
                continue
            
            frontmatter, fm_end = extract_frontmatter(content)
            title = extract_title(content, md_file)
            category = classify_note(content, frontmatter)
            date = extract_date(content, frontmatter, md_file)
            
            category_counts[category] += 1
            
            if category == "Uncategorized":
                uncategorized.append((md_file, title))
            
            results.append({
                'file': str(md_file.relative_to(vault)),
                'title': title,
                'category': category,
                'date': date,
                'frontmatter': frontmatter,
                'needs_update': 'category' not in frontmatter or frontmatter.get('category') != category,
            })
        except Exception as e:
            results.append({
                'file': str(md_file.relative_to(vault)),
                'title': md_file.stem,
                'category': 'Error',
                'date': 'unknown',
                'frontmatter': {},
                'needs_update': False,
                'error': str(e),
            })
    
    return results, category_counts, uncategorized


def show_import_report(results, category_counts, uncategorized, dry_run=True):
    """Display classification report."""
    print("\n" + "=" * 60)
    print("Note Classification Report")
    print("=" * 60)
    
    print(f"\nTotal notes scanned: {len(results)}")
    print(f"Categories found: {len(category_counts)}")
    
    print("\nCategory Distribution:")
    for category, count in category_counts.most_common():
        print(f"  {category:20} {count} notes")
    
    if uncategorized:
        print(f"\nUncategorized ({len(uncategorized)} notes):")
        for f, t in uncategorized[:10]:
            print(f"  - {f.name}: {t[:50]}")
        if len(uncategorized) > 10:
            print(f"  ... and {len(uncategorized) - 10} more")
    
    print("\n" + "-" * 60)
    if dry_run:
        print("DRY RUN: No files will be modified.")
        print("Run with --apply to apply changes.")
    else:
        print("Changes would be applied:")
        for r in results:
            if r['needs_update']:
                print(f"  Update {r['file']}: category={r['category']}, date={r['date']}")
    print("=" * 60)


def apply_changes(vault_path, results):
    """Apply frontmatter updates to classified notes."""
    vault = Path(vault_path).resolve()
    updated = 0
    
    for r in results:
        if not r['needs_update']:
            continue
        
        md_file = vault / r['file']
        try:
            content = md_file.read_text(encoding='utf-8')
            
            # Generate new frontmatter
            new_fm = generate_frontmatter(
                r['category'],
                r['title'],
                r['date'],
                r.get('tags')
            )
            
            # Replace existing frontmatter or prepend
            fm_match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
            if fm_match:
                content = new_fm + '\n' + content[fm_match.end():]
            else:
                content = new_fm + '\n\n' + content
            
            md_file.write_text(content, encoding='utf-8')
            updated += 1
            print(f"  Updated: {r['file']}")
        except Exception as e:
            print(f"  Error updating {r['file']}: {e}")
    
    return updated


def main():
    parser = argparse.ArgumentParser(description="Obsidian Pilot - Note Import & Classification")
    parser.add_argument("vault_path", help="Path to your Obsidian vault")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show report without modifying files")
    parser.add_argument("--apply", "-a", action="store_true", help="Apply changes to files")
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    print(f"Scanning notes in: {vault_path}")
    
    results, category_counts, uncategorized = scan_notes(str(vault_path))
    show_import_report(results, category_counts, uncategorized, dry_run=not args.apply)
    
    if args.apply:
        print("\nApplying changes...")
        updated = apply_changes(str(vault_path), results)
        print(f"\nUpdated {updated} notes.")
    else:
        print("\nTo apply changes, run with --apply flag.")


if __name__ == "__main__":
    main()
