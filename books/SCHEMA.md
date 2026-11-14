# C# Q&A content schema

Each category is one JSON file in `data/`. Exact schema:

```json
{
  "category": "Human Readable Category Name",
  "slug": "short-slug",
  "icon": "one of: book, layers, cube, grid, code, bolt, filter, alert, refresh, cpu, memory, search, text, file, database, globe, link, check, blocks, sparkles",
  "questions": [
    {
      "id": "slug-001",
      "difficulty": "Beginner | Intermediate | Advanced",
      "question": "One clear interview question ending with a question mark?",
      "answer": "A thorough 2-5 sentence answer. Explain the concept, trade-offs, and when to use it. Plain, technical, accurate.",
      "code": "optional C# snippet with \\n escapes; omit key if not needed",
      "tags": ["lowercase", "keyword", "tags"],
      "references": ["https://learn.microsoft.com/..."]
    }
  ]
}
```

Rules:
- Exactly 25 questions per file, ids sequential `slug-001` .. `slug-025`.
- Difficulty mix per file: ~10 Beginner, ~10 Intermediate, ~5 Advanced.
- Every question has tags (1-3) and references (1-2 Microsoft Learn URLs).
- Valid JSON only, no trailing commas, no comments. `code` key is optional.
- Answers must be factually correct for modern C# (.NET 8/9, C# 12/13).
