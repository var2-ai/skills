# Contributing

Thanks for improving the VAR2 skills package.

## Principles

- Write from the **MCP consumer's** perspective only. Never add VAR2 internals
  (implementation, edge functions, DB, env vars). See [`CLAUDE.md`](CLAUDE.md).
- Keep model data **selection-focused**. Exact IDs/pricing/capabilities come
  from `var2_list_models` at runtime — don't turn the catalog into a brittle
  mirror.
- Skills must be **self-contained**: no `../` references; every `references/`
  file linked from `SKILL.md`.

## Making a change

1. Edit `var2-creative-orchestrator/SKILL.md` and/or `var2-creative-orchestrator/references/*.md`.
2. If you add a reference file, link it from `SKILL.md` (CI fails on orphans
   and on dead links).
3. **Bump the version** in all four places (CI enforces they match):
   - `VERSION`
   - `var2-creative-orchestrator/SKILL.md` frontmatter `version`
   - `.claude-plugin/plugin.json` `version`
   - `.claude-plugin/marketplace.json` `plugins[0].version`
4. If you add a skill folder, add it to
   `.claude-plugin/marketplace.json` `plugins[0].skills` (CI checks every
   `var2-*/` folder is listed) and name the folder to match the `SKILL.md`
   frontmatter `name`.

## Frontmatter rules

`SKILL.md` frontmatter must have:

- `name` — exactly the directory name (e.g. `var2-creative-orchestrator`)
- `version` — non-empty, equal to `VERSION`
- `description` — ≤1024 chars, containing a `Use when` phrase and a `NOT for`
  boundary
- `argument-hint`, `allowed-tools` — recommended

## Versioning

Semantic-ish: bump **patch** for wording/fixes, **minor** for new
guidance/reference files or a new skill, **major** for breaking changes to how
the skill instructs tool use.

## Local check

CI (`.github/workflows/validate-skills.yml`) validates frontmatter, version
sync, marketplace coverage, reference resolution, and the no-`../` rule. Skim
that workflow to reproduce the checks locally before opening a PR.
