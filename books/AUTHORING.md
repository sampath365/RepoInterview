# Interview book authoring guide

Each book lives in `books/<slug>/` and is built into `dist/<slug>.pdf` by
`tools/build_pdf.py`. Content is one JSON file per category in `books/<slug>/data/`.

## Category file schema

```json
{
  "category": "Human Readable Category Name",
  "slug": "category-slug",
  "icon": "short-icon-name",
  "questions": [
    {
      "id": "category-slug-001",
      "difficulty": "Beginner | Intermediate | Advanced",
      "question": "One clear interview question ending with a question mark?",
      "answer": "A thorough 2-5 sentence answer with trade-offs and when to use it.",
      "code": "optional snippet with \\n escapes; omit the key if not needed",
      "tags": ["lowercase", "keywords"],
      "references": ["https://<official-docs-url>"]
    }
  ]
}
```

## Rules

- Exactly **25 questions** per file, ids sequential `slug-001` .. `slug-025`.
- Difficulty mix per file: about 10 Beginner, 10 Intermediate, 5 Advanced.
- Every question has `id`, `difficulty`, `question`, `answer`, `tags` (1-3), `references` (1-2).
- `question` ends with `?`. `answer` is 2-5 accurate sentences.
- `code` is optional; use `\n` for newlines; keep lines under ~95 characters.
- Valid JSON only: no trailing commas, no comments, double quotes.
- References must be real official documentation URLs (Microsoft Learn, MDN,
  angular.io/angular.dev, react.dev, docs.nunit.org, xunit.net, etc.).
- Content must be factually correct and current.

## Validate a book

```bash
python3 tools/validate.py books/<slug>
```
