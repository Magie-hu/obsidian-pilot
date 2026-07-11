"""Obsidian Pilot API - Main FastAPI Application
Copyright (c) 2026 NingXiaoBan
Licensed under MIT License
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger("obsidian_pilot_api")


# ---------------------------------------------------------------------------
# Error classes
# ---------------------------------------------------------------------------

class VaultError(Exception):
    """Raised when a vault path is invalid or inaccessible."""


class NoteError(Exception):
    """Raised when a note operation fails."""


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class VaultRequest(BaseModel):
    vault_path: str = Field(..., min_length=1, description="Absolute or relative path to the Obsidian vault.")

    @field_validator("vault_path")
    @classmethod
    def validate_vault(cls, v: str) -> str:
        path = Path(v).resolve()
        if not path.exists():
            raise ValueError(f"Vault path does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"Vault path is not a directory: {v}")
        return str(path)


class NoteRequest(BaseModel):
    content: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1, max_length=255)


class ScanRequest(BaseModel):
    vault_path: str
    dry_run: bool = True


class LinkRequest(BaseModel):
    vault_path: str
    apply: bool = False


class RouteRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    vault_path: Optional[str] = None


class MaintainRequest(BaseModel):
    vault_path: str
    archive: bool = False


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


# ---------------------------------------------------------------------------
# Import core functions (lazy to avoid circular import)
# ---------------------------------------------------------------------------

_core_funcs = {}


def _load_core():
    """Lazy-load core module functions."""
    if _core_funcs:
        return _core_funcs

    # Try relative path from this file
    candidates = [
        Path(__file__).parent.parent.parent / "src",
        Path(__file__).parent.parent / "src",
        Path(__file__).parent.parent.parent.parent / "obsidian pilot" / "src",
    ]
    for candidate in candidates:
        if candidate.exists() and (candidate / "init.py").exists():
            if str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
            break
    else:
        # Fallback: try installed package
        project_root = Path(__file__).parent.parent.parent / "obsidian pilot" / "src"
        if not project_root.exists():
            project_root = Path(__file__).parent.parent / "src"
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

    from init import (
        create_folder_structure, create_templates, create_index_page, FOLDER_TEMPLATES,
        show_welcome, show_plugin_guide,
    )
    from note_import import classify_note, scan_notes, apply_changes
    from link import extract_titles_and_slugs, find_missing_links, detect_isolated_notes, apply_link_updates
    from route import check_local_knowledge, recommend_assistant
    from maintain import find_expired_notes, find_duplicate_titles, find_orphaned_links, archive_expired_notes

    _core_funcs.update(locals())
    return _core_funcs


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class InitResponse(BaseModel):
    status: str
    message: str
    folders_created: int
    templates_created: int


class ScanResponseItem(BaseModel):
    file: str
    title: str
    category: str
    needs_update: bool


class ScanResponse(PaginatedResponse):
    category_counts: dict = {}
    uncategorized: list = []


class LinkReportResponseItem(BaseModel):
    file: str
    title: str
    slug: str
    missing: list


class LinkReportResponse(PaginatedResponse):
    missing_links: list = []
    isolated_notes: list = []


class RouteResponse(BaseModel):
    recommended_model: str
    confidence: float
    local_knowledge: Optional[str] = None


class MaintainResponse(PaginatedResponse):
    expired_count: int = 0
    duplicate_count: int = 0
    orphaned_count: int = 0
    archived: int = 0
    expired_notes: list = []
    duplicate_titles: dict = {}
    orphaned_links: list = []


# ---------------------------------------------------------------------------
# App lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger.info("Obsidian Pilot API starting")
    yield
    # Shutdown
    logger.info("Obsidian Pilot API shutting down")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    app = FastAPI(
        title="Obsidian Pilot API",
        description="LLM-Wiki Bridge Backend API — manages Obsidian vaults with automated note classification, link analysis, and AI routing.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom exception handler for validation errors
    @app.exception_handler(VaultError)
    async def vault_error_handler(request: Request, exc: VaultError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(NoteError)
    async def note_error_handler(request: Request, exc: NoteError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paginate(items: list, page: int = 1, page_size: int = 50) -> dict:
    """Paginate a flat list and return a dict compatible with PaginatedResponse."""
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "items": items[start:end],
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["status"])
async def root():
    return {
        "service": "Obsidian Pilot API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["status"])
async def health_check():
    return {"status": "healthy"}


@app.post("/init", response_model=InitResponse, tags=["vault"])
async def init_vault(request: VaultRequest):
    """Initialize a new LLM-Wiki vault."""
    try:
        core = _load_core()
        vault_path = request.vault_path
        template_name = "llm-wiki"

        core["create_folder_structure"](vault_path, template_name)
        core["create_templates"](vault_path)
        core["create_index_page"](vault_path, template_name)

        return InitResponse(
            status="success",
            message=f"Vault initialized at {vault_path}",
            folders_created=len(core["FOLDER_TEMPLATES"].get(template_name, {}).get("folders", [])),
            templates_created=1,
        )
    except Exception as e:
        logger.exception("Failed to initialize vault")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/import", response_model=ScanResponse, tags=["vault"])
async def import_notes(request: VaultRequest, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200)):
    """Scan and classify all notes in vault."""
    try:
        core = _load_core()
        results, category_counts, uncategorized = core["scan_notes"](request.vault_path, dry_run=True)

        category_dict = dict(category_counts)
        uncategorized_names = [f.name for f, t in uncategorized]

        scan_items = [
            ScanResponseItem(
                file=r["file"],
                title=r["title"],
                category=r["category"],
                needs_update=r.get("needs_update", False),
            )
            for r in results
        ]

        paginated = _paginate(scan_items, page, page_size)
        total = len(scan_items)

        return ScanResponse(
            total=total,
            page=paginated["page"],
            page_size=paginated["page_size"],
            items=paginated["items"],
            category_counts=category_dict,
            uncategorized=uncategorized_names,
        )
    except Exception as e:
        logger.exception("Failed to scan vault")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/import/apply", tags=["vault"])
async def apply_import(request: VaultRequest):
    """Apply note classification changes."""
    try:
        core = _load_core()
        results, _, _ = core["scan_notes"](request.vault_path, dry_run=False)
        updated = core["apply_changes"](request.vault_path, results)
        return {"status": "success", "updated": updated}
    except Exception as e:
        logger.exception("Failed to apply import changes")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/links/report", response_model=LinkReportResponse, tags=["links"])
async def get_link_report(
    request: LinkRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Get link analysis report for vault."""
    try:
        core = _load_core()
        title_map = core["extract_titles_and_slugs"](request.vault_path)

        results = []
        missing_links = []
        for title_key, info in title_map.items():
            try:
                content = info["file"].read_text(encoding="utf-8")
                missing = core["find_missing_links"](content, title_map, info["slug"])
                results.append(
                    LinkReportResponseItem(
                        file=str(info["file"]),
                        title=info["title"],
                        slug=info["slug"],
                        missing=missing,
                    )
                )
                for m in missing:
                    missing_links.append(
                        {
                            "source": info["title"],
                            "suggested": m["suggested"],
                            "current_file": m["current_file"],
                        }
                    )
            except Exception:
                pass

        isolated = core["detect_isolated_notes"](request.vault_path, title_map)

        paginated = _paginate(results, page, page_size)
        return LinkReportResponse(
            total=len(results),
            page=paginated["page"],
            page_size=paginated["page_size"],
            items=paginated["items"],
            missing_links=missing_links,
            isolated_notes=isolated,
        )
    except Exception as e:
        logger.exception("Failed to generate link report")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/links/apply", tags=["links"])
