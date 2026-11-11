"""Wolftech Shield Suite - FastAPI app."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from . import db
from .compliance import service
from .compliance.routes import load_firm, router as compliance_router
from .models import Firm
from .seed import reset_demo, seed_demo
from .web import BASE, render

SECURITY_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self'; "
                               "script-src 'none'; object-src 'self'; form-action 'self'; "
                               "frame-ancestors 'self'; base-uri 'self'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "SAMEORIGIN",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
}

Db = Annotated[Session, Depends(db.get_session)]


def create_app(db_url: str | None = None, seed: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db.init_db(db_url)
        if seed:
            with Session(db.get_engine()) as session:
                seed_demo(session)
        yield

    app = FastAPI(title="Wolftech Shield Suite", docs_url=None, redoc_url=None, openapi_url=None,
                  lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
    app.include_router(compliance_router)

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        for key, value in SECURITY_HEADERS.items():
            response.headers.setdefault(key, value)
        return response

    @app.get("/")
    def home(request: Request, session: Db):
        firms = session.exec(select(Firm).order_by(Firm.is_demo.desc(), Firm.id)).all()
        return render(request, "home.html", firms=firms, deadline=service.next_deadline())

    @app.get("/firms/{firm_id}")
    def workspace(request: Request, firm_id: int, session: Db):
        firm = load_firm(session, firm_id)
        inventory = service.get_inventory(session, firm_id)
        return render(
            request, "workspace.html", firm=firm,
            dpdp=service.dpdp_assessment(session, firm),
            health=None,
            deadlines=service.deadlines(),
            inventory_done=sum(1 for i in inventory if i.id is not None),
        )

    @app.post("/demo/reset")
    def demo_reset(session: Db):
        firm = reset_demo(session)
        return RedirectResponse(f"/firms/{firm.id}", status_code=303)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


app = create_app()
