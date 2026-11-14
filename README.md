# Interview Questions - 13 Books, 6,500 Questions

A collection of **13 interview-question books**, each with **500 questions and
answers** across 20 topic areas, delivered as navigable PDFs.

## Books

| Book | Topic | Questions | Pages |
|------|-------|-----------|-------|
| `csharp` | Complete C# | 500 | 135 |
| `sqlserver` | SQL Server | 500 | 105 |
| `aspnetcore` | ASP.NET Core | 500 | 114 |
| `aspnetcoreapi` | ASP.NET Core Web API | 500 | 99 |
| `wpf` | WPF | 500 | 107 |
| `xunit` | xUnit | 500 | 116 |
| `nunit` | NUnit | 500 | 102 |
| `maui` | .NET MAUI | 500 | 114 |
| `angular` | Angular | 500 | 103 |
| `react` | React | 500 | 102 |
| `designpatterns` | Design Patterns | 500 | 98 |
| `fastify` | Fastify | 500 | 97 |
| `nextjs` | Next.js | 500 | 94 |

Each PDF has a cover page, a clickable table of contents, PDF bookmarks per
category, and 500 numbered questions with a difficulty label, tags, reference
links, and code blocks where relevant.

## Download

Prebuilt PDFs are in `dist/`. Each book is also published as a GitHub release
with a direct download link, for example:

```
https://github.com/sampath365/RepoInterview/releases/download/<tag>/<slug>.pdf
```

## Repository layout

```
books/
  AUTHORING.md            Schema and authoring rules for all books
  <slug>/
    book.json             Title, subtitle, blurb
    PLAN.md               Category plan (20 categories)
    data/*.json           One file per category (source of truth)
tools/
  build_pdf.py            Builds PDFs from book folders
  validate.py             Validates books (schema, counts, duplicates)
dist/                     Generated PDFs
```

## Regenerating the PDFs

```bash
pip install -r requirements.txt
python3 tools/validate.py --all      # check content
python3 tools/build_pdf.py --all     # build every book into dist/
```

Build a single book with `python3 tools/build_pdf.py books/<slug>`.

## Content schema

Each `books/<slug>/data/<nn>-<category>.json` file contains 25 questions:

```json
{
  "category": "Human Readable Category Name",
  "slug": "category-slug",
  "icon": "short-icon-name",
  "questions": [
    {
      "id": "category-slug-001",
      "difficulty": "Beginner | Intermediate | Advanced",
      "question": "The interview question?",
      "answer": "A thorough answer.",
      "code": "optional snippet",
      "tags": ["keyword"],
      "references": ["https://official-docs..."]
    }
  ]
}
```

Answers target current versions (C# 12/13, .NET 8/9, SQL Server 2019/2022,
Angular 17+, React 18/19, NUnit 4, xUnit v3) and cite official documentation.