async def apply_links(request: LinkRequest):
    """Apply link suggestions."""
    try:
        core = _load_core()
        title_map = core["extract_titles_and_slugs"](request.vault_path)

        results = []
        for title_key, info in title_map.items():
            try:
                content = info["file"].read_text(encoding="utf-8")
                missing = core["find_missing_links"](content, title_map, info["slug"])
                results.append({"file": info["file"], "title": info["title"], "slug": info["slug"], "missing": missing})
            except Exception:
                pass

        isolated = core["detect_isolated_notes"](request.vault_path, title_map)

        updated = 0
        for r in results:
            if r.get("missing"):
                try:
                    content = r["file"].read_text(encoding="utf-8")
                    modified = False
                    for m in r["missing"]:
                        suggested_link = f"[[{m['suggested']}]]"
                        if suggested_link not in content:
                            content = content.rstrip() + f"\n\nRelated: {suggested_link}"
                            modified = True
                    if modified:
                        r["file"].write_text(content, encoding="utf-8")
                        updated += 1
                except Exception:
                    pass

        return {"status": "success", "updated": updated}
    except Exception as e:
        logger.exception("Failed to apply link suggestions")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route", response_model=RouteResponse, tags=["routing"])
async def route_query(request: RouteRequest):
    """Route a query to the appropriate AI model."""
    try:
        core = _load_core()
        local_result = None
        if request.vault_path:
            local_result = core["check_local_knowledge"](request.vault_path, request.query)

        recommendation = core["recommend_assistant"](request.query)

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
            local_knowledge=local_result,
        )
    except Exception as e:
        logger.exception("Failed to route query")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/maintain", response_model=MaintainResponse, tags=["maintenance"])
