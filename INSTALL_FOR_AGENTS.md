# Install for Agents

You are an AI coding agent. The user asked you to install the VAR2 skills.
VAR2 is an **MCP server** — there is no CLI to install. "Install" means
(1) registering the VAR2 MCP server with your host and (2) installing this
skill. Follow this exactly.

## Step 1 — Get a VAR2 API key

Ask the user to create an API key:

> Open **https://www.var2.ai/dashboard/settings?tab=developers**, create an API
> key, and paste it here. It looks like `vak_live_xxxxxxxx_xxxxxxxxxxxxxxxx`.

Wait for the key. Treat it as a secret — never echo it back in full, never
write it into the repo or into chat logs.

## Step 2 — Register the VAR2 MCP server

The server speaks MCP over HTTP at:

```
https://www.var2.ai/api/mcp
```

Authentication is a bearer token (the `vak_...` key).

**Claude Code:**

```bash
claude mcp add var2 --transport http https://www.var2.ai/api/mcp \
  --header "Authorization: Bearer <PASTE_VAK_KEY>"
```

**Other MCP hosts:** add an HTTP MCP server named `var2` with URL
`https://www.var2.ai/api/mcp` and an `Authorization: Bearer <vak key>` header,
using that host's MCP configuration mechanism.

Use the server name **`var2`** so tools resolve as `var2_*` (e.g.
`var2_create_image`).

## Step 3 — Install this skill

Recommended (cross-agent), requires Node.js:

```bash
npx skills add var2-ai/skills
```

Claude Code plugin alternative:

```
/plugin marketplace add var2-ai/skills
/plugin install var2@var2
```

Either installs the `var2-creative-orchestrator` skill into the agent's skills directory.

## Step 4 — Verify

Call the `var2_list_models` tool.

- Returns a model list → connected and authenticated. Done.
- `401` / auth error → key is wrong or not attached. Recheck Step 1–2.
- Connection error / tool not found → MCP server not registered. Recheck
  Step 2.

## Step 5 — Done

Tell the user, briefly:

> "VAR2 is connected. Try: *Create a 9:16 image with the Hebrew text
> 'פתוח 24 שעות'* or *Make an 8-second cinematic video of a fox in snow.*"

Do not dump skill paths, file structure, or internals. Confirm + give a
starter prompt.
