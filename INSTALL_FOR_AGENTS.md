# Install for Agents

You are an AI coding agent. The user asked you to install / connect VAR2.
VAR2 is an **MCP server with OAuth sign-in** — there is no CLI and, in the
normal flow, **no API key to paste**. Follow this exactly.

## Step 1 — Connect the VAR2 MCP server (OAuth, primary path)

The server speaks MCP over HTTP at:

```
https://www.var2.ai/api/mcp
```

It uses OAuth 2.1 (PKCE) with dynamic client registration — the user signs in
with their VAR2 account in a browser; no token handling on your side.

**Claude Code:**

```bash
claude mcp add var2 --transport http https://www.var2.ai/api/mcp
```

Then tell the user: a browser window will open — sign in to VAR2 and approve
access. (Claude Code performs the OAuth handshake automatically; do **not**
pass an `Authorization` header in this flow.)

**claude.ai / Claude desktop:** the user adds it themselves via
**Settings → Connectors → Add custom connector**, names it `VAR2`, pastes
`https://www.var2.ai/api/mcp`, clicks **Connect**, and signs in. You cannot do
this step for them — instruct them, then continue once they confirm.

**Other MCP hosts:** add an HTTP MCP server at `https://www.var2.ai/api/mcp`;
the host will discover the OAuth endpoints and run the sign-in.

Use the server name **`var2`** so tools resolve as `var2_*`.

### Advanced / headless only — static API key

For non-interactive use (CI, servers, no browser), a long-lived key works
instead of OAuth. Only use this if the user explicitly needs headless auth:

1. User creates a key at
   **https://www.var2.ai/dashboard/settings?tab=developers** (`vak_live_...`).
2. `claude mcp add var2 --transport http https://www.var2.ai/api/mcp --header "Authorization: Bearer <KEY>"`

Treat the key as a secret — never echo it back or write it to the repo.

## Step 2 — Install this skill (Claude Code only)

The skill makes the agent *use* VAR2 well; it is separate from the connection.
Skip for non-Claude-Code hosts (they still get the tools via the connector).

```bash
npx skills add var2-ai/skills
```

or, in Claude Code: `/plugin marketplace add var2-ai/skills` then
`/plugin install var2@var2`.

## Step 3 — Verify

Call the `var2_list_models` tool.

- Returns a model list → connected. Done.
- `401` / `WWW-Authenticate` challenge → sign-in not completed or expired; have
  the user re-run the connect step and finish the browser sign-in.
- Tool not found / connection error → MCP server not registered; redo Step 1.

## Step 4 — Done

Tell the user, briefly:

> "VAR2 is connected. Try: *Create a 9:16 image with the Hebrew text
> 'פתוח 24 שעות'* or *Make an 8-second cinematic video of a fox in snow.*"

Do not dump skill paths, file structure, or internals. Confirm + give a
starter prompt.
