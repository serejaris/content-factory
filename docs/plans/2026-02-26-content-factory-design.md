# Content Factory — Design Document

Universal blog post pipeline as a Claude Code skill.

## Overview

Open-source Claude Code skill that takes a topic and produces a ready-to-merge PR with a blog post. 7-phase pipeline with parallel sub-agents, persistent storage via GitHub Issues, and configurable author persona.

## Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Phase 1     │     │  Phase 2     │     │  Phase 2.5   │     │  Phase 2.7   │
│  Questions   │ ──▶ │  Research    │ ──▶ │  Related     │ ──▶ │  Brief       │
│  (human)     │     │  (sonnet)    │     │  Posts       │     │  (sonnet)    │
└──────────────┘     └──────────────┘     │  (haiku)     │     └──────┬───────┘
                                          └──────────────┘            │
                                                                      ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Phase 6     │     │  Phase 5     │     │  Phase 4     │     │  Phase 3     │
│  Deploy      │ ◀── │  Titles      │ ◀── │  Deaify      │ ◀── │  Draft       │
│  PR          │     │  (opus)      │     │  (5 critics) │     │  (opus)      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

## Phases

| # | Phase | Model | Input | Output |
|---|-------|-------|-------|--------|
| 1 | Questions | AskUserQuestion | Topic from user | Angle, audience, context, takeaway |
| 2 | Research | Task(sonnet) + Exa | Phase 1 answers | 3-5 sources, facts, cases |
| 2.5 | Related Posts | Script + Task(haiku) | Tags of new post | 3-5 related posts (JSON) |
| 2.7 | Brief | Task(sonnet) | Research + Related | Structured brief: thesis, facts, outline |
| 3 | Draft | Task(opus) + author config | Brief + Related | Draft 800+ words in markdown |
| 4 | Deaify | 5 parallel critics (haiku) | Draft | Text without AI fingerprints |
| 5 | Titles | Task(opus) → AskUserQuestion | Deaified text | 5 title options → user picks |
| 6 | Deploy | git + gh CLI | Final article | PR to blog repo |

## Repository Structure

```
content-factory/
├── SKILL.md                         # Main skill — orchestrator
├── scripts/
│   ├── find_related_posts.py        # Find related posts by tags (universal)
│   └── screenshot.py                # ASCII → PNG for og:image (later)
├── config/
│   ├── author-bible.md              # User fills: persona, facts, patterns
│   ├── writing-guide.md             # User fills: style rules
│   ├── terms-glossary.md            # User fills: domain terms (optional)
│   ├── project.md                   # Auto-generated on first run
│   └── semantic-core.md             # SEO keywords (optional, later)
├── docs/
│   └── plans/
│       └── 2026-02-26-content-factory-design.md
└── README.md
```

## Configuration

### config/project.md (auto-generated on first run)

```markdown
# Project Config

- repo: user/my-blog
- ssg: hugo
- content_path: content/blog/
- frontmatter_format: yaml
- telegram_channel:              # optional
- branch_prefix: blog/
```

### config/author-bible.md (user fills manually)

```markdown
# Author Bible

## Persona — who are you? (2-3 sentences)

## What you DON'T do

## Replacement patterns
| Bad | Good |
|-----|------|

## Facts — what's true (list)
```

### Onboarding (first run)

When `/content-factory` is called and `config/project.md` is empty, the skill runs onboarding:

1. Author name / blog signature
2. Blog repository URL
3. SSG engine → Hugo / Astro / Other
4. Content path (auto-detect or manual)
5. Telegram channel for announcements (optional)

Result saved to `config/project.md`.

## Phase 4: Deaify — 5 Parallel Critics

```
┌─────────────────────────────────────────┐
│  config/author-bible.md                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  5 parallel critics (Task/Haiku)     │
│                                      │
│  A: Generic Detector  — universal    │
│  B: Rhythm Analyzer   — universal    │
│  C: Specificity Check — universal    │
│  D: Fact Checker      — universal    │
│  E: Persona Guardian  — from config  │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Fact verification (Exa search)      │
│  Only for flags from Critic D        │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Rewriter (Opus)                     │
│  Persona rules from author-bible     │
│  + all critic notes                  │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│  Post-check: Critic E again         │
│  If violations remain — fix inline   │
└──────────────────────────────────────┘
```

### Critics

| Critic | What it does | Universal |
|--------|-------------|-----------|
| A — Generic Detector | Catches AI phrases ("importantly", "it should be noted") | Yes |
| B — Rhythm Analyzer | Same-length sentences, monotony | Yes |
| C — Specificity Checker | Where to add specifics, numbers, opinions | Yes |
| D — Fact Checker | Verifies versions, dates, names via Exa | Yes |
| E — Persona Guardian | Catches persona violations + fabricated facts | From config |

**Critic E parameterization:** reads `config/author-bible.md` for persona rules and fact verification. If author-bible is empty — falls back to generic AI-pattern detection only.

## SSG Adaptation

| SSG | Frontmatter | Callouts/Components | Content path default |
|-----|-------------|--------------------|--------------------|
| Hugo | YAML `---` | `{{</* callout */>}}` shortcodes | `content/blog/` |
| Astro | YAML `---` | MDX components | `src/content/blog/` |
| Other | YAML `---` | Plain markdown (no components) | User specifies |

Phase 3 (Draft) and Phase 6 (Deploy) adapt based on `config/project.md` SSG setting. All other phases are SSG-agnostic.

## Context Window Management

The 7-phase pipeline does NOT fit in one context window. Solutions:

1. **Sub-agents** — Phases 2, 2.5, 2.7, 3, 4, 5 run via Task tool. Main agent only orchestrates.
2. **GitHub Issue as persistent storage** — each phase result saved as a comment. On context compaction — read comments from issue.
3. **Full context in sub-agent prompts** — pass complete brief text, author-bible, related posts. Never reference "previous context".

## Graceful Degradation

| Config missing | What happens |
|----------------|-------------|
| `author-bible.md` empty | Phase 3: generic voice. Phase 4: Critic E checks AI patterns only. Skill reminds to fill it. |
| `writing-guide.md` empty | Default writing rules (built into SKILL.md). |
| `terms-glossary.md` empty | No domain term enforcement. |
| `semantic-core.md` empty | No SEO keyword targeting. |
| No Exa MCP | Phase 2 uses WebSearch fallback. Phase 4 Critic D skips fact verification. |

## Deploy Flow

```
git checkout -b {branch_prefix}{slug}
  → commit
  → push + PR (never to main directly)
  → after merge: channel notification (optional)
  → close tracking issue
```

## MVP Scope

### MVP (first release)

- SKILL.md — orchestrator for 7 phases
- `config/` — author-bible, writing-guide, project, terms-glossary templates
- Onboarding on first run
- Phases 1-6: Questions → Research → Related → Brief → Draft → Deaify → Titles → PR
- 5 parallel critics with fact-check
- Issue as persistent storage
- `find_related_posts.py` universal script
- Hugo + Astro SSG support

### Later

- `screenshot.py` ASCII → PNG for og:image
- Telegram announcement after merge
- Next.js / custom SSG support
- `semantic-core.md` SEO keywords
- README auto-update after publish
