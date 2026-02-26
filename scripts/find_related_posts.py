#!/usr/bin/env python3
"""Find related blog posts by tag overlap.

Usage:
    python find_related_posts.py "tag1,tag2,tag3" /path/to/blog/content [exclude_slug]

Scans markdown files in the given directory, extracts tags from YAML frontmatter,
and returns top 15 posts sorted by tag overlap as JSON.

Supports:
- YAML frontmatter (--- delimited)
- Tags as array: tags: ["a", "b"] or tags: [a, b]
- Tags as list: tags:\\n  - a\\n  - b
"""

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract title, description, tags from YAML frontmatter."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fm = {}
    lines = match.group(1).split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line or line.startswith(" ") or line.startswith("\t"):
            i += 1
            continue

        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip().strip("\"'")

        # Inline array: tags: ["a", "b"] or tags: [a, b]
        if key == "tags" and val.startswith("["):
            val = [t.strip().strip("\"'") for t in val[1:-1].split(",") if t.strip()]
        # YAML list: tags:\n  - a\n  - b
        elif key == "tags" and not val:
            tag_list = []
            while i + 1 < len(lines) and re.match(r"^\s+-\s+", lines[i + 1]):
                i += 1
                tag_val = re.sub(r"^\s+-\s+", "", lines[i]).strip().strip("\"'")
                if tag_val:
                    tag_list.append(tag_val)
            val = tag_list

        fm[key] = val
        i += 1

    return fm


def get_all_posts(content_dir: Path) -> list[dict]:
    """Scan all blog posts and extract metadata."""
    posts = []

    for path in content_dir.rglob("*.md"):
        if path.name.startswith("_"):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        fm = parse_frontmatter(content)
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags] if tags else []

        slug = path.stem
        # For index.md inside a directory, use parent dir name
        if slug == "index" and path.parent != content_dir:
            slug = path.parent.name

        posts.append(
            {
                "slug": slug,
                "path": f"/blog/{slug}",
                "title": fm.get("title", slug),
                "description": fm.get("description", ""),
                "tags": tags,
            }
        )

    return posts


def find_by_tags(
    content_dir: Path, target_tags: list[str], exclude_slug: str | None = None
) -> list[dict]:
    """Find posts with overlapping tags, sorted by overlap count."""
    posts = get_all_posts(content_dir)
    scored = []

    target_set = set(t.lower() for t in target_tags)

    for post in posts:
        if post["slug"] == exclude_slug:
            continue

        post_tags = set(t.lower() for t in post["tags"])
        overlap = len(target_set & post_tags)

        if overlap > 0:
            scored.append({**post, "tag_overlap": overlap})

    scored.sort(key=lambda x: -x["tag_overlap"])
    return scored[:15]


def main():
    if len(sys.argv) < 3:
        print("Usage: python find_related_posts.py 'tag1,tag2' /path/to/content [exclude_slug]")
        print()
        print("Examples:")
        print("  python find_related_posts.py 'ai,automation' ./content/blog")
        print("  python find_related_posts.py 'react,frontend' ./posts my-post-slug")
        sys.exit(1)

    tags = [t.strip() for t in sys.argv[1].split(",") if t.strip()]
    content_dir = Path(sys.argv[2])
    exclude = sys.argv[3] if len(sys.argv) > 3 else None

    if not content_dir.exists():
        print(f"Error: directory not found: {content_dir}", file=sys.stderr)
        sys.exit(1)

    related = find_by_tags(content_dir, tags, exclude)

    if not related:
        print("[]")
        return

    print(json.dumps(related, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
