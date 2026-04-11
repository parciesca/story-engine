#!/usr/bin/env python3
"""
migrate-to-slugs.py — One-time migration from GUID-based layout to
sequence-number + slug layout (story-engine#17, #18).

For each book under Books/:
  * rename chapters/NN-ch-<guid>.md   -> chapters/NN.md
  * rename addenda/NN-ad-<guid>.md    -> addenda/NN.md
  * rename planning/ch-<guid>-*.md    -> planning/NN-*.md
  * rename planning/ad-<guid>-*.md    -> planning/aNN-*.md
  * rename branches/br-<guid>/        -> branches/<slug>/   (slug from branches.*.name in manifest)
  * strip `id:` from chapter/addendum frontmatter
  * rewrite `branch: br-main` -> `branch: main` (or the branch slug)
  * rewrite manifest.json to the new schema (no top-level id, no per-item ids,
    integer current_chapter, current_item as {kind, number}, slug-keyed branches,
    integer after_chapter / after_addendum on addenda)

Idempotent: a book whose manifest has no top-level `id` is assumed already
migrated and is skipped.

Usage:
    python3 migrate-to-slugs.py --dry-run
    python3 migrate-to-slugs.py
    python3 migrate-to-slugs.py --books-dir /path/to/Books
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

GUID_RE = re.compile(r"[0-9a-f]{8}")


def slugify(name: str) -> str:
    s = (name or "").lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-") or "unnamed"


class Planner:
    """Collects planned operations; applies them or prints them."""

    def __init__(self, dry_run: bool):
        self.dry_run = dry_run
        self.renames: list[tuple[Path, Path]] = []
        self.writes: list[tuple[Path, str]] = []  # (path, new_content)
        self.deletes: list[Path] = []

    def rename(self, src: Path, dst: Path):
        if src == dst:
            return
        self.renames.append((src, dst))

    def write(self, path: Path, content: str):
        self.writes.append((path, content))

    def delete(self, path: Path):
        self.deletes.append(path)

    def summary(self) -> list[str]:
        lines = []
        for src, dst in self.renames:
            lines.append(f"  rename  {src}  ->  {dst}")
        for path, _ in self.writes:
            lines.append(f"  write   {path}")
        for path in self.deletes:
            lines.append(f"  delete  {path}")
        return lines

    def apply(self):
        # Apply renames first (files, then directories — sort longest path first)
        for src, dst in sorted(self.renames, key=lambda p: -len(str(p[0]))):
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.rename(src, dst)
        for path, content in self.writes:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
        for path in self.deletes:
            if path.exists():
                path.unlink()


# ------------------------------------------------------------
# Frontmatter rewrite
# ------------------------------------------------------------

def rewrite_frontmatter(text: str, branch_slug: str | None = None) -> str:
    """Strip `id:` line. Rewrite `branch: br-xxx` to the branch slug."""
    lines = text.splitlines(keepends=False)
    if not lines or lines[0].strip() != "---":
        return text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return text

    new_front = []
    for line in lines[1:end]:
        stripped = line.strip()
        if stripped.startswith("id:"):
            continue
        if branch_slug is not None and stripped.startswith("branch:"):
            new_front.append(f"branch: {branch_slug}")
            continue
        # Convert after_chapter: ch-xxx (for addenda; migration maps it separately,
        # but we leave the frontmatter's after_chapter as-is here — addendum flow
        # does not touch frontmatter's after_chapter since it's rewritten to a
        # number elsewhere. We just strip id lines.)
        new_front.append(line)

    result = ["---", *new_front, "---", *lines[end + 1:]]
    return "\n".join(result) + ("\n" if text.endswith("\n") else "")


def rewrite_addendum_frontmatter(text: str, chapter_guid_to_num: dict, addendum_guid_to_num: dict) -> str:
    """Strip id:, rewrite after_chapter: ch-xxx -> integer, or after_addendum: ad-xxx -> integer."""
    lines = text.splitlines(keepends=False)
    if not lines or lines[0].strip() != "---":
        return text
    try:
        end = lines.index("---", 1)
    except ValueError:
        return text

    new_front = []
    for line in lines[1:end]:
        stripped = line.strip()
        if stripped.startswith("id:"):
            continue
        m = re.match(r"after_chapter:\s*(\S+)", stripped)
        if m:
            val = m.group(1).strip('"\'')
            if val.startswith("ch-"):
                guid = val[3:]
                num = chapter_guid_to_num.get(guid)
                if num is not None:
                    new_front.append(f"after_chapter: {num}")
                    continue
            elif val.startswith("ad-"):
                guid = val[3:]
                num = addendum_guid_to_num.get(guid)
                if num is not None:
                    new_front.append(f"after_addendum: {num}")
                    continue
            # Fall through: leave line as-is
        new_front.append(line)

    result = ["---", *new_front, "---", *lines[end + 1:]]
    return "\n".join(result) + ("\n" if text.endswith("\n") else "")


# ------------------------------------------------------------
# Per-book migration
# ------------------------------------------------------------

def migrate_book(book_dir: Path, planner: Planner) -> str:
    """Return a status string ('migrated', 'skipped', 'error: ...')."""
    manifest_path = book_dir / "manifest.json"
    if not manifest_path.exists():
        return "skipped (no manifest.json)"

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as e:
        return f"error: could not parse manifest: {e}"

    # Idempotency: already migrated?
    if "id" not in manifest and isinstance(manifest.get("current_chapter"), int):
        return "skipped (already migrated)"
    if "id" not in manifest and manifest.get("current_chapter") is None and isinstance(manifest.get("current_item"), dict):
        return "skipped (already migrated)"

    # Build chapter guid -> number map
    chapters = manifest.get("chapters") or []
    chapter_guid_to_num: dict[str, int] = {}
    for ch in chapters:
        cid = ch.get("id", "")
        if cid.startswith("ch-"):
            chapter_guid_to_num[cid[3:]] = ch["number"]

    # Build addendum guid -> number map (hi-story only)
    addenda = manifest.get("addenda") or []
    addendum_guid_to_num: dict[str, int] = {}
    for ad in addenda:
        aid = ad.get("id", "")
        if aid.startswith("ad-"):
            addendum_guid_to_num[aid[3:]] = ad["number"]

    # Build branch id -> slug map.
    branches = manifest.get("branches") or {}
    branch_id_to_slug: dict[str, str] = {}
    for bid, bdata in branches.items():
        name = (bdata or {}).get("name") or bid
        # Special-case: br-main always becomes "main" regardless of name
        if bid == "br-main":
            slug = "main"
        else:
            slug = slugify(name)
        branch_id_to_slug[bid] = slug

    # ---- Main branch: rename chapter files & rewrite frontmatter ----
    main_chapters_dir = book_dir / "chapters"
    for ch in chapters:
        # Only chapters that belong to main branch live in book/chapters/
        if ch.get("branch") and ch["branch"] != "br-main":
            continue
        old_file = book_dir / ch["file"]
        new_name = f"{ch['number']:02d}.md"
        new_file = main_chapters_dir / new_name
        if old_file.exists() and old_file != new_file:
            # Read, rewrite frontmatter, plan rename + write
            text = old_file.read_text(encoding="utf-8")
            new_text = rewrite_frontmatter(text, branch_slug="main")
            planner.rename(old_file, new_file)
            if new_text != text:
                planner.write(new_file, new_text)

    # ---- Main branch: rename planning files ----
    planning_dir = book_dir / "planning"
    if planning_dir.exists():
        for p in sorted(planning_dir.iterdir()):
            if not p.is_file():
                continue
            name = p.name
            m = re.match(r"ch-([0-9a-f]{8})-(proposal|feedback)\.md$", name)
            if m:
                guid, kind = m.group(1), m.group(2)
                num = chapter_guid_to_num.get(guid)
                if num is not None:
                    new_p = planning_dir / f"{num:02d}-{kind}.md"
                    planner.rename(p, new_p)
                continue
            m = re.match(r"ad-([0-9a-f]{8})-(proposal|feedback)\.md$", name)
            if m:
                guid, kind = m.group(1), m.group(2)
                num = addendum_guid_to_num.get(guid)
                if num is not None:
                    new_p = planning_dir / f"a{num:02d}-{kind}.md"
                    planner.rename(p, new_p)
                continue

    # ---- Addenda files (hi-story) ----
    addenda_dir = book_dir / "addenda"
    for ad in addenda:
        old_file = book_dir / ad["file"]
        new_file = addenda_dir / f"{ad['number']:02d}.md"
        if old_file.exists() and old_file != new_file:
            text = old_file.read_text(encoding="utf-8")
            new_text = rewrite_addendum_frontmatter(text, chapter_guid_to_num, addendum_guid_to_num)
            planner.rename(old_file, new_file)
            if new_text != text:
                planner.write(new_file, new_text)

    # ---- Branch directories: rename and migrate inside ----
    branches_dir = book_dir / "branches"
    if branches_dir.exists():
        for bdir in sorted(branches_dir.iterdir()):
            if not bdir.is_dir():
                continue
            old_name = bdir.name
            new_slug = branch_id_to_slug.get(old_name)
            if not new_slug:
                # Unknown branch directory (not in manifest); derive slug from name if possible
                new_slug = slugify(old_name.replace("br-", ""))
            new_bdir = branches_dir / new_slug

            # Migrate chapter files inside this branch BEFORE renaming the dir
            bchapters_dir = bdir / "chapters"
            if bchapters_dir.exists():
                for ch in chapters:
                    if ch.get("branch") != old_name:
                        continue
                    # Chapter file path in manifest may be relative to book root
                    rel = ch["file"]
                    old_ch = book_dir / rel
                    if not old_ch.exists():
                        continue
                    new_ch_name = f"{ch['number']:02d}.md"
                    new_ch = bchapters_dir / new_ch_name
                    if old_ch != new_ch:
                        text = old_ch.read_text(encoding="utf-8")
                        new_text = rewrite_frontmatter(text, branch_slug=new_slug)
                        planner.rename(old_ch, new_ch)
                        if new_text != text:
                            planner.write(new_ch, new_text)

            # Migrate planning files inside this branch
            bplanning = bdir / "planning"
            if bplanning.exists():
                for p in sorted(bplanning.iterdir()):
                    if not p.is_file():
                        continue
                    name = p.name
                    m = re.match(r"ch-([0-9a-f]{8})-(proposal|feedback)\.md$", name)
                    if m:
                        guid, kind = m.group(1), m.group(2)
                        num = chapter_guid_to_num.get(guid)
                        if num is not None:
                            new_p = bplanning / f"{num:02d}-{kind}.md"
                            planner.rename(p, new_p)

            # Finally, rename the branch directory itself
            if bdir != new_bdir:
                planner.rename(bdir, new_bdir)

    # ---- Rewrite manifest ----
    new_manifest = dict(manifest)
    new_manifest.pop("id", None)

    # Rebuild chapters
    new_chapters = []
    for ch in chapters:
        entry = {k: v for k, v in ch.items() if k != "id"}
        branch_id = entry.get("branch", "br-main")
        entry["branch"] = branch_id_to_slug.get(branch_id, slugify(branch_id))
        # New file path
        if entry["branch"] == "main":
            entry["file"] = f"chapters/{ch['number']:02d}.md"
        else:
            entry["file"] = f"branches/{entry['branch']}/chapters/{ch['number']:02d}.md"
        new_chapters.append(entry)
    new_manifest["chapters"] = new_chapters

    # Rebuild addenda
    if addenda:
        new_addenda = []
        for ad in addenda:
            entry = {k: v for k, v in ad.items() if k != "id"}
            # Convert after_chapter: ch-xxx -> int, or to after_addendum if it points to ad-
            ac = entry.get("after_chapter")
            if isinstance(ac, str):
                if ac.startswith("ch-"):
                    num = chapter_guid_to_num.get(ac[3:])
                    if num is not None:
                        entry["after_chapter"] = num
                elif ac.startswith("ad-"):
                    num = addendum_guid_to_num.get(ac[3:])
                    if num is not None:
                        entry.pop("after_chapter", None)
                        entry["after_addendum"] = num
            entry["file"] = f"addenda/{ad['number']:02d}.md"
            new_addenda.append(entry)
        new_manifest["addenda"] = new_addenda

    # Rebuild branches map (keyed by slug, drop `name`)
    new_branches = {}
    for bid, bdata in branches.items():
        slug = branch_id_to_slug.get(bid, slugify(bid))
        entry = {k: v for k, v in (bdata or {}).items() if k != "name"}
        # forked_from: translate br-xxx -> slug
        if isinstance(entry.get("forked_from"), str) and entry["forked_from"] in branch_id_to_slug:
            entry["forked_from"] = branch_id_to_slug[entry["forked_from"]]
        # forked_at_chapter: translate ch-xxx -> integer
        fac = entry.get("forked_at_chapter")
        if isinstance(fac, str) and fac.startswith("ch-"):
            num = chapter_guid_to_num.get(fac[3:])
            if num is not None:
                entry["forked_at_chapter"] = num
        new_branches[slug] = entry
    new_manifest["branches"] = new_branches

    # active_branch: translate
    ab = manifest.get("active_branch")
    if isinstance(ab, str):
        new_manifest["active_branch"] = branch_id_to_slug.get(ab, slugify(ab))

    # current_chapter / current_item
    cc = manifest.get("current_chapter")
    if isinstance(cc, str) and cc.startswith("ch-"):
        num = chapter_guid_to_num.get(cc[3:])
        if num is not None:
            new_manifest["current_chapter"] = num

    ci = manifest.get("current_item")
    if isinstance(ci, str):
        if ci.startswith("ch-"):
            num = chapter_guid_to_num.get(ci[3:])
            if num is not None:
                new_manifest["current_item"] = {"kind": "chapter", "number": num}
        elif ci.startswith("ad-"):
            num = addendum_guid_to_num.get(ci[3:])
            if num is not None:
                new_manifest["current_item"] = {"kind": "addendum", "number": num}

    new_manifest_text = json.dumps(new_manifest, indent=2, ensure_ascii=False) + "\n"
    planner.write(manifest_path, new_manifest_text)

    return "migrated"


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Migrate books from GUID layout to slug/number layout.")
    parser.add_argument("--books-dir", default="Books", help="Path to Books/ directory (default: ./Books)")
    parser.add_argument("--dry-run", action="store_true", help="Print planned operations without touching disk")
    args = parser.parse_args()

    books_root = Path(args.books_dir).resolve()
    if not books_root.exists():
        print(f"Error: {books_root} does not exist", file=sys.stderr)
        sys.exit(1)

    any_error = False
    for book_dir in sorted(books_root.iterdir()):
        if not book_dir.is_dir():
            continue
        planner = Planner(dry_run=args.dry_run)
        status = migrate_book(book_dir, planner)
        print(f"\n== {book_dir.name} == {status}")
        for line in planner.summary():
            print(line)
        if status == "migrated" and not args.dry_run:
            try:
                planner.apply()
                print("  [applied]")
            except Exception as e:
                print(f"  [ERROR applying: {e}]", file=sys.stderr)
                any_error = True

    if args.dry_run:
        print("\n[dry run — no files written]")

    sys.exit(1 if any_error else 0)


if __name__ == "__main__":
    main()
