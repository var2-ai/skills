# Install for Agents

You are an AI coding agent. The user asked you to install / connect VAR2.
VAR2 is an **MCP server with OAuth sign-in** — there is no CLI and, in the
normal flow, **no API key to paste**. Follow this exactly.

## Step 0 — Pick the path by host

- **Claude Code** → use the **plugin** (Step 1a). One install registers the
  VAR2 MCP server AND all four skills together. Do not also run
  `claude mcp add` — the plugin already carries the server config.
- **Any other host** (claude.ai, Claude desktop, ChatGPT, other MCP clients)
  → connect the MCP server manually (Step 1b). Skills are a Claude Code
  feature; on these hosts the connector alone is the full install.

## Step 1a — Claude Code: install the plugin (server + skills in one step)

Run these two slash commands (they are Claude Code commands, not shell):

```
/plugin marketplace add var2-ai/skills
/plugin install var2@var2
```

Restart the session if prompted. On the first VAR2 tool call a browser opens —
tell the user to sign in to VAR2 and approve access. Then go to Step 2.

If the plugin system is unavailable, fall back to the manual pair:
`claude mcp add var2 --transport http https://www.var2.ai/api/mcp` for the
server, plus `npx skills add var2-ai/skills` for the skills.

## Step 1b — Other hosts: connect the VAR2 MCP server (OAuth)

The server speaks MCP over HTTP at:

```
https://www.var2.ai/api/mcp
```

It uses OAuth 2.1 (PKCE) with dynamic client registration — the user signs in
with their VAR2 account in a browser; no token handling on your side.

**claude.ai / Claude desktop:** the user adds it themselves via
**Settings → Connectors → Add custom connector**, names it `VAR2`, pastes
`https://www.var2.ai/api/mcp`, clicks **Connect**, and signs in. You cannot do
this step for them — instruct them, then continue once they confirm.

**ChatGPT (Plus/Pro/Business):** the user enables
**Settings → Connectors → Advanced → Developer mode**, then creates a
connector with URL `https://www.var2.ai/api/mcp` and completes the OAuth
sign-in. There is no skills system on ChatGPT — the connector alone is the
full install.

**Other MCP hosts:** add an HTTP MCP server at `https://www.var2.ai/api/mcp`;
the host will discover the OAuth endpoints and run the sign-in.

Use the server name **`var2`** so tools resolve as `var2_*`. Do **not** pass
an `Authorization` header in the OAuth flow.

### Advanced / headless only — static API key

For non-interactive use (CI, servers, no browser), a long-lived key works
instead of OAuth. Only use this if the user explicitly needs headless auth:

1. User creates a key at
   **https://www.var2.ai/dashboard/settings?tab=developers** (`vak_live_...`).
2. `claude mcp add var2 --transport http https://www.var2.ai/api/mcp --header "Authorization: Bearer <KEY>"`

Treat the key as a secret — never echo it back or write it to the repo.

## Step 2 — Verify

Call the `var2_list_models` tool.

- Returns a model list → connected. Done.
- `401` / `WWW-Authenticate` challenge → sign-in not completed or expired; have
  the user re-run the connect step and finish the browser sign-in.
- Tool not found / connection error → MCP server not registered; redo Step 1a
  (Claude Code) or 1b (other hosts).

## Step 3 — Done

Tell the user, briefly:

> "VAR2 is connected. Try: *Create a 9:16 image with the Hebrew text
> 'פתוח 24 שעות'* or *Make an 8-second cinematic video of a fox in snow.*"

Do not dump skill paths, file structure, or internals. Confirm + give a
starter prompt.
