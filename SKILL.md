---
name: content-factory
description: Universal blog post pipeline. 7-phase workflow with research, deaification, and deploy. Use when asked to write a blog post, create an article, or produce content for a blog.
---

# Content Factory

7-phase pipeline that takes a topic and produces a ready-to-merge PR with a blog post.

```
Questions → Research → Related Posts → Brief → Draft → Deaify → Titles → Deploy
```

## Quick Start

1. Read `{baseDir}/config/project.md` — if empty, run **Onboarding** below
2. Read `{baseDir}/config/author-bible.md` — pass to Phase 3, 4
3. Read `{baseDir}/config/writing-guide.md` — pass to Phase 3, 4
4. Start Phase 1

## Onboarding (first run only)

If `config/project.md` has empty values, ask user via AskUserQuestion:

1. Blog repository (GitHub URL, e.g. `user/my-blog`)
2. SSG engine → Hugo / Astro / Other
3. Content path (default: `content/blog/` for Hugo, `src/content/blog/` for Astro)
4. Telegram channel for announcements (optional, leave empty to skip)

Save answers to `{baseDir}/config/project.md` using Write tool. Then remind:

> Fill `config/author-bible.md` with your persona and facts — this makes Phase 4 (deaify) work for your voice. Without it, the pipeline still works but produces generic-sounding text.

## Context Window Management

This pipeline does NOT fit in one context window. Rules:

1. **Use sub-agents.** Phases 2, 2.5, 2.7, 3, 4, 5 — ALL through Task tool. Main agent only orchestrates.
2. **GitHub Issue as persistent storage.** Create issue before Phase 1. Save each phase result as a comment. If context compacts — read comments from issue.
3. **Full context in sub-agent prompts.** Pass complete text of brief, author-bible, related posts. Never reference "previous context".

### Issue tracking

Before Phase 1:

```bash
gh issue create -R {repo} --title "blog: {topic}" --body "Content factory pipeline.
Topic: {topic}
Status: Phase 1 — Questions"
```

After EACH phase, save result as comment:

```bash
gh issue comment {issue_number} -R {repo} --body "## Phase N: {name}
{full result}"
```

If context compacts, recover with: `gh issue view {issue_number} -R {repo} --comments`

---

## Phase 1: Questions

**ALWAYS start here. Don't proceed without answers.**

Ask via AskUserQuestion:

1. **Topic/Angle** — what specifically? which aspect?
2. **Context** — personal experience? solved problem? concept?
3. **Audience** — beginners/advanced? what background?
4. **Key takeaway** — what should reader learn?

If article is about personal experience, also ask: specific numbers, results, timeline.

**Never invent facts.** Better no numbers than fake numbers.

Save answers to issue.

## Phase 2: Research (sub-agent)

```
Task(model: sonnet, subagent_type: general-purpose):

Research for blog post.

Topic: {topic}
Angle: {Phase 1 answer}
Audience: {Phase 1 answer}
Takeaway: {Phase 1 answer}

Tasks:
1. Web search on the topic (3-5 sources)
2. Find concrete examples, numbers, cases
3. Check information is current (2026)

Return structured research with sources and links.
```

Save result to issue.

## Phase 2.5: Related Posts (sub-agent)

Find related posts in user's blog for internal linking.

**Step 1:** Run script with tags from the new post:

```bash
python {baseDir}/scripts/find_related_posts.py "tag1,tag2,tag3" {blog_path}/{content_path}
```

If script returns empty or blog has no posts — skip to Phase 2.7.

**Step 2:** Rank via sub-agent:

```
Task(model: haiku, subagent_type: general-purpose):

Topic of new post: "{topic}"

Find 3-5 most related posts from this list:
{script output}

Criteria (priority order):
1. Same technique/pattern in different context
2. Continuation of author's idea
3. Mentioned tool/project
4. Adjacent problem with similar solution

Return JSON array:
[{"slug": "...", "title": "...", "link_text": "how to insert link (5-10 words)"}]

If nothing fits — return [].
```

Save result to issue.

## Phase 2.7: Brief (sub-agent)

Draft works ONLY from brief, not from raw research.

```
Task(model: sonnet, subagent_type: general-purpose):

Create structured brief for a blog post.

Topic: {topic}
Angle: {Phase 1 answer}
Audience: {Phase 1 answer}
Takeaway: {Phase 1 answer}

Research:
{Phase 2 result}

Related posts:
{Phase 2.5 result}

Extract a structured brief — article plan with specifics. Do NOT write the article.

Format:

### Thesis
One sentence — main idea.

### Key Facts
- Fact 1 (source)
- Fact 2 (source)
Only verified facts from research.

### Structure
1. Intro: {what about}
2. Problem: {what's wrong}
3. Solution: {what did}
4. Result: {what got}
5. Conclusions: {takeaway}

### Prompts for Article
What prompts author gave to agent (real or reconstructed). Minimum 1.

### Internal Links
Which related posts to mention and in what context.

### Self-Check
Check EACH fact: is it in research? has source? fact or interpretation?

Return brief in markdown.
```

