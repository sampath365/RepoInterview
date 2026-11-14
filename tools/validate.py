#!/usr/bin/env python3
"""Validate one or more interview books.

Usage:
  python3 tools/validate.py books/<slug> [books/<slug2> ...]
  python3 tools/validate.py --all
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter


def validate_book(book_dir):
    slug = os.path.basename(book_dir.rstrip("/"))
    errors, warnings = [], []
    meta_path = os.path.join(book_dir, "book.json")
    if not os.path.exists(meta_path):
        errors.append("missing book.json")
    files = sorted(glob.glob(os.path.join(book_dir, "data", "*.json")))
    if not files:
        errors.append("no data/*.json files")
        return slug, 0, 0, errors, warnings

    total = 0
    seen_ids = set()
    seen_questions = set()
    for path in files:
        name = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: invalid JSON ({exc})")
            continue
        qs = data.get("questions", [])
        if len(qs) != 25:
            errors.append(f"{name}: {len(qs)} questions (expected 25)")
        for key in ("category", "slug", "questions"):
            if key not in data:
                errors.append(f"{name}: missing '{key}'")
        for q in qs:
            total += 1
            qid = q.get("id", "?")
            for key in ("id", "difficulty", "question", "answer", "tags", "references"):
                if not q.get(key):
                    errors.append(f"{name}:{qid}: missing/empty '{key}'")
            if q.get("difficulty") not in ("Beginner", "Intermediate", "Advanced"):
                warnings.append(f"{name}:{qid}: unusual difficulty '{q.get('difficulty')}'")
            if q.get("question") and not q["question"].strip().endswith("?"):
                warnings.append(f"{name}:{qid}: question does not end with '?'")
            if qid in seen_ids:
                errors.append(f"{name}:{qid}: duplicate id")
            seen_ids.add(qid)
            qtext = (q.get("question") or "").strip().lower()
            if qtext in seen_questions:
                warnings.append(f"{name}:{qid}: duplicate question text")
            seen_questions.add(qtext)
            if q.get("code"):
                for line in q["code"].split("\n"):
                    if len(line) > 100:
                        warnings.append(f"{name}:{qid}: long code line ({len(line)} chars)")

    return slug, len(files), total, errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("books", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.all:
        dirs = sorted(d for d in glob.glob(os.path.join(here, "books", "*")) if os.path.isdir(d))
    else:
        dirs = args.books

    ok = True
    for d in dirs:
        slug, nfiles, total, errors, warnings = validate_book(d)
        status = "OK" if not errors else "FAIL"
        print(f"[{status}] {slug}: {nfiles} files, {total} questions, {len(errors)} errors, {len(warnings)} warnings")
        for e in errors:
            print(f"    ERROR: {e}")
        for w in warnings[:15]:
            print(f"    warn: {w}")
        if errors:
            ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
