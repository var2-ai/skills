# Install VAR2 Skills

One skill ships in this repo:

- **`var2-generate`** — generate and edit images, videos, music, and 3D models
  through the VAR2 MCP server, with model selection, prompt engineering, cost
  estimation, polling, and Hebrew/Arabic text guidance.

VAR2 is an **MCP server**, not a CLI. Setup is two parts: register the MCP
server, then install the skill.

## Prerequisites

1. A VAR2 API key — create one at
   **https://www.var2.ai/dashboard/settings?tab=developers** (looks like
   `vak_live_xxxxxxxx_xxxxxxxxxxxxxxxx`).
2. Register the VAR2 MCP server with your agent.

   **Claude Code:**

   ```bash
   claude mcp add var2 --transport http https://www.var2.ai/api/mcp \
     --header "Authorization: Bearer <YOUR_VAK_KEY>"
   ```

   **Other MCP hosts:** add an HTTP MCP server named `var2` pointing at
   `https://www.var2.ai/api/mcp` with an `Authorization: Bearer <key>` header.

## Option 1 — `npx skills` (recommended, cross-agent)

Works with Claude Code and any agent that loads
`~/.<agent>/skills/<name>/SKILL.md`. Requires Node.js.

```bash
npx skills add var2-ai/skills
```

## Option 2 — Claude Code marketplace

Inside Claude Code:

```
/plugin marketplace add var2-ai/skills
/plugin install var2@var2
```

Registers the skill as `/var2:generate`.

## Option 3 — Setup script

Clones the repo and symlinks the skill into your agent's skills directory.

```bash
git clone --depth 1 https://github.com/var2-ai/skills.git
cd skills
./setup
```

Auto-detects Claude Code (override with `--host <agent>`). It does **not**
configure the MCP server — do the Prerequisites step yourself. Idempotent.

## Verify

In your agent, ask:

> "List the VAR2 models."

The agent should call `var2_list_models` and return the catalog. If it errors
with `401`, recheck the API key; if the tool isn't found, recheck the MCP
server registration.

## Updating

| Method | Update command |
|---|---|
| `npx skills` | re-run `npx skills add var2-ai/skills` |
| Claude Code marketplace | `/plugin update var2@var2` |
| Setup script | `cd skills && git pull && ./setup` |
