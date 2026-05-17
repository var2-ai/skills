# CLAUDE.md — var2-ai/skills

Guidance for agents/contributors working **in this repository** (the published
skills package). This is not the VAR2 product repo.

## What this repo is

A distributable set of agent skills for the VAR2.ai **MCP server**. It contains
only Markdown skills + packaging. There is **no application code, no secrets,
no VAR2 internals** here, and there must never be.

## Hard rules

- **No internals.** Never document VAR2's server implementation, edge
  functions, database schema, environment variables, or private endpoints.
  Write only against the public MCP tool contract a customer can see.
- **No secrets.** Never commit API keys. Examples use placeholders like
  `<YOUR_VAK_KEY>`.
- **Self-contained skills.** No `../` parent-directory references in `SKILL.md`
  or `references/`. A skill must work after being copied alone into an agent's
  skills directory.
- **Live truth over hardcoded data.** Model IDs, capabilities, and pricing are
  read at runtime from `var2_list_models` / `var2_estimate_cost`. Reference
  docs are *selection guidance*, not a frozen mirror of the live catalog.

## Layout

```
var2-creative-orchestrator/SKILL.md         # the skill entrypoint (frontmatter required)
var2-creative-orchestrator/references/*.md  # supporting docs, all linked from SKILL.md
.claude-plugin/                   # Claude Code plugin + marketplace manifests
VERSION                           # single source of truth for the version
setup                             # clone+symlink installer
.github/workflows/validate-skills.yml
```

## Versioning

`VERSION` is authoritative. On any change to the skill or manifests, bump
`VERSION` and keep these in sync (CI enforces it):

- `var2-creative-orchestrator/SKILL.md` frontmatter `version`
- `.claude-plugin/plugin.json` `version`
- `.claude-plugin/marketplace.json` `plugins[0].version`

## Frontmatter contract (CI-enforced)

`SKILL.md` frontmatter must include `name` (== directory name), non-empty
`version` and `description` (≤1024 chars). The `description` must contain a
`Use when` trigger phrase and a `NOT for` boundary so the host routes the skill
correctly.

## References contract (CI-enforced)

Every `references/*.md` file must be linked from `SKILL.md`, and every
`references/...` link in `SKILL.md` must resolve. No orphans, no dead links.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the change checklist.
