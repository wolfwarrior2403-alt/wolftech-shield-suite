"""Privacy Shield pages. Plain HTML forms, no JavaScript. Nothing uploaded is stored:
the file is masked in memory and returned as a download."""
from __future__ import annotations

import io
import os
import zipfile

from fastapi import APIRouter, Request
from starlette.datastructures import UploadFile
from fastapi.responses import Response

from ..web import render
from .mask import MAX_BYTES, SAMPLE_CSV, MaskError, mask_csv, unmask_text

router = APIRouter()

README = """Wolftech Shield Suite - Privacy Shield

masked.csv
  Personal data replaced with consistent fake values. Safe to use for testing,
  development and AI tools (Claude Code, Gemini, ChatGPT).

KEY-KEEP-PRIVATE.csv
  Maps every fake value back to the real one. Treat it like the original data:
  keep it on the firm's machine, never upload it to any AI tool, never email it.

To put real values back into a masked file or an AI tool's answer:
  python -m app.shield.mask --unmask answer.txt KEY-KEEP-PRIVATE.csv
or use "Restore real values" on the Privacy Shield page.

Masking finds names, emails, phone numbers, PAN, Aadhaar, GSTIN, dates of birth
and addresses by column name and by pattern. Check the masked file before you
share it: unusual columns (for example a free-text field with a client's
nickname) may need a manual look.
"""


def public_demo() -> bool:
    """On the public demo (Vercel) only the built-in sample can be masked."""
    return bool(os.environ.get("WOLFTECH_PUBLIC_DEMO") or os.environ.get("VERCEL"))


def _page(request: Request, error: str = "", status_code: int = 200):
    sample = mask_csv(SAMPLE_CSV)
    return render(request, "privacy_shield.html", status_code=status_code, error=error, sample=sample,
                  public_demo=public_demo(), max_mb=MAX_BYTES // (1024 * 1024))


@router.get("/privacy-shield")
def page(request: Request):
    return _page(request)


def _zip(masked: str, key: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("masked.csv", masked)
        z.writestr("KEY-KEEP-PRIVATE.csv", key)
        z.writestr("README.txt", README)
    return buf.getvalue()


@router.post("/privacy-shield/mask")
async def mask(request: Request):
    form = await request.form()
    if form.get("use_sample") == "yes":
        data: bytes | str = SAMPLE_CSV
    elif public_demo():
        return _page(request, "This public demo only masks the built-in sample file. Run the Shield Suite on "
                              "your own computer to mask real data: it never leaves your machine.", 400)
    else:
        upload = form.get("file")
        if not isinstance(upload, UploadFile) or not upload.filename:
            return _page(request, "Choose a CSV file first.", 400)
        data = await upload.read(MAX_BYTES + 1)
    try:
        result = mask_csv(data)
    except MaskError as exc:
        return _page(request, str(exc), 400)
    return Response(_zip(result.masked_csv, result.key_csv), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="privacy-shield-masked.zip"',
                             "Cache-Control": "no-store"})


@router.post("/privacy-shield/unmask")
async def unmask(request: Request):
    if public_demo():
        return _page(request, "Restoring real values works only on your own computer, where the key file lives.", 400)
    form = await request.form()
    target, key = form.get("file"), form.get("key")
    if not (isinstance(target, UploadFile) and target.filename and isinstance(key, UploadFile) and key.filename):
        return _page(request, "Choose both the masked file and the key file.", 400)
    try:
        raw = await target.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise MaskError("File is too large.")
        restored = unmask_text(raw.decode("utf-8-sig", errors="replace"), await key.read(MAX_BYTES + 1))
    except MaskError as exc:
        return _page(request, str(exc), 400)
    name = target.filename.rsplit(".", 1)
    out = f"{name[0]}.restored.{name[1]}" if len(name) == 2 else f"{target.filename}.restored"
    return Response(restored.encode("utf-8"), media_type="text/plain; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{out}"', "Cache-Control": "no-store"})
