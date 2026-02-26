# Content Factory

Universal blog post pipeline as a Claude Code skill.

Takes a topic → produces a ready-to-merge PR with a blog post through 7 automated phases.

```
Questions → Research → Related Posts → Brief → Draft → Deaify → Titles → PR
```

## Install

```bash
git clone https://github.com/serejaris/content-factory ~/.claude/skills/content-factory
```

## Setup

1. Fill `config/author-bible.md` — your persona, facts, voice
2. Run `/content-factory` — onboarding will ask for your blog repo and SSG
3. Write your first post

## Usage

```
/content-factory topic: how I automated my deploy pipeline
```

The skill will:
1. Ask clarifying questions (angle, audience, takeaway)
2. Research the topic with web search
3. Find related posts in your blog
4. Create a structured brief
5. Write an 800+ word draft with your voice
6. Run 5 parallel critics to remove AI fingerprints
7. Generate 5 title options for you to pick
8. Create a PR in your blog repo

## Pipeline

| Phase | What | Model |
|-------|------|-------|
| 1. Questions | Clarify topic, angle, audience | Human input |
| 2. Research | Web search, 3-5 sources | Sonnet |
| 2.5 Related | Find related posts by tags | Haiku |
| 2.7 Brief | Structure research into plan | Sonnet |
| 3. Draft | Write 800+ words from brief | Opus |
| 4. Deaify | 5 parallel critics + rewrite | Haiku + Opus |
| 5. Titles | 5 options, user picks | Opus |
| 6. Deploy | Branch + PR | git + gh |

## Configuration

All config files are in `config/`:

| File | Purpose | Required |
|------|---------|----------|
| `project.md` | Blog repo, SSG, paths | Yes (auto-generated) |
| `author-bible.md` | Your persona and facts | Recommended |
| `writing-guide.md` | Style rules | Optional |
| `terms-glossary.md` | Domain terminology | Optional |

### Supported SSGs

- **Hugo** — YAML frontmatter, `{{< callout >}}` shortcodes
- **Astro** — YAML frontmatter, MDX or blockquotes
- **Other** — YAML frontmatter, plain markdown

## Deaify: 5 Critics

The pipeline runs 5 parallel critics on every draft:

| Critic | Catches |
|--------|---------|
| A — Generic Detector | AI phrases, abstract claims |
| B — Rhythm Analyzer | Monotonous sentence patterns |
| C — Specificity Checker | Missing concrete details |
| D — Fact Checker | Outdated versions, wrong dates |
| E — Persona Guardian | Voice violations, fabricated facts |

Critics A-D are universal. Critic E adapts to your persona from `author-bible.md`.

## How It Works Without Config

The pipeline degrades gracefully:

- No `author-bible.md` → generic voice, basic AI-pattern detection
- No `writing-guide.md` → default style rules
- No `terms-glossary.md` → no term enforcement
- No existing blog posts → skips related posts phase
- No Exa MCP → falls back to WebSearch

## License

MIT