async def run_maintenance(
    request: MaintainRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """Run daily maintenance on vault."""
    try:
        core = _load_core()
        expired = core["find_expired_notes"](request.vault_path)
        duplicates, notes = core["find_duplicate_titles"](request.vault_path)
        orphaned = core["find_orphaned_links"](request.vault_path)

        archived = 0
        if request.archive:
            archived = core["archive_expired_notes"](request.vault_path, expired)

        expired_items = [{"title": n["title"], "date": n["date"], "age_days": n["age_days"]} for n in expired]
        orphaned_items = [{"file": o["file"].name, "broken_link": o["broken_link"]} for o in orphaned]

        # Expired and orphaned are paginated
        exp_paginated = _paginate(expired_items, page, page_size)
        orn_paginated = _paginate(orphaned_items, page, page_size)

        return MaintainResponse(
            total=max(len(notes), len(expired), len(orphaned)),
            page=exp_paginated["page"],
            page_size=exp_paginated["page_size"],
            items=exp_paginated["items"],
            expired_count=len(expired),
            duplicate_count=len(duplicates),
            orphaned_count=len(orphaned),
            archived=archived,
            expired_notes=exp_paginated["items"],
            duplicate_titles=duplicates,
            orphaned_links=orn_paginated["items"],
        )
    except Exception as e:
        logger.exception("Failed to run maintenance")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Pro endpoints
# ---------------------------------------------------------------------------

class TemplateRequest(BaseModel):
    vault_path: str
    templates: Optional[list] = None
    preset: Optional[str] = None


class TemplateListResponse(BaseModel):
    total: int
    templates: list


class TemplateGenerateResponse(BaseModel):
    status: str
    generated: int
    skipped: int
    errors: list


class RepairRequest(BaseModel):
    vault_path: str
    batch: bool = False
    apply: bool = False
    dry_run: bool = True


class RepairResponse(BaseModel):
    status: str
    dry_run: bool
    repairs: list
    stats: dict


class ConflictRequest(BaseModel):
    vault_path: str
    resolve: bool = False
    auto: bool = False


class ConflictResponse(BaseModel):
    total_conflicts: int
    resolved: int
    unresolved: int
    conflicts: list
    type_counts: dict


class ExportRequest(BaseModel):
    vault_path: str
    format: str = "zip"


class ExportResponse(BaseModel):
    status: str
    format: str
    files: int
    output: str


class SkillExportRequest(BaseModel):
    vault_path: str
    output: Optional[str] = None


class SkillExportResponse(BaseModel):
    status: str
    exported_skills: int
    output_path: str


class LicenseRequest(BaseModel):
    key: str
    vault_path: Optional[str] = None


class LicenseResponse(BaseModel):
    valid: bool
    product: str
    expires: Optional[str] = None
    registered: bool = False


class LicenseRegisterResponse(BaseModel):
    status: str
    valid: bool
    registered_at: str


@app.post("/pro/templates/list", response_model=TemplateListResponse, tags=["pro"])
async def list_templates(request: VaultRequest):
    """List available Pro templates."""
    try:
        # Lazy load pro module
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from templater import list_available_templates
        templates = list_available_templates()
        return TemplateListResponse(total=len(templates), templates=templates)
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to list templates")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/templates/generate", response_model=TemplateGenerateResponse, tags=["pro"])
async def generate_templates(request: TemplateRequest):
    """Generate Pro Templater templates."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from templater import generate_templates
        result = generate_templates(request.vault_path, selected=request.templates, preset=request.preset)
        return TemplateGenerateResponse(
            status="success",
            generated=len(result["generated"]),
            skipped=len(result["skipped"]),
            errors=result["errors"],
        )
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to generate templates")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/repair", response_model=RepairResponse, tags=["pro"])
async def repair_links(request: RepairRequest):
    """Repair broken links (Pro)."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from repair import LinkRepair
        repair = LinkRepair(request.vault_path)

        if request.batch:
            result = repair.batch_repair()
            return RepairResponse(
                status="success",
                dry_run=False,
                repairs=[],
                stats={
                    "repaired": result["repaired"],
                    "unresolved": result["unresolved"],
                    "total_links": repair.stats["total_links"],
                    "broken_links": repair.stats["broken_links"],
                },
            )
        else:
            result = repair.repair_links(dry_run=request.dry_run)
            return RepairResponse(
                status="success",
                dry_run=request.dry_run,
                repairs=result["repairs"],
                stats=result["stats"],
            )
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to repair links")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/conflict", response_model=ConflictResponse, tags=["pro"])
async def check_conflicts(request: ConflictRequest):
    """Detect and optionally resolve conflicts (Pro)."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from conflict import ConflictDetector
        detector = ConflictDetector(request.vault_path)
        conflicts = detector.scan_conflicts()

        type_counts = {}
        for c in conflicts:
            t = c["type"]
            type_counts[t] = type_counts.get(t, 0) + 1

        resolved_count = 0
        if request.resolve:
            result = detector.resolve_conflicts(auto_resolve=request.auto)
            resolved_count = result["resolved"]

        return ConflictResponse(
            total_conflicts=len(conflicts),
            resolved=resolved_count,
            unresolved=len(conflicts) - resolved_count,
            conflicts=conflicts,
            type_counts=type_counts,
        )
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to detect conflicts")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/export", response_model=ExportResponse, tags=["pro"])
async def export_knowledge(request: ExportRequest):
    """Export knowledge base (Pro)."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from export import KnowledgeBaseExporter
        exporter = KnowledgeBaseExporter(request.vault_path)
        result = exporter.export_all(format=request.format)

        return ExportResponse(
            status="success",
            format=result["format"],
            files=result.get("exported_files", 0),
            output=result.get("zip_path", result.get("output_dir", "N/A")),
        )
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to export knowledge base")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/skill-export", response_model=SkillExportResponse, tags=["pro"])
async def export_skills(request: SkillExportRequest):
    """Export skills as Hermes skill packages (Pro)."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from skill_pack import SkillPackExporter
        exporter = SkillPackExporter(request.vault_path, request.output)
        result = exporter.export_skills()
        return SkillExportResponse(
            status="success",
            exported_skills=result["exported_skills"],
            output_path=result["output_path"],
        )
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to export skills")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/license/register", response_model=LicenseRegisterResponse, tags=["pro"])
async def register_license(request: LicenseRequest):
    """Register a Pro license key."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from license_check import register_license, LicenseError
        try:
            info = register_license(request.vault_path or "/tmp", request.key)
            return LicenseRegisterResponse(
                status="success",
                valid=info["valid"],
                registered_at=info.get("registered_at", ""),
            )
        except LicenseError as e:
            raise HTTPException(status_code=400, detail=str(e))
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to register license")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pro/license/verify", response_model=LicenseResponse, tags=["pro"])
async def verify_license_endpoint(request: LicenseRequest):
    """Verify a Pro license key."""
    try:
        pro_src = Path(__file__).parent.parent.parent.parent / "obsidian-pilot-pro" / "src"
        if not pro_src.exists():
            pro_src = Path(__file__).parent.parent / "obsidian-pilot-pro" / "src"
        if str(pro_src) not in sys.path:
            sys.path.insert(0, str(pro_src))
        from license_check import verify_license, LicenseError, check_license_installed
        try:
            info = verify_license(request.key)
            registered = False
            if request.vault_path:
                registered = check_license_installed(request.vault_path)
            return LicenseResponse(
                valid=info["valid"],
                product=info["product"],
                expires=info.get("expires"),
                registered=registered,
            )
        except LicenseError as e:
            return LicenseResponse(valid=False, product="", registered=False)
    except ImportError:
        raise HTTPException(status_code=503, detail="Pro module not installed")
    except Exception as e:
        logger.exception("Failed to verify license")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

def run_server():
    """Run the API server."""
    import uvicorn
    logger.info("Starting Obsidian Pilot API server")
    uvicorn.run(
        "obsidian_pilot_api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
