# Complete C# Interview Questions and Answers — 500 Questions

A curated set of **500 C# interview questions with detailed answers**, grouped
into 20 topic areas and delivered as a single, navigable **PDF**.

## Deliverable

`dist/CSharp-Interview-Questions-500.pdf`

- 135 pages, A4
- Cover page, clickable table of contents, and PDF bookmarks per category
- 500 numbered questions, each with a difficulty label, tags, and reference links
- Syntax-highlighted-style code blocks where relevant

## Topic areas

| # | Category | Questions |
|---|----------|-----------|
| 1 | C# Basics & Syntax | 25 |
| 2 | Object-Oriented Programming | 25 |
| 3 | Value Types & Reference Types | 25 |
| 4 | Collections & Data Structures | 25 |
| 5 | Generics | 25 |
| 6 | Delegates, Events & Lambdas | 25 |
| 7 | LINQ | 25 |
| 8 | Exception Handling | 25 |
| 9 | Async & Await | 25 |
| 10 | Memory Management & Garbage Collection | 25 |
| 11 | Strings & Text | 25 |
| 12 | File I/O & Serialization | 25 |
| 13 | Threading & Concurrency | 25 |
| 14 | Reflection & Attributes | 25 |
| 15 | Modern C# Features | 25 |
| 16 | Design Patterns | 25 |
| 17 | Testing & Best Practices | 25 |
| 18 | .NET Platform & Tooling | 25 |
| 19 | ASP.NET Core & Web | 25 |
| 20 | Entity Framework & Data Access | 25 |

## Repository layout

```
data/                 One JSON file per category (the content source of truth)
  SCHEMA.md           Schema and authoring rules
generate_pdf.py       Builds the PDF from the JSON data
dist/                 Generated PDF output
```

## Regenerating the PDF

```bash
pip install -r requirements.txt
python3 generate_pdf.py
```

The generator reads every `data/*.json` file, validates nothing implicitly, and
writes `dist/CSharp-Interview-Questions-500.pdf`. The table of contents and
bookmarks resolve over multiple build passes.

## Content schema

Each `data/<nn>-<slug>.json` file contains:

```json
{
  "category": "Human Readable Category Name",
  "slug": "short-slug",
  "icon": "icon-name",
  "questions": [
    {
      "id": "slug-001",
      "difficulty": "Beginner | Intermediate | Advanced",
      "question": "The interview question?",
      "answer": "A thorough answer.",
      "code": "optional C# snippet",
      "tags": ["keyword"],
      "references": ["https://learn.microsoft.com/..."]
    }
  ]
}
```

Answers target modern C# and .NET (C# 12/13, .NET 8/9) and cite Microsoft Learn.