Save result to issue.

## Phase 3: Draft (sub-agent)

**Before launching:** read `{baseDir}/config/author-bible.md` and `{baseDir}/config/writing-guide.md`. Pass their contents to the sub-agent.

```
Task(model: opus, subagent_type: general-purpose):

Write blog post draft.

## Author Config
{contents of author-bible.md — or "No author config provided" if empty}

## Writing Guide
{contents of writing-guide.md — or "No writing guide provided" if empty}

## Brief
{Phase 2.7 result}

## Related Posts
{Phase 2.5 result}

## Rules

PERSONA: Follow "Replacement patterns" from Author Config. If no config — use standard technical writing voice.

LINKS: Only link related posts where it makes sense in context. Links inline, not separate section. 0 links is fine if nothing fits.

REQUIREMENTS:
- Minimum 800 words (SEO)
- Personal tone matching author config
- ASCII diagram (at least one)
- Inline links in text (no "Sources" section at end)
- Frontmatter: title, date, description, tags

AEO: First paragraph = direct answer to the title question (2-3 sentences). AI engines cite first paragraph.

FAQ: 2-4 questions at end (optional, only if topic allows).

PROMPTS IN ARTICLE: Include real prompts in callout/quote blocks. Readers copy these for their own agents. Show full prompt, not paraphrase.

SSG-SPECIFIC:
- Hugo: use {{</* callout type="insight" */>}} for prompts
- Astro: use > blockquotes or MDX components
- Other: use > blockquotes

NEVER INVENT FACTS beyond what's in Brief and Author Config.

Return complete markdown with frontmatter.
```

Save result to issue.

## Phase 4: Deaify (5 parallel critics)

Launch ALL FIVE critics in parallel using Task tool, then aggregate and rewrite.

**Before launching:** read `{baseDir}/config/author-bible.md` for Critic E.

### Launch critics

```
Task(model: haiku, subagent_type: general-purpose): "Critic A — Generic Detector

Find AI-typical phrases in this text:
- 'важно понимать', 'следует отметить', 'в заключение', 'it's worth noting', 'importantly'
- 'Это не X — это Y' dramatic contrasts
- Sentences without specific names/numbers/dates
- Abstract claims without examples

Text:
{draft}

Output: numbered list with exact quotes."
```

```
Task(model: haiku, subagent_type: general-purpose): "Critic B — Rhythm Analyzer

Analyze text rhythm:
- Find 3+ consecutive sentences of similar length
- Find paragraphs where all sentences start similarly
- Check burstiness: ratio of shortest to longest sentence

EXCEPTION: Do NOT flag sequential/step lists, numbered workflows. Those help readers scan.

Text:
{draft}

Output: specific locations that need rhythm variation."
```

```
Task(model: haiku, subagent_type: general-purpose): "Critic C — Specificity Checker

Where could author add:
- Personal experience ('I tried this and...')
- Specific number or statistic
- Name/company/date reference
- Opinion marker ('I think', 'in my opinion')

Text:
{draft}

Output: 3-5 specific suggestions with WHERE to insert."
```

```
Task(model: haiku, subagent_type: general-purpose): "Critic D — Fact Checker

Extract all verifiable claims:
- Software/model versions
- Release dates and timelines
- Company names, product names, tool names
- Statistics, percentages, numbers

For each claim, flag if:
- Version might be outdated (AI models move fast)
- Date doesn't match 2026 context
- Tool might be deprecated or renamed
- Statistic seems made up (round numbers, no source)

Text:
{draft}

Output: numbered list. Format: [CLAIM]: {quote} + [FLAG]: {why suspicious}"
```

```
Task(model: haiku, subagent_type: general-purpose): "Critic E — Persona Guardian

{If author-bible exists:}
Author persona from config:
{author-bible contents}

Check text against persona:
1. PERSONA VIOLATIONS: Does text attribute actions to author that contradict persona?
2. FABRICATED STORIES: Does text claim personal experiences not listed in Facts section?
3. MADE-UP NUMBERS: Specific numbers without source or confirmation from author?

{If author-bible is empty:}
No author persona configured. Check for generic AI patterns only:
1. Text sounds like it could be about anyone (no personal voice)
2. Claims personal experiences without specifics
3. Made-up statistics

Text:
{draft}

Output: numbered list with exact quotes and suggested fixes."
```

