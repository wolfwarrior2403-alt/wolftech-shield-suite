"""Branded PDF writer (reportlab). Dark Wolftech header band, white body so the
draft prints cleanly for a lawyer's mark-up. The disclaimer is on every page."""
from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

BRAND = "Wolftech AI Labs"
BG = colors.HexColor("#0a0a0c")
RED = colors.HexColor("#ff2e3d")
CREAM = colors.HexColor("#f2efe9")
INK = colors.HexColor("#1b1b1f")
GREY = colors.HexColor("#5c5c66")
RULE = colors.HexColor("#d9d6cf")

BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14, textColor=INK, alignment=TA_LEFT, spaceAfter=6)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=INK, spaceAfter=2)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=INK, spaceBefore=10, spaceAfter=5)
META = ParagraphStyle("meta", fontName="Helvetica", fontSize=9, leading=12, textColor=GREY, spaceAfter=8)
NOTE = ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=9, leading=12.5, textColor=GREY,
                      borderColor=RULE, borderWidth=0.6, borderPadding=6, spaceBefore=8, spaceAfter=10)
WARN = ParagraphStyle("warn", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=RED, spaceAfter=10)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK)
CELL_H = ParagraphStyle("cellh", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=CREAM)
SMALL = ParagraphStyle("small", fontName="Helvetica", fontSize=8, leading=10.5, textColor=GREY)


def _p(text: str, style=BODY) -> Paragraph:
    return Paragraph(escape(str(text)), style)


def _decorate(disclaimer: str, product: str):
    def draw(canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setFillColor(BG)
        canvas.rect(0, height - 22 * mm, width, 22 * mm, stroke=0, fill=1)
        canvas.setFillColor(RED)
        canvas.rect(0, height - 23.2 * mm, width, 1.2 * mm, stroke=0, fill=1)
        canvas.setFillColor(CREAM)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(18 * mm, height - 13 * mm, BRAND.upper())
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(width - 18 * mm, height - 13 * mm, product)
        canvas.setStrokeColor(RULE)
        canvas.line(18 * mm, 16 * mm, width - 18 * mm, 16 * mm)
        canvas.setFillColor(RED)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18 * mm, 11.5 * mm, disclaimer)
        canvas.setFillColor(GREY)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(width - 18 * mm, 11.5 * mm, f"Page {doc.page}")
        canvas.restoreState()
    return draw


def _table(headers: list[str], rows: list[list[str]], width: float) -> Table:
    data = [[_p(h, CELL_H) for h in headers]] + [[_p(c, CELL) for c in row] for row in rows]
    n = len(headers)
    lengths = [max([len(str(headers[i]))] + [len(str(r[i])) for r in rows if i < len(r)]) for i in range(n)]
    capped = [min(max(l, 6), 60) for l in lengths]
    total = sum(capped)
    col_widths = [width * c / total for c in capped]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f5f0")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def render_pdf(doc, product: str = "Compliance Kit") -> bytes:
    """doc: an object with title, firm_name, generated_on, disclaimer, blocks, sources()."""
    buf = BytesIO()
    pdf = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=31 * mm, bottomMargin=22 * mm,
        title=f"{doc.title} - {doc.firm_name}", author=BRAND, subject=doc.disclaimer,
    )
    width = A4[0] - 36 * mm
    story = [
        _p(doc.title, H1),
        _p(f"{doc.firm_name}  |  Generated {doc.generated_on:%d %B %Y}  |  Fictional sample data may be shown in demo workspaces", META),
        _p(doc.disclaimer, WARN),
    ]
    for block in doc.blocks:
        kind = block[0]
        if kind == "h2":
            story.append(_p(block[1], H2))
        elif kind == "p":
            story.append(_p(block[1]))
        elif kind == "note":
            story.append(_p(block[1], NOTE))
        elif kind in ("ul", "ol"):
            items = [ListItem(_p(i), leftIndent=14) for i in block[1]]
            story.append(ListFlowable(items, bulletType="bullet" if kind == "ul" else "1",
                                      bulletFontSize=8 if kind == "ul" else 9, leftIndent=14))
            story.append(Spacer(1, 4))
        elif kind == "table":
            story.append(_table(block[1], block[2], width))
            story.append(Spacer(1, 6))
    sources = doc.sources()
    if sources:
        story.append(_p("Sources", H2))
        story.append(_table(["Rule ID", "Citation", "Link"], [list(s) for s in sources], width))
    story.append(Spacer(1, 8))
    story.append(_p(f"Prepared with {BRAND} Shield Suite. {doc.disclaimer}", SMALL))
    draw = _decorate(doc.disclaimer, product)
    pdf.build(story, onFirstPage=draw, onLaterPages=draw)
    return buf.getvalue()
