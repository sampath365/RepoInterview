#!/usr/bin/env python3
"""Generate the 'Complete C# Interview Questions and Answers - 500 Questions' PDF.

Reads the per-category JSON files in data/ and produces a single, navigable PDF
with a cover page, table of contents, per-category sections and 500 Q&A entries.
"""

from __future__ import annotations

import glob
import json
import os
from collections import Counter
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, "data")
OUTPUT = os.path.join(HERE, "dist", "CSharp-Interview-Questions-500.pdf")

# Brand palette (close to the .NET / Visual Studio purple)
BRAND = colors.HexColor("#68217A")
BRAND_DARK = colors.HexColor("#3C0F4A")
ACCENT = colors.HexColor("#8A2BE2")
INK = colors.HexColor("#1F2430")
MUTED = colors.HexColor("#5A6472")
RULE = colors.HexColor("#D9DCE3")
CODE_BG = colors.HexColor("#F4F5F7")
CODE_BORDER = colors.HexColor("#DADDE3")
TAG_BG = colors.HexColor("#EFE7F5")

DIFF_COLORS = {
    "Beginner": colors.HexColor("#1B7F3B"),
    "Intermediate": colors.HexColor("#B25E00"),
    "Advanced": colors.HexColor("#B32020"),
}


def load_categories():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
    categories = []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        categories.append(data)
    return categories


def build_styles():
    ss = getSampleStyleSheet()
    styles = {}
    styles["cover_title"] = ParagraphStyle(
        "cover_title", parent=ss["Title"], fontName="Helvetica-Bold",
        fontSize=34, leading=40, textColor=BRAND_DARK, alignment=TA_CENTER,
        spaceAfter=6,
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", parent=ss["Normal"], fontName="Helvetica-Bold",
        fontSize=20, leading=26, textColor=BRAND, alignment=TA_CENTER,
    )
    styles["cover_tag"] = ParagraphStyle(
        "cover_tag", parent=ss["Normal"], fontName="Helvetica", fontSize=12,
        leading=18, textColor=MUTED, alignment=TA_CENTER,
    )
    styles["cat_title"] = ParagraphStyle(
        "cat_title", parent=ss["Heading1"], fontName="Helvetica-Bold",
        fontSize=22, leading=27, textColor=BRAND_DARK, spaceBefore=4, spaceAfter=4,
    )
    styles["cat_sub"] = ParagraphStyle(
        "cat_sub", parent=ss["Normal"], fontName="Helvetica", fontSize=10.5,
        leading=14, textColor=MUTED, spaceAfter=10,
    )
    styles["question"] = ParagraphStyle(
        "question", parent=ss["Normal"], fontName="Helvetica-Bold",
        fontSize=12, leading=16, textColor=INK, spaceBefore=2, spaceAfter=4,
    )
    styles["answer"] = ParagraphStyle(
        "answer", parent=ss["Normal"], fontName="Helvetica", fontSize=10.5,
        leading=15.5, textColor=INK, alignment=TA_LEFT, spaceAfter=4,
    )
    styles["meta"] = ParagraphStyle(
        "meta", parent=ss["Normal"], fontName="Helvetica", fontSize=8.5,
        leading=12, textColor=MUTED,
    )
    styles["code"] = ParagraphStyle(
        "code", parent=ss["Code"], fontName="Courier", fontSize=7.4,
        leading=10.2, textColor=colors.HexColor("#0B2E13"),
    )
    styles["toc_head"] = ParagraphStyle(
        "toc_head", parent=ss["Heading1"], fontName="Helvetica-Bold",
        fontSize=20, leading=24, textColor=BRAND_DARK, spaceAfter=12,
    )
    return styles


class CatalogDoc(BaseDocTemplate):
    """Doc template with running header/footer and TOC bookkeeping."""

    def __init__(self, filename, title, **kw):
        super().__init__(filename, pagesize=A4, title=title,
                         author="OpenHands", subject="C# interview preparation",
                         creator="C# Interview Questions generator", **kw)
        self._toc_entries = []
        frame = Frame(18 * mm, 18 * mm, A4[0] - 36 * mm, A4[1] - 40 * mm, id="main")
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame], onPage=self._cover_page),
            PageTemplate(id="body", frames=[frame], onPage=self._body_page),
        ])

    def _cover_page(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BRAND)
        canvas.rect(0, A4[1] - 14 * mm, A4[0], 14 * mm, stroke=0, fill=1)
        canvas.setFillColor(BRAND_DARK)
        canvas.rect(0, 0, A4[0], 8 * mm, stroke=0, fill=1)
        canvas.restoreState()

    def _body_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.6)
        y = A4[1] - 14 * mm
        canvas.line(18 * mm, y, A4[0] - 18 * mm, y)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, y + 2.2 * mm, "Complete C# Interview Questions and Answers")
        canvas.drawRightString(A4[0] - 18 * mm, y + 2.2 * mm, "500 Questions")
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "cat_title":
            text = flowable.getPlainText()
            # Stable key so repeated build passes converge on the same bookmark.
            key = "cat-" + "".join(c if c.isalnum() else "-" for c in text.lower())
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (0, text, self.page, key))
            self.canv.addOutlineEntry(text, key, level=0)


