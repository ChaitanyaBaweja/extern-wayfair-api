"""Dashboard template router — serves the P5 dashboard HTML template.

GET /api/dashboard/template returns the static HTML template that P5 uses
to assemble category dashboards. The template still contains {{PLACEHOLDER}}
tokens which P5 replaces at runtime.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..config import DASHBOARD_TEMPLATE

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/template", response_class=Response)
async def get_dashboard_template() -> Response:
    """Return the dashboard HTML template as-is, with {{PLACEHOLDER}} tokens intact."""
    if not DASHBOARD_TEMPLATE.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard template missing on server. Expected at {DASHBOARD_TEMPLATE.name}.",
        )

    with open(DASHBOARD_TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()

    return Response(
        content=html,
        media_type="text/html; charset=utf-8",
        headers={"Cache-Control": "no-store"},
    )
