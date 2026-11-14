#!/usr/bin/env python3
"""Build an interview-questions PDF from a book folder.

Each book lives in books/<slug>/ with:
  book.json    metadata: {"title", "subtitle", "blurb", "kicker"}
  data/*.json  one file per category (see books/SCHEMA.md)

Usage:
  python3 tools/build_pdf.py books/<slug>
  python3 tools/build_pdf.py --all
"""

from __future__ import annotations

import argparse
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

BRAND = colors.HexColor("#68217A")
BRAND_DARK = colors.HexColor("#3C0F4A")
INK = colors.HexColor("#1F2430")
MUTED = colors.HexColor("#5A6472")
RULE = colors.HexColor("#D9DCE3")
CODE_BG = colors.HexColor("#F4F5F7")
CODE_BORDER = colors.HexColor("#DADDE3")

DIFF_COLORS = {
    "Beginner": colors.HexColor("#1B7F3B"),
    "Intermediate": colors.HexColor("#B25E00"),
    "Advanced": colors.HexColor("#B32020"),
}


def load_book(book_dir):
    with open(os.path.join(book_dir, "book.json"), encoding="utf-8") as fh:
        meta = json.load(fh)
    categories = []
    for path in sorted(glob.glob(os.path.join(book_dir, "data", "*.json"))):
        with open(path, encoding="utf-8") as fh:
            categories.append(json.load(fh))
    return meta, categories


def build_styles():
    ss = getSampleStyleSheet()
    s = {}
    s["cover_title"] = ParagraphStyle("cover_title", parent=ss["Title"], fontName="Helvetica-Bold",
                                      fontSize=32, leading=38, textColor=BRAND_DARK, alignment=TA_CENTER, spaceAfter=6)
    s["cover_sub"] = ParagraphStyle("cover_sub", parent=ss["Normal"], fontName="Helvetica-Bold",
                                    fontSize=19, leading=25, textColor=BRAND, alignment=TA_CENTER)
    s["cover_tag"] = ParagraphStyle("cover_tag", parent=ss["Normal"], fontName="Helvetica", fontSize=12,
                                    leading=18, textColor=MUTED, alignment=TA_CENTER)
    s["cat_title"] = ParagraphStyle("cat_title", parent=ss["Heading1"], fontName="Helvetica-Bold",
                                    fontSize=22, leading=27, textColor=BRAND_DARK, spaceBefore=4, spaceAfter=4)
    s["cat_sub"] = ParagraphStyle("cat_sub", parent=ss["Normal"], fontName="Helvetica", fontSize=10.5,
                                  leading=14, textColor=MUTED, spaceAfter=10)
    s["question"] = ParagraphStyle("question", parent=ss["Normal"], fontName="Helvetica-Bold",
                                   fontSize=12, leading=16, textColor=INK, spaceBefore=2, spaceAfter=4)
    s["answer"] = ParagraphStyle("answer", parent=ss["Normal"], fontName="Helvetica", fontSize=10.5,
                                 leading=15.5, textColor=INK, alignment=TA_LEFT, spaceAfter=4)
    s["meta"] = ParagraphStyle("meta", parent=ss["Normal"], fontName="Helvetica", fontSize=8.5,
                               leading=12, textColor=MUTED)
    s["code"] = ParagraphStyle("code", parent=ss["Code"], fontName="Courier", fontSize=7.4,
                               leading=10.2, textColor=colors.HexColor("#0B2E13"))
    s["toc_head"] = ParagraphStyle("toc_head", parent=ss["Heading1"], fontName="Helvetica-Bold",
                                   fontSize=20, leading=24, textColor=BRAND_DARK, spaceAfter=12)
    return s


class BookDoc(BaseDocTemplate):
    def __init__(self, filename, title, header, **kw):
        super().__init__(filename, pagesize=A4, title=title, author="OpenHands",
                         subject="Interview preparation", creator="Interview Questions generator", **kw)
        self.header = header
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
        canvas.drawString(18 * mm, y + 2.2 * mm, self.header)
        canvas.drawRightString(A4[0] - 18 * mm, y + 2.2 * mm, "500 Questions")
        canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
        canvas.drawCentredString(A4[0] / 2, 10 * mm, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "cat_title":
            text = flowable.getPlainText()
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


def build_story(meta, categories, styles):
    story = []
    total = sum(len(c["questions"]) for c in categories)

    story.append(Spacer(1, 38 * mm))
    story.append(Paragraph(meta.get("kicker", "Complete"), styles["cover_tag"]))
    story.append(Paragraph(meta["title"], styles["cover_title"]))
    if meta.get("subtitle"):
        story.append(Paragraph(meta["subtitle"], styles["cover_sub"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("500 Questions", styles["cover_sub"]))
    story.append(Spacer(1, 8 * mm))
    if meta.get("blurb"):
        story.append(Paragraph(meta["blurb"], styles["cover_tag"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Difficulty levels: Beginner &middot; Intermediate &middot; Advanced", styles["cover_tag"]))
    story.append(Spacer(1, 26 * mm))
    story.append(Paragraph(f"{total} curated questions", styles["cover_sub"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(date.today().strftime("%B %Y"), styles["cover_tag"]))
    story.append(PageBreak())

    story.append(Paragraph("Contents", styles["toc_head"]))
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle("toc0", fontName="Helvetica-Bold", fontSize=11, leading=17,
                                      textColor=BRAND_DARK, leftIndent=0)]
    story.append(toc)
    story.append(PageBreak())

    counter = 0
    for idx, cat in enumerate(categories):
        if idx > 0:
            story.append(PageBreak())
        story.append(Paragraph(cat["category"], styles["cat_title"]))
        mix = Counter(q.get("difficulty", "") for q in cat["questions"])
        mix_txt = " &middot; ".join(f"{mix[lvl]} {lvl}" for lvl in ("Beginner", "Intermediate", "Advanced") if mix.get(lvl))
        story.append(Paragraph(f'{len(cat["questions"])} questions &middot; {mix_txt}', styles["cat_sub"]))

        for q in cat["questions"]:
            counter += 1
            block = [Paragraph(f'<font color="{BRAND.hexval()}">{counter}.</font>&nbsp; {q["question"]}', styles["question"]),
                     meta_line(q, styles), Spacer(1, 3),
                     Paragraph(q["answer"], styles["answer"])]
            if q.get("code"):
                block += [Spacer(1, 3), code_box(q["code"], styles)]
            block.append(Spacer(1, 9))
            story.append(KeepTogether(block))
    return story


def build_book(book_dir, out_dir):
    meta, categories = load_book(book_dir)
    styles = build_styles()
    os.makedirs(out_dir, exist_ok=True)
    slug = os.path.basename(book_dir.rstrip("/"))
    out_path = os.path.join(out_dir, f"{slug}.pdf")
    doc = BookDoc(out_path, meta["title"], meta["title"])
    doc.multiBuild(build_story(meta, categories, styles))
    total = sum(len(c["questions"]) for c in categories)
    print(f"{slug}: {len(categories)} categories, {total} questions -> {out_path}")
    return out_path, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book_dir", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.all:
        dirs = sorted(d for d in glob.glob(os.path.join(here, "books", "*")) if os.path.isdir(d))
    else:
        dirs = [args.book_dir]
    grand = 0
    for d in dirs:
        _, n = build_book(d, os.path.join(here, args.out))
        grand += n
    print(f"TOTAL questions across books: {grand}")


if __name__ == "__main__":
    main()
