# Install VAR2 Skills

One skill ships in this repo:

- **`var2-generate`** — generate and edit images, videos, music, and 3D models
  through the VAR2 MCP server, with model selection, prompt engineering, cost
  estimation, polling, and Hebrew/Arabic text guidance.

VAR2 is an **MCP server with OAuth sign-in** — no CLI, and in the normal flow
no API key to paste. Setup is two parts: **connect VAR2**, then (in Claude
Code) **install the skill**.

## Step 1 — Connect VAR2 (OAuth, recommended)

You sign in with your VAR2 account in the browser — nothing to copy/paste.

**claude.ai / Claude desktop:**

1. **Settings → Connectors → Add custom connector**
2. Name it **VAR2**, URL: `https://www.var2.ai/api/mcp`
3. Click **Connect**, sign in with your VAR2 account, approve access.

**Claude Code:**

```bash
claude mcp add var2 --transport http https://www.var2.ai/api/mcp
```

A browser opens for sign-in; approve and you're connected.

**Other MCP hosts:** add an HTTP MCP server at `https://www.var2.ai/api/mcp`;
the host discovers the OAuth flow automatically.

> **Advanced / headless (CI, servers, no browser):** create a `vak_` key at
> **https://www.var2.ai/dashboard/settings?tab=developers** and connect with
> `--header "Authorization: Bearer <KEY>"`. Most users should use OAuth above.

## Step 2 — Install the skill (Claude Code)

Recommended (cross-agent), requires Node.js:

```bash
npx skills add var2-ai/skills
```

Claude Code marketplace alternative:

```
/plugin marketplace add var2-ai/skills
/plugin install var2@var2
```

Setup-script fallback (clone + symlink; does **not** connect VAR2 — do Step 1
first):

```bash
git clone --depth 1 https://github.com/var2-ai/skills.git
cd skills
./setup
```

The skill is a Claude Code add-on that makes the agent use VAR2 well.
claude.ai / desktop users get the tools from the connector alone and can skip
Step 2.

## Verify

Ask your agent:

> "List the VAR2 models."

The agent should call `var2_list_models` and return the catalog. If it gets a
sign-in / `401` challenge, finish the browser sign-in from Step 1; if the tool
isn't found, recheck the connector.

## Updating

| Method | Update command |
|---|---|
| `npx skills` | re-run `npx skills add var2-ai/skills` |
| Claude Code marketplace | `/plugin update var2@var2` |
| Setup script | `cd skills && git pull && ./setup` |
