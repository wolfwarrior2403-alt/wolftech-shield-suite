"""Template helper shared by all routes."""
from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from .rules.base import DISCLAIMER

BASE = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE / "templates"))
templates.env.globals["health_enabled"] = False


def render(request: Request, name: str, status_code: int = 200, **context):
    context.setdefault("disclaimer", DISCLAIMER)
    context.setdefault("firm", None)
    return templates.TemplateResponse(request=request, name=name, context=context, status_code=status_code)
