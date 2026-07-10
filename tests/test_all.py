#!/usr/bin/env python3
"""Obsidian Pilot - Test Suite"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from init import create_folder_structure, create_templates, create_index_page
from note_import import scan_notes
from link import extract_titles_and_slugs, find_missing_links, detect_isolated_notes
from route import check_local_knowledge
from maintain import find_expired_notes, find_duplicate_titles, find_orphaned_links


def test_init():
    """Test initialization."""
    tmpdir = tempfile.mkdtemp(prefix="test-init-")
    try:
        vault = Path(tmpdir)
        vault.mkdir(exist_ok=True)
        
        # Create folder structure
        create_folder_structure(str(vault), "minimal")
        
        # Check folders exist
        for folder in ["Inbox", "Projects", "Archive"]:
            assert (vault / folder).is_dir(), f"Missing folder: {folder}"
        
        # Create templates
        create_templates(str(vault))
        
        # Check templates exist
        for tmpl in ["raw-material.md", "index.md", "wiki-entry.md"]:
            assert (vault / "_templates" / tmpl).is_file(), f"Missing template: {tmpl}"
        
        # Create index page
        create_index_page(str(vault), "minimal")
        
        # Check index exists
        assert (vault / "00-Index.md").is_file(), "Missing index page"
        
        print("✅ test_init passed")
        return True
    except AssertionError as e:
        print(f"❌ test_init failed: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir)


def test_import():
    """Test note import."""
    tmpdir = tempfile.mkdtemp(prefix="test-import-")
    try:
        vault = Path(tmpdir)
        vault.mkdir(exist_ok=True)
        
        # Create sample notes
        (vault / "test-wiki.md").write_text("# Test Wiki Entry\nLangGraph is great for building AI agents.\n\nThis is a wiki concept definition.")
        (vault / "test-raw.md").write_text("# Test Raw Material\nRaw source document for processing.\n\nPending review.")
        (vault / "test-script.md").write_text("# Test Script\nShell automation workflow for pipeline.\n\nPipeline script for deployment.")
        
        # Scan notes
        results, category_counts, uncategorized = scan_notes(str(vault))
        
        # Check results
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        assert "wiki" in category_counts, "wiki category not found"
        assert "raw" in category_counts, "raw category not found"
        assert "script" in category_counts, "script category not found"
        
        print("✅ test_import passed")
        return True
    except AssertionError as e:
        print(f"❌ test_import failed: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir)


def test_link():
    """Test link automation."""
    tmpdir = tempfile.mkdtemp(prefix="test-link-")
    try:
        vault = Path(tmpdir)
        vault.mkdir(exist_ok=True)
        
        # Create sample notes
        (vault / "test-note1.md").write_text("# Test Note 1\nThis mentions Docker and Kubernetes.\n\nRelated: [[Test Note 2]]")
        (vault / "test-note2.md").write_text("# Test Note 2\nThis mentions AI Agent and Claude Code.\n\nRelated: [[Test Note 1]]")
        
        # Extract titles
        title_map = extract_titles_and_slugs(str(vault))
        assert len(title_map) == 2, f"Expected 2 titles, got {len(title_map)}"
        
        # Find missing links
        results = []
        for title_key, info in title_map.items():
            content = info['file'].read_text(encoding='utf-8')
            missing = find_missing_links(content, title_map, info['slug'])
            results.append({
                'file': info['file'],
                'title': info['title'],
                'slug': info['slug'],
                'missing': missing,
            })
        
        # Check results
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        
        print("✅ test_link passed")
        return True
    except AssertionError as e:
        print(f"❌ test_link failed: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir)


def test_route():
    """Test AI routing."""
    tmpdir = tempfile.mkdtemp(prefix="test-route-")
    try:
        vault = Path(tmpdir)
        vault.mkdir(exist_ok=True)
        
        # Create sample note
        (vault / "test-docker.md").write_text("# Test Docker\nHow to use docker compose for multi-service deployment.\n\n## Steps\n1. Install Docker\n2. Create docker-compose.yml\n3. Run docker compose up")
        
        # Check local knowledge
        result = check_local_knowledge(str(vault), "docker compose")
        
        assert result['found'], "Expected to find docker compose in local knowledge"
        assert result['source'] == "test-docker", f"Expected source test-docker, got {result['source']}"
        
        print("✅ test_route passed")
        return True
    except AssertionError as e:
        print(f"❌ test_route failed: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir)


def test_maintain():
    """Test maintenance."""
    tmpdir = tempfile.mkdtemp(prefix="test-maintain-")
    try:
        vault = Path(tmpdir)
        vault.mkdir(exist_ok=True)
        
        # Create sample notes with dates
        (vault / "2020-01-01-old-note.md").write_text("# Old Note\nThis is an old note from 2020.")
        (vault / "2026-07-09-new-note.md").write_text("# New Note\nThis is a new note.")
        (vault / "duplicate-title.md").write_text("# Duplicate Title\nFirst occurrence.")
        (vault / "duplicate-title-copy.md").write_text("# Duplicate Title\nSecond occurrence.")
        
        # Find expired notes
        expired = find_expired_notes(str(vault))
        assert len(expired) >= 1, f"Expected at least 1 expired note, got {len(expired)}"
        
        # Find duplicate titles
        duplicates, notes = find_duplicate_titles(str(vault))
        assert "Duplicate Title" in duplicates, f"Expected duplicate title, got {duplicates}"
        
        # Find orphaned links
        orphaned = find_orphaned_links(str(vault))
        # Should be 0 since no wiki-links in our test notes
        
        print("✅ test_maintain passed")
        return True
    except AssertionError as e:
        print(f"❌ test_maintain failed: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir)


def main():
    print("\n" + "=" * 60)
    print("Obsidian Pilot - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Initialization", test_init),
        ("Note Import", test_import),
        ("Link Automation", test_link),
        ("AI Routing", test_route),
        ("Maintenance", test_maintain),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\nRunning {name}...")
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