def code_box(code, styles):
    pre = Preformatted(code, styles["code"])
    tbl = Table([[pre]], colWidths=[A4[0] - 36 * mm - 2])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("BOX", (0, 0), (-1, -1), 0.6, CODE_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def meta_line(q, styles):
    diff = q.get("difficulty", "")
    diff_color = DIFF_COLORS.get(diff, MUTED)
    parts = [f'<font color="{diff_color.hexval()}"><b>{diff}</b></font>']
    if q.get("tags"):
        parts.append("&nbsp;&nbsp;|&nbsp;&nbsp;" + "  ".join(f"#{t}" for t in q["tags"]))
    if q.get("references"):
        links = "  ".join(f'<link href="{u}">reference</link>' for u in q["references"])
        parts.append("&nbsp;&nbsp;|&nbsp;&nbsp;" + links)
    return Paragraph("&nbsp;&nbsp;".join(parts), styles["meta"])


def category_intro(cat):
    n = len(cat["questions"])
    return Paragraph(
        f"{n} questions covering {cat['category'].lower()}.",
        # placeholder replaced below
    )


def build_story(categories, styles):
    story = []

    # ---- Cover page ----
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("Complete", styles["cover_tag"]))
    story.append(Paragraph("C# Interview Questions", styles["cover_title"]))
    story.append(Paragraph("and Answers", styles["cover_title"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("500 Questions", styles["cover_sub"]))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "Across 20 topic areas &mdash; from language basics and OOP to async, "
        "LINQ, ASP.NET Core and EF Core.",
        styles["cover_tag"],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Difficulty levels: Beginner &middot; Intermediate &middot; Advanced",
        styles["cover_tag"],
    ))
    story.append(Spacer(1, 30 * mm))
    total = sum(len(c["questions"]) for c in categories)
    story.append(Paragraph(f"{total} curated questions", styles["cover_sub"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(date.today().strftime("%B %Y"), styles["cover_tag"]))
    story.append(PageBreak())

    # ---- Table of contents ----
    story.append(Paragraph("Contents", styles["toc_head"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("toc0", fontName="Helvetica-Bold", fontSize=11, leading=17,
                       textColor=BRAND_DARK, leftIndent=0),
    ]
    story.append(toc)
    story.append(PageBreak())

    # ---- Category sections ----
    counter = 0
    for idx, cat in enumerate(categories):
        if idx > 0:
            story.append(PageBreak())
        cat_title = Paragraph(cat["category"], styles["cat_title"])
        story.append(cat_title)
        mix = Counter(q.get("difficulty", "") for q in cat["questions"])
        mix_txt = " &middot; ".join(
            f"{mix[lvl]} {lvl}" for lvl in ("Beginner", "Intermediate", "Advanced") if mix.get(lvl)
        )
        story.append(Paragraph(
            f'{len(cat["questions"])} questions &middot; {mix_txt}',
            styles["cat_sub"],
        ))

        for q in cat["questions"]:
            counter += 1
            block = []
            block.append(Paragraph(
                f'<font color="{BRAND.hexval()}">{counter}.</font>&nbsp; {q["question"]}',
                styles["question"],
            ))
            block.append(meta_line(q, styles))
            block.append(Spacer(1, 3))
            block.append(Paragraph(q["answer"], styles["answer"]))
            if q.get("code"):
                block.append(Spacer(1, 3))
                block.append(code_box(q["code"], styles))
            block.append(Spacer(1, 9))
            story.append(KeepTogether(block))

    return story


def main():
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    categories = load_categories()
    styles = build_styles()
    title = "Complete C# Interview Questions and Answers - 500 Questions"
    doc = CatalogDoc(OUTPUT, title)
    story = build_story(categories, styles)

    # multiBuild so the TOC page numbers resolve.
    doc.multiBuild(story)
    total = sum(len(c["questions"]) for c in categories)
    print(f"Wrote {OUTPUT}")
    print(f"Categories: {len(categories)}  Questions: {total}")


if __name__ == "__main__":
    main()
