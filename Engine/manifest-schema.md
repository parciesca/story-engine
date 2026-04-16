# manifest.json Schema

Every book has a `Books/<slug>/manifest.json` that tracks state. The two engines share the same core schema; hi-story adds `topic`, `time_period`, `geographic_focus`, and `addenda`.

## Common fields

| Field | Type | Description |
|---|---|---|
| `title` | string | Display title of the book |
| `slug` | string | URL/directory identifier (`kebab-case`) |
| `status` | string | `"active"` \| `"completed"` \| `"initializing"` |
| `created` | ISO 8601 | When the book was first created |
| `last_modified` | ISO 8601 | Updated on every write |
| `engine` | string | `"story"` or `"hi-story"` — which engine manages this book |
| `engine_commit` | string | Short SHA of the engine branch (`main`) when the book was last written. Set on new-book creation; updated on every chapter-write commit. |
| `treatment_source` | string \| null | Filename of the source treatment, or `null` |

## story engine only

| Field | Type | Description |
|---|---|---|
| `genre` | string | Genre descriptor |
| `tone` | string | Tone description |
| `perspective` | string | Narrative POV |
| `current_chapter` | integer | Sequence number of the most recently written chapter on the active branch |
| `active_branch` | string | Slug of the currently active story-fork branch (default: `"main"`) |
| `branches` | object | Map of branch slug → `{ forked_from, forked_at_chapter, created }` |
| `chapters` | array | Ordered list of chapter records (see below) |

### Chapter record

```json
{
  "number": 1,
  "branch": "main",
  "title": "Chapter Title",
  "file": "chapters/01.md",
  "written": "2026-04-06T00:00:00Z",
  "word_count": 1050
}
```

## hi-story engine only

| Field | Type | Description |
|---|---|---|
| `topic` | string | The specific historical subject |
| `time_period` | string | Era or date range |
| `geographic_focus` | string | Primary location(s) |
| `current_item` | object | `{ "kind": "chapter"\|"addendum", "number": N }` |
| `chapters` | array | Ordered list of chapter records |
| `addenda` | array | Ordered list of addendum records (see below) |

### Addendum record

```json
{
  "number": 1,
  "title": "Addendum Title",
  "after_chapter": 1,
  "file": "addenda/01.md",
  "written": "2026-04-09T00:00:00Z",
  "word_count": 500
}
```

`after_chapter` is the integer chapter number the addendum hangs off. For an addendum off another addendum, use `after_addendum` instead.

## Routing

The `engine` field is the canonical way to distinguish story vs hi-story books. The viewer and tooling should use `manifest.engine === 'hi-story'` to detect history books. The presence of `topic`/`time_period`/`addenda` is a legacy heuristic that applies to books written before `engine` was added (#34).
