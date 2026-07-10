#!/usr/bin/env python3
"""End-to-end test: simulate a real user workflow."""
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, "/mnt/c/Users/Allen/Desktop/projects/obsidian pilot/src")

from init import create_folder_structure, create_templates, create_index_page
from note_import import scan_notes
from link import extract_titles_and_slugs, find_missing_links
from route import check_local_knowledge
from maintain import find_expired_notes, find_duplicate_titles


def test_workflow():
    """Simulate a complete user workflow."""
    tmpdir = tempfile.mkdtemp(prefix="e2e-test-")
    try:
        vault = Path(tmpdir)
        
        # Step 1: Initialize vault
        print("Step 1: Initializing vault...")
        create_folder_structure(str(vault), "minimal")
        create_templates(str(vault))
        create_index_page(str(vault), "minimal")
        assert (vault / "00-Index.md").exists(), "Index page not created"
        print("  OK: Vault initialized")
        
        # Step 2: Create sample notes
        print("Step 2: Creating sample notes...")
        (vault / "ai-agent-guide.md").write_text("# AI Agent Development Guide\nLangGraph is great for building AI agents.\n\nSee also: [[Docker Deployment]])")
        (vault / "docker-setup.md").write_text("# Docker Setup Guide\nHow to use docker compose for deployment.")
        (vault / "stock-report.md").write_text("# Stock Market Report 2026-07-09\nStock market analysis.\n\nInvestment portfolio update.")
        print("  OK: 3 notes created")
        
        # Step 3: Scan and classify
        print("Step 3: Scanning and classifying notes...")
        results, counts, uncategorized = scan_notes(str(vault))
        assert len(results) == 4, f"Expected 4 results (3 notes + 1 index), got {len(results)}"
        print(f"  OK: Classified {len(results)} notes into {len(counts)} categories")
        
        # Step 4: Check links
        print("Step 4: Checking links...")
        title_map = extract_titles_and_slugs(str(vault))
        assert len(title_map) == 4, f"Expected 4 titles (3 notes + 1 index), got {len(title_map)}"
        print(f"  OK: Found {len(title_map)} notes with titles")
        
        # Step 5: Test routing
        print("Step 5: Testing AI routing...")
        result = check_local_knowledge(str(vault), "docker compose")
        assert result['found'], "Expected to find docker in local knowledge"
        print(f"  OK: Found '{result['source']}' for 'docker compose'")
        
        # Step 6: Check maintenance
        print("Step 6: Running maintenance checks...")
        expired = find_expired_notes(str(vault))
        duplicates, _ = find_duplicate_titles(str(vault))
        print(f"  OK: {len(expired)} expired, {len(duplicates)} duplicate titles")
        
        print("\n✅ All steps passed!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ FAILED: {e}")
        return False
    finally:
        shutil.rmtree(tmpdir)


if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)
