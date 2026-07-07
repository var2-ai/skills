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

1. Edit the skill's `SKILL.md` and/or its `references/*.md` (skills live at
   `var2-generate/` and under `skills/`).
2. If you add a reference file, link it from that skill's `SKILL.md` (CI fails
   on orphans and on dead links).
3. **Bump the version** everywhere (CI enforces they match):
   - `VERSION`
   - every `SKILL.md` frontmatter `version` (all skills share the package
     version)
   - `.claude-plugin/plugin.json` `version`
   - `.claude-plugin/marketplace.json` `plugins[0].version`
4. If you add a skill folder, add it to
   `.claude-plugin/marketplace.json` `plugins[0].skills` (CI checks every
   skill folder is listed) and name the folder to match the `SKILL.md`
   frontmatter `name`.

## Frontmatter rules

`SKILL.md` frontmatter must have:

- `name` — exactly the directory name (e.g. `var2-generate`)
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
sync, marketplace coverage, reference resolution, and the no-`../` rule. Run
the same checks locally before opening a PR:

```bash
python3 scripts/validate_skills.py
```
