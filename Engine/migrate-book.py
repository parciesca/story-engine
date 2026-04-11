#!/usr/bin/env python3
"""
migrate-book.py — Split a compiled book.md into v3 chapter files.

Usage:
    python3 migrate-book.py <book.md> [--title "Book Title"] [--slug book-slug]
                                      [--genre "Genre"] [--tone "Tone"]
                                      [--perspective "3rd person"]
                                      [--treatment treatment.md]
                                      [--out ~/Documents/Stories/Books/<slug>]
                                      [--status completed|active]
                                      [--dry-run]

The script auto-detects chapter headings (### Chapter N: Title, ### Intermission: ...,
## Epilogue: ..., etc.) and splits them into individual files with YAML front matter.

Heading detection patterns (in order of priority):
    ### Chapter N: Title
    ### Intermission: Title
    ## Epilogue: Title
    ## Chapter N: Title
    # Chapter N: Title

If --out is not specified, defaults to ~/Documents/Stories/Books/<slug>/

Examples:
    # Minimal — auto-detect everything from the file
    python3 migrate-book.py "Books/My Novel/book.md" --title "My Novel"

    # Full spec
    python3 migrate-book.py book.md --title "Creation Beyond Existence" \\
        --slug creation-beyond-existence \\
        --genre "Hard sci-fi" --tone "Thriller to mythic" \\
        --perspective "3rd person limited" \\
        --treatment treatment.md --status completed
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def slugify(title: str) -> str:
    """Convert a title to a URL-friendly slug."""
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def find_sections(text: str):
    """Find all chapter/intermission/epilogue headings and their positions."""
    # Match heading lines that look like chapters, intermissions, or epilogue
    pattern = re.compile(
        r"^(#{1,3})\s+"
        r"(Chapter\s+\d+[^:\n]*:\s*.+|Intermission:\s*.+|Epilogue:\s*.+)",
        re.MULTILINE,
    )

    sections = []
    for m in pattern.finditer(text):
        level = len(m.group(1))
        full_heading = m.group(2).strip()
        start = m.start()

        # Parse title and original chapter number
        ch_match = re.match(r"Chapter\s+(\d+)(?:\s*[^:]*)?:\s*(.+)", full_heading)
        if ch_match:
            original_num = int(ch_match.group(1))
            title = ch_match.group(2).strip()
        else:
            original_num = None
            title = full_heading  # "Intermission: ..." or "Epilogue: ..."

        sections.append(
            {
                "start": start,
                "level": level,
                "full_heading": full_heading,
                "title": title,
                "original_num": original_num,
            }
        )

    return sections


def extract_prose(text: str, start: int, end: int, heading_line: str) -> str:
    """Extract prose between two section boundaries, stripping the heading."""
    raw = text[start:end]

    # Remove the heading line
    first_newline = raw.find("\n")
    if first_newline == -1:
        return ""
    prose = raw[first_newline:]

    # Split into lines and strip structural noise from tail
    lines = prose.split("\n")
    while lines and (
        lines[-1].strip() == ""
        or lines[-1].strip() == "---"
        or re.match(r"^#{1,3}\s+ACT\s+", lines[-1].strip())
    ):
        lines.pop()

    # Strip leading blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)

    return "\n".join(lines)


def detect_act_boundaries(text: str) -> dict[int, str]:
    """Find ## ACT headings and map them to character positions."""
    pattern = re.compile(r"^#{1,3}\s+(ACT\s+\S+)", re.MULTILINE)
    acts = {}
    for m in pattern.finditer(text):
        acts[m.start()] = m.group(1)
    return acts


