# VAR2.ai Skills

Agent skills for the **VAR2.ai MCP server** — generate and edit **images,
videos, music, and 3D models** from your AI coding agent.

These are Markdown-based skills compatible with Claude Code and any agent that
loads `~/.<agent>/skills/<name>/SKILL.md`. VAR2 is delivered as an **MCP
server** (no CLI to install).

## Quick start

1. Create a VAR2 API key:
   **https://www.var2.ai/dashboard/settings?tab=developers**
2. Register the MCP server (Claude Code):

   ```bash
   claude mcp add var2 --transport http https://www.var2.ai/api/mcp \
     --header "Authorization: Bearer <YOUR_VAK_KEY>"
   ```
3. Install the skill:

   ```bash
   npx skills add var2-ai/skills
   ```

Then ask your agent: *"Create a 9:16 image with the Hebrew text 'פתוח 24 שעות'"*
or *"Make an 8-second cinematic video of a fox in the snow."*

Full instructions: [`INSTALL.md`](INSTALL.md). Agents: see
[`INSTALL_FOR_AGENTS.md`](INSTALL_FOR_AGENTS.md).

## Skills

| Skill | Invoke | What it does |
|---|---|---|
| `var2-creative-orchestrator` | `/var2:creative-orchestrator` | Decompose any creative brief into a multi-step VAR2 pipeline (image / video / music / 3D) and execute it end-to-end. Storyboard pre-flight for multi-shot video, parallel-where-possible execution, model selection, cost estimation, Hebrew/Arabic guidance. |

## What's covered

- **Image** — text-to-image and image-to-image across the VAR2 model lineup
  (defaults `gpt-image-2` / `nano-banana-2`), with strong Hebrew/Arabic
  on-image text.
- **Video** — text/image/reference/video-to-video. Default `veo-3.1` for
  everyday clips; `seedance-2` for anything cinematic. Multi-shot pipelines
  via character-sheet → storyboard-frame → video pre-flight.
- **Music** — Suno (`create` / `extend` / `replace-section`), instrumental or
  vocal.
- **3D** — image-to-3D textured GLB meshes (`trellis-2`).
- **Modify** — upscale and background removal.
- **Cost** — token estimation before every non-trivial pipeline.

Model IDs, capabilities, and pricing are always read live from
`var2_list_models`; the reference docs under
[`var2-creative-orchestrator/references/`](var2-creative-orchestrator/references/)
are supplementary selection guidance.

## Distribution

- `npx skills add var2-ai/skills` (recommended, cross-agent)
- Claude Code plugin: `/plugin marketplace add var2-ai/skills` then
  `/plugin install var2@var2`
- `./setup` script (clone + symlink)

## License

MIT — see [`LICENSE`](var2-skills/LICENSE).
