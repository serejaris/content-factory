# Content Factory

Claude Code skill — universal blog post pipeline with 7-phase workflow.

## Boundaries

| | Rule |
|---|------|
| ✅ Always | Keep SKILL.md universal (no hardcoded paths/repos), test find_related_posts.py with real blogs |
| ⚠️ Ask first | New phases in pipeline, new config fields, changing critic prompts |
| 🚫 Never | Hardcode user-specific data, invent facts in prompts, reference sereja.tech |

## Architecture

| Path | Purpose |
|------|---------|
| `SKILL.md` | Main skill — 7-phase orchestrator |
| `config/` | User-editable templates (author-bible, writing-guide, terms-glossary, project) |
| `scripts/` | Python utilities (find_related_posts.py) |
| `docs/plans/` | Design documents |

## Key Patterns

**Pipeline phases**: Questions → Research → Related → Brief → Draft → Deaify → Titles → Deploy. Each phase saves result to GitHub Issue as persistent storage.

**Sub-agents by model**: Haiku for classification/critics, Sonnet for research/brief, Opus for creative writing.

**Graceful degradation**: Every config file is optional. Empty author-bible → generic voice. No Exa → WebSearch fallback. No blog posts → skip related posts phase.

**Deaify = 5 parallel critics**: Generic Detector, Rhythm Analyzer, Specificity Checker, Fact Checker, Persona Guardian. Critics A-D universal, E reads from `config/author-bible.md`.

## Commands

| Task | Command |
|------|---------|
| Test related posts | `python scripts/find_related_posts.py "tag1,tag2" /path/to/blog/content` |

## Config Files

| File | Filled by | Purpose |
|------|-----------|---------|
| `config/project.md` | Onboarding (auto) | Repo, SSG, paths |
| `config/author-bible.md` | User (manual) | Persona, facts, replacement patterns |
| `config/writing-guide.md` | User (manual) | Style rules, anti-patterns |
| `config/terms-glossary.md` | User (manual) | Domain terminology |

## Tech Stack

Python 3.10+ (scripts), Markdown (skill + configs), gh CLI (deploy)
