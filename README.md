# VAR2.ai Skills

Agent skills for the **VAR2.ai MCP server** — generate and edit **images,
videos, music, and 3D models** from your AI coding agent.

These are Markdown-based skills compatible with Claude Code and any agent that
loads `~/.<agent>/skills/<name>/SKILL.md`. VAR2 is delivered as an **MCP
server** (no CLI to install).

## Quick start

1. **Connect VAR2** (OAuth — sign in, nothing to paste):
   - **claude.ai / desktop:** Settings → Connectors → Add custom connector →
     name **VAR2**, URL `https://www.var2.ai/api/mcp` → Connect → sign in.
   - **Claude Code:** `claude mcp add var2 --transport http https://www.var2.ai/api/mcp`
     (a browser opens to sign in).
2. **Install the skill** (Claude Code add-on):

   ```bash
   npx skills add var2-ai/skills
   ```

Then ask your agent: *"Create a 9:16 image with the Hebrew text 'פתוח 24 שעות'"*
or *"Make an 8-second cinematic video of a fox in the snow."*

Full instructions: [`INSTALL.md`](INSTALL.md). Agents: see
[`INSTALL_FOR_AGENTS.md`](INSTALL_FOR_AGENTS.md).

## Skills

| Skill | What it does |
|---|---|
| `var2-generate` | The core skill: image / video / music / voice-over / 3D generation and editing, uploads, upscale & background-removal, model selection, cost estimation, polling, stitching & timelines, character consistency, Hebrew/Arabic text guidance. |
| `var2-routing` | Fast dispatch rules — which var2 tool to call when a prompt could map to several (upload vs. generate, create vs. status, music vs. TTS). |
| `ai-music-video-maker` | End-to-end music video: Suno song → consistent on-model singer → lip-synced per-section clips (`pruna-avatar`) → one stitched final cut. |
| `creative-orchestrator` | Decomposes an open-ended creative brief into a custom multi-step VAR2 pipeline (character sheets, storyboards, approval gates) and executes it. |

## What's covered

- **Image** — text-to-image and image-to-image across the VAR2 model lineup
  (default `nano-banana-pro`), with best-in-class Hebrew/Arabic on-image text.
- **Video** — text/image/reference/video-to-video plus lip-synced talking
  heads (default `veo-3.1`; `seedance-2` cinematic; `pruna-avatar` avatar),
  multi-shot narratives, native-audio models.
- **Music** — Suno (`create` / `extend` / `replace-section`), instrumental or
  vocal, custom-lyrics mode.
- **Speech** — TTS voice-overs and multi-speaker dialog (ElevenLabs voices,
  browsable catalog).
- **3D** — image-to-3D textured GLB meshes (`trellis-2`, `tripo`).
- **Modify & compose** — upscale, background removal, audio trim/split,
  video stitching with dry-run plans, precise multi-track timelines with
  captions.
- **Assets** — durable uploads of local/attached files into VAR2 storage;
  saved character/product sheets for cross-session consistency.
- **Cost** — token estimation before every non-trivial job.

Model IDs, capabilities, and pricing are always read live from
`var2_list_models`; the reference docs under
[`var2-generate/references/`](var2-generate/references/) are selection
guidance.

## Distribution

- **Claude Code plugin (one step — MCP server + all skills):**
  `/plugin marketplace add var2-ai/skills` then `/plugin install var2@var2`.
  The plugin bundles the VAR2 MCP server config, so the connector and the
  skills install together; a browser opens once for the OAuth sign-in.
- `npx skills add var2-ai/skills` (cross-agent, skills only — connect the MCP
  server separately, see `INSTALL.md`)
- `./setup` script (clone + symlink, skills only)

## License

MIT — see [`LICENSE`](LICENSE).