### Fact verification

After Critic D returns, verify each flagged claim via web search (Exa or WebSearch).

### Rewrite

Aggregate all critic outputs. Rewrite with constraints:

1. **Length cap:** output ≤ original word count
2. **Vary sentence length:** mix short and long
3. **Kill generic phrases:** replace every flagged phrase
4. **Add ONE personal touch:** opinion, memory, preference
5. **Break one grammar rule:** start with "And" or "But", use fragment
6. **Persona enforcement:** fix ALL violations from Critic E
7. **Update facts:** apply corrections from Critic D verification

### Post-check

Run Critic E again on rewritten text. If persona violations remain — fix inline.

Save final text to issue.

## Phase 5: Title Options (sub-agent)

```
Task(model: opus, subagent_type: general-purpose):

Here is a finished blog post:

{deaified text}

Generate 5 title variants. Requirements:
- Maximum 60 characters (SEO limit)
- No AI clichés ("revolution", "future", "secrets", "ultimate guide")
- Each must reflect article ESSENCE, not clickbait
- CONCRETE: name tools, numbers, results
- Tool names are OK: Claude Code, Telegram, GitHub, etc.
- FORBIDDEN abstractions: "Improving productivity", "New approach to development"

Patterns that work:
1. "X: explanation" — name + benefit
2. "How I [did X]" — personal experience
3. "X instead of Y" — contrast
4. "X — your Y" — metaphor + benefit
5. Bold/unexpected angle

For each variant:
1. Title text
2. Which pattern used
3. Length in characters

Return exactly 5 variants.
```

Show user 4 best via AskUserQuestion. Mention 5th as text. User picks or writes own via "Other".

After selection — update `title` in frontmatter.

Save choice to issue.

## Phase 6: Deploy

Read `{baseDir}/config/project.md` for repo and paths.

### Save file

```bash
# Save to blog repo
cp article.md {blog_path}/{content_path}/{slug}.md
```

Slug from title: lowercase, transliterate if needed, replace spaces with hyphens, remove special chars.

### Create PR

**NEVER push to main directly.**

```bash
cd {blog_path}
git checkout -b {branch_prefix}{slug}
git add {content_path}/{slug}.md
git commit -m "feat(blog): add {title}"
git push -u origin {branch_prefix}{slug}
gh pr create --title "blog: {title}" --body "Content factory pipeline.
Tracking issue: {issue_url}"
```

### Close tracking

```bash
gh issue close {issue_number} -R {repo}
```

### Report to user

Show:
- PR link
- Post URL (will be live after merge)
- Telegram announcement date (if configured)

---

## SSG Reference

| SSG | Frontmatter | Callouts | Default content path |
|-----|-------------|----------|---------------------|
| Hugo | YAML `---` | `{{</* callout */>}}` | `content/blog/` |
| Astro | YAML `---` | `> blockquote` or MDX | `src/content/blog/` |
| Other | YAML `---` | `> blockquote` | user specifies |

## Graceful Degradation

| Missing | What happens |
|---------|-------------|
| `author-bible.md` empty | Generic voice. Critic E checks AI patterns only. Remind user to fill it. |
| `writing-guide.md` empty | Default rules from this skill. |
| `terms-glossary.md` empty | No term enforcement. |
| No Exa MCP | Use WebSearch fallback for research. Skip Critic D fact verification. |
| No blog posts yet | Skip Phase 2.5 entirely. |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Article too short | Minimum 800 words. Add context, alternatives, examples |
| No ASCII diagram | Add architecture or data flow visualization |
| Text sounds like AI | Deaify phase is mandatory. Check all 5 critics ran |
| No inline links | Research phase must find sources. Links in text, not "Sources" section |
| No prompts | Readers copy prompts. Every article needs at least one real prompt |
| Pushed to main | NEVER. Always branch + PR |
| Intro doesn't answer | First paragraph = direct answer (AEO) |

## Checklist

- [ ] Issue created for tracking
- [ ] Phase 1: Questions answered, saved to issue
- [ ] Phase 2: Research with 3-5 sources, saved to issue
- [ ] Phase 2.5: Related posts found (or skipped), saved to issue
- [ ] Phase 2.7: Structured brief, saved to issue
- [ ] Phase 3: Draft 800+ words from brief, saved to issue
- [ ] Phase 4: 5 critics + fact-check + rewrite, saved to issue
- [ ] Phase 5: Title chosen by user, saved to issue
- [ ] Phase 6: PR created, issue closed