def main():
    parser = argparse.ArgumentParser(
        description="Split a compiled book.md into v3 Story Engine chapter files."
    )
    parser.add_argument("book_file", help="Path to the compiled book.md")
    parser.add_argument("--title", help="Book title (auto-detected from # heading if omitted)")
    parser.add_argument("--slug", help="URL slug (derived from title if omitted)")
    parser.add_argument("--genre", default="", help="Genre description")
    parser.add_argument("--tone", default="", help="Tone description")
    parser.add_argument("--perspective", default="3rd person", help="Narrative perspective")
    parser.add_argument("--treatment", help="Path to treatment.md to copy in")
    parser.add_argument("--out", help="Output directory (default: ~/Documents/Stories/Books/<slug>/)")
    parser.add_argument("--status", default="completed", choices=["completed", "active"],
                        help="Book status")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without writing")
    args = parser.parse_args()

    # Read the book
    book_path = Path(args.book_file).resolve()
    if not book_path.exists():
        print(f"Error: {book_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(book_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Auto-detect title from first # heading if not provided
    title = args.title
    if not title:
        title_match = re.match(r"^#\s+(.+)", text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            print("Error: could not detect title. Use --title.", file=sys.stderr)
            sys.exit(1)

    slug = args.slug or slugify(title)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Detect sections
    sections = find_sections(text)
    if not sections:
        print("Error: no chapter headings found in the book.", file=sys.stderr)
        sys.exit(1)

    # Detect act boundaries (for reconstruction during compilation)
    act_positions = detect_act_boundaries(text)

    # Map act boundaries to section indices (which section each act precedes)
    act_before_section = {}
    for act_pos, act_name in sorted(act_positions.items()):
        for i, sec in enumerate(sections):
            if sec["start"] > act_pos:
                act_before_section[i] = act_name
                break

    # Output directory
    if args.out:
        out_dir = Path(args.out).resolve()
    else:
        out_dir = Path.home() / "Documents" / "Stories" / "Books" / slug

    chapters_dir = out_dir / "chapters"
    planning_dir = out_dir / "planning"
    branches_dir = out_dir / "branches"

    print(f"Book: {title}")
    print(f"Slug: {slug}")
    print(f"Output: {out_dir}")
    print(f"Sections found: {len(sections)}")
    print()

    # Extract prose for each section
    for i, sec in enumerate(sections):
        end = sections[i + 1]["start"] if i + 1 < len(sections) else len(text)
        prose = extract_prose(text, sec["start"], end, sec["full_heading"])
        sec["prose"] = prose
        sec["word_count"] = len(prose.split())
        sec["file_num"] = i + 1

    # Display plan
    total_words = 0
    for sec in sections:
        fname = f"{sec['file_num']:02d}.md"
        print(f"  {fname} — {sec['title']} ({sec['word_count']} words)")
        total_words += sec["word_count"]
    print(f"\nTotal: {total_words} words across {len(sections)} files")

    if args.dry_run:
        print("\n[dry run — no files written]")
        return

    # Create directories
    for d in [chapters_dir, planning_dir, branches_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Write chapter files
    chapter_entries = []
    for sec in sections:
        fname = f"{sec['file_num']:02d}.md"
        filepath = chapters_dir / fname

        front_matter = (
            f"---\n"
            f"chapter: {sec['file_num']}\n"
            f"title: \"{sec['title']}\"\n"
            f"branch: main\n"
            f"written: {today}\n"
            f"word_count: {sec['word_count']}\n"
            f"---"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + "\n\n" + sec["prose"] + "\n")

        chapter_entries.append(
            {
                "number": sec["file_num"],
                "branch": "main",
                "title": sec["title"],
                "file": f"chapters/{fname}",
                "written": now,
                "word_count": sec["word_count"],
            }
        )

    # Build manifest
    manifest = {
        "title": title,
        "slug": slug,
        "status": args.status,
        "genre": args.genre,
        "tone": args.tone,
        "perspective": args.perspective,
        "created": now,
        "last_modified": now,
        "current_chapter": sections[-1]["file_num"],
        "active_branch": "main",
        "branches": {
            "main": {
                "forked_from": None,
                "forked_at_chapter": None,
                "created": now,
            }
        },
        "chapters": chapter_entries,
        "treatment_source": "treatment.md" if args.treatment else None,
    }

    with open(out_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Copy treatment if provided
    if args.treatment:
        treatment_path = Path(args.treatment).resolve()
        if treatment_path.exists():
            import shutil
            shutil.copy2(treatment_path, out_dir / "treatment.md")
            print(f"\nTreatment copied from {treatment_path}")
        else:
            print(f"\nWarning: treatment file not found: {treatment_path}", file=sys.stderr)

    print(f"\nMigration complete.")
    print(f"  {len(chapter_entries)} chapter files written")
    print(f"  manifest.json created (slug: {slug})")
    print(f"\nNext steps:")
    print(f"  - Write story-bible.md (requires reading the prose)")
    print(f"  - Compile book.md to verify round-trip integrity")


if __name__ == "__main__":
    main()
