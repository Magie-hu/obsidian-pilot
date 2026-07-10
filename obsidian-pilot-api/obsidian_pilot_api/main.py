"""Obsidian Pilot API - Main FastAPI Application
Copyright (c) 2026 NingXiaoBan
Licensed under MIT License
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent / "obsidian pilot" / "src"
sys.path.insert(0, str(project_root))

from init import create_folder_structure, create_templates, create_index_page, FOLDER_TEMPLATES
from note_import import classify_note, scan_notes, apply_changes
from link import extract_titles_and_slugs, find_missing_links, detect_isolated_notes
from route import check_local_knowledge, recommend_assistant
from maintain import find_expired_notes, find_duplicate_titles, find_orphaned_links, archive_expired_notes

app = FastAPI(
    title="Obsidian Pilot API",
    description="LLM-Wiki Bridge Backend API",
    version="0.1.0"
)


class VaultRequest(BaseModel):
    vault_path: str

class NoteRequest(BaseModel):
    content: str
    filename: str

class ScanRequest(BaseModel):
    vault_path: str
    dry_run: bool = True

class LinkRequest(BaseModel):
    vault_path: str
    apply: bool = False

class RouteRequest(BaseModel):
    query: str
    vault_path: Optional[str] = None

class MaintainRequest(BaseModel):
    vault_path: str
    archive: bool = False

class InitResponse(BaseModel):
    status: str
    message: str
    folders_created: int
    templates_created: int

class ScanResponse(BaseModel):
    total_notes: int
    category_counts: dict
    uncategorized: List[str]
    results: List[dict]

class LinkReportResponse(BaseModel):
    missing_links: List[dict]
    isolated_notes: List[dict]
    total_notes: int

class RouteResponse(BaseModel):
    recommended_model: str
    confidence: float
    local_knowledge: Optional[str] = None

class MaintainResponse(BaseModel):
    total_notes: int
    expired_count: int
    duplicate_count: int
    orphaned_count: int
    archived: int
    expired_notes: List[dict]
    duplicate_titles: dict
    orphaned_links: List[dict]


@app.get("/")
async def root():
    return {
        "service": "Obsidian Pilot API",
        "version": "0.1.0",
        "status": "running"
    }

@app.post("/init", response_model=InitResponse)
async def init_vault(request: VaultRequest):
    """Initialize a new LLM-Wiki vault."""
    try:
        vault_path = request.vault_path
        template_name = "default"
        
        create_folder_structure(vault_path, template_name)
        create_templates(vault_path)
        create_index_page(vault_path, template_name)
        
        return InitResponse(
            status="success",
            message=f"Vault initialized at {vault_path}",
            folders_created=len(FOLDER_TEMPLATES.get(template_name, {}).get("folders", [])),
            templates_created=1
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/import", response_model=ScanResponse)
async def import_notes(request: VaultRequest):
    """Scan and classify all notes in vault."""
    try:
        results, category_counts, uncategorized = scan_notes(request.vault_path, dry_run=True)
        
        category_dict = dict(category_counts)
        uncategorized_names = [f.name for f, t in uncategorized]
        
        return ScanResponse(
            total_notes=len(results),
            category_counts=category_dict,
            uncategorized=uncategorized_names,
            results=[{
                "file": r["file"],
                "title": r["title"],
                "category": r["category"],
                "needs_update": r.get("needs_update", False),
            } for r in results]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/import/apply")
async def apply_import(request: VaultRequest):
    """Apply note classification changes."""
    try:
        results, _, _ = scan_notes(request.vault_path, dry_run=False)
        updated = apply_changes(request.vault_path, results)
        return {"status": "success", "updated": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/links/report", response_model=LinkReportResponse)
async def get_link_report(request: LinkRequest):
    """Get link analysis report for vault."""
    try:
        title_map = extract_titles_and_slugs(request.vault_path)
        
        results = []
        missing_links = []
        for title_key, info in title_map.items():
            try:
                content = info['file'].read_text(encoding='utf-8')
                missing = find_missing_links(content, title_map, info['slug'])
                results.append({
                    'file': str(info['file']),
                    'title': info['title'],
                    'slug': info['slug'],
                    'missing': missing,
                })
                for m in missing:
                    missing_links.append({
                        'source': info['title'],
                        'suggested': m['suggested'],
                        'current_file': m['current_file'],
                    })
            except:
                pass
        
        isolated = detect_isolated_notes(request.vault_path, title_map)
        
        return LinkReportResponse(
            missing_links=missing_links,
            isolated_notes=isolated,
            total_notes=len(title_map)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/links/apply")
async def apply_links(request: LinkRequest):
    """Apply link suggestions."""
    try:
        title_map = extract_titles_and_slugs(request.vault_path)
        
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
        
        isolated = detect_isolated_notes(request.vault_path, title_map)
        
        updated = 0
        for r in results:
            if r.get('missing'):
                try:
                    content = r['file'].read_text(encoding='utf-8')
                    modified = False
                    for m in r['missing']:
                        suggested_link = f"[[{m['suggested']}]]"
                        if suggested_link not in content:
                            content = content.rstrip() + f"\n\nRelated: {suggested_link}"
                            modified = True
                    if modified:
                        r['file'].write_text(content, encoding='utf-8')
                        updated += 1
                except:
                    pass
        
        return {"status": "success", "updated": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """Route a query to the appropriate AI model."""
    try:
        local_result = None
        if request.vault_path:
            local_result = check_local_knowledge(request.vault_path, request.query)
        
        recommendation = recommend_assistant(request.query)
        
        if isinstance(recommendation, tuple):
            model_key, description = recommendation
            model = model_key
            confidence = 0.5
        else:
            model = recommendation.get("model", "default")
            confidence = recommendation.get("confidence", 0.5)
        
        return RouteResponse(
            recommended_model=model,
            confidence=confidence,
            local_knowledge=local_result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/maintain", response_model=MaintainResponse)
async def run_maintenance(request: MaintainRequest):
    """Run daily maintenance on vault."""
    try:
        expired = find_expired_notes(request.vault_path)
        duplicates, notes = find_duplicate_titles(request.vault_path)
        orphaned = find_orphaned_links(request.vault_path)
        
        archived = 0
        if request.archive:
            archived = archive_expired_notes(request.vault_path, expired)
        
        return MaintainResponse(
            total_notes=len(notes),
            expired_count=len(expired),
            duplicate_count=len(duplicates),
            orphaned_count=len(orphaned),
            archived=archived,
            expired_notes=[{
                "title": n["title"],
                "date": n["date"],
                "age_days": n["age_days"],
            } for n in expired],
            duplicate_titles=duplicates,
            orphaned_links=[{
                "file": o["file"].name,
                "broken_link": o["broken_link"],
            } for o in orphaned]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
