# File Formats — hi-story-engine

Reference for the file shapes this engine reads and writes inside `$LIBRARY_ROOT/Books/<slug>/`. SKILL.md links here from the write flow; open when you need the exact structure.

For manifest shape see `manifest-schema.md`.

---

## Chapter file — `chapters/NN.md`

Zero-padded sequence number (`01.md`, `02.md`). YAML frontmatter followed by prose:

```markdown
---
chapter: 1
title: "Chapter Title"
written: 2026-04-09
word_count: 850
---

[Chapter prose here]
```

---

## Addendum file — `addenda/NN.md`

Addenda have their own sequence numbering, independent of chapters. Zero-padded: `01.md`, `02.md`.

```markdown
---
addendum: 1
title: "Addendum Title"
after_chapter: 1
written: 2026-04-09
word_count: 500
---

[Addendum prose here]
```

For an addendum off another addendum, replace `after_chapter` with `after_addendum: N`. An addendum entry carries exactly one of the two.

---

## Planning file — `planning/NN-proposal.md` (chapters) or `planning/aNN-proposal.md` (addenda)

Flat `planning/` directory. The `a` prefix marks an addendum; the number that follows is the addendum's own sequence number (not the chapter it's attached to).

Two sections written at different points in the lifecycle; both accumulate in the same file — never overwritten.

### Chapter proposal + handoff

```
CHAPTER PROPOSAL
  Chapter: [number]
  Topic: [specific focus of this chapter]
  Time Period: [dates/era covered]
  Follows from: [user's navigation choice or direction]
  This chapter covers: [1-2 sentences]
  Key elements: [3-6 things to cover]
  Figures featured: [who appears in this chapter]
  Research note: [what to verify, what sources to seek]
  Approach: [sweeping overview / focused deep dive / character study / connective tissue]
  Research bible implications: [what changes after this chapter]

---

CHAPTER HANDOFF
  Written: [date]

  [The exact navigation options as presented to the user.
   Copy verbatim — this is the resume anchor for the next session.]
```

### Addendum proposal + handoff

Lighter than a chapter proposal.

```
ADDENDUM PROPOSAL
  Addendum: [number]
  After chapter: [current chapter number]
  Topic: [the tangent being explored]
  This addendum covers: [1-2 sentences]
  Key elements: [2-4 things to cover]
  Connection to main thread: [how this relates]

---

ADDENDUM HANDOFF
  Written: [date]

  [The return-or-continue options as presented to the user.]
```

The PROPOSAL is written before drafting. The HANDOFF is written after presenting — it must be the text the user actually saw, verbatim. Without it, resume has nothing to orient against.

---

## Feedback file — `planning/NN-feedback.md` (chapters) or `planning/aNN-feedback.md` (addenda)

Contains the user's steering response to a HANDOFF — a letter choice, a specific question, or open-ended direction.

```
CHAPTER FEEDBACK
  For: [chapter or addendum number, e.g. "1" or "a1"]
  Written: [date]

[User's free-text response to the handoff navigation options]
```

### Who writes feedback files

Two paths produce them:

1. **The book viewer** — when the user steers between sessions, the viewer commits a feedback file directly to `book/<slug>`.
2. **The engine** — when the user steers in chat in response to the prior item's handoff, the engine writes the user's message verbatim as part of the next write pass.

### Engine write rules

- Write only if the file does not already exist. If the viewer already wrote one, trust it — **do not overwrite**.
- Write the user's message **verbatim**. A letter choice, `"keep going"`, or a full direction paragraph all go in as-is.
- Use the exact format above.
- Stage it in the same commit as the next chapter or addendum — no separate commit.
- Off-book / meta chat ("show bible", "who's who?", "where are we?") is not handoff steering and does not produce a feedback file.

Outside this carve-out, feedback files are read-only for the engine — never overwrite or modify them.

---

## Research bible — `research-bible.md`

Plain markdown (no frontmatter), rewritten incrementally as research comes in and again after every chapter/addendum. Structure:

```
RESEARCH BIBLE
===============

SUBJECT & SCOPE
  Topic: [established at init]
  Time Period: [range being explored]
  Geographic Focus: [if applicable]
  Core question: [1-2 sentence distillation of what we're exploring]

KEY FIGURES
  [Name] — [Role/identity]. [Why they matter to this exploration].
    [Status: central / peripheral / mentioned]
  ...

ESTABLISHED CONTEXT
  [Historical facts, systems, and conditions that have been
   established as the backdrop for the exploration. Economic
   structures, political arrangements, social norms, technologies
   — whatever the exploration has grounded itself in.]
  ...

THEMATIC THREADS
  [Patterns and recurring dynamics that have emerged across
   chapters. Not imposed — observed from what the exploration is
   actually revealing. Updated as the exploration develops.]
  ...

THREADS TO PULL
  [Things mentioned in passing that haven't been explored yet.
   Connections hinted at. Rabbit holes spotted but not entered.
   The "explore these later" list. Items move off this list when
   they become chapters or addenda, or when they're deliberately
   set aside.]
  ...

EXPLORATION MAP
  Current focus: [where we are topically]
  Time position: [where we are chronologically]
  Chapters so far: [1-line summaries]
  Addenda: [1-line summaries]
  ...

OPEN QUESTIONS
  [Things the historical record doesn't clearly answer.
   Debates among historians. Uncertainties worth noting.
   Things we've flagged as contested or ambiguous.]
  ...

SOURCES OF NOTE
  [Particularly interesting or important sources encountered
   during research. Not an exhaustive bibliography — just the
   ones worth remembering or returning to.]
  ...
```

Incremental-save discipline: fold findings into the bible on disk after each productive search pass. Don't hold research in context waiting for a complete chapter.

---

## Treatment — `treatment.md`

Written at wrap-up — captures what the exploration *became*. Keep under 1500 words. See the Wrap-Up section of SKILL.md for structure.

---

## Compiled book — `book.md`

Regenerated on demand by "compile book". Concatenates chapters and addenda in order (addenda placed after the chapter they follow) with headings and a title page. Always regenerable — not a source of truth.
