---
version: 0.1.0
name: var2-generate
description: >-
  Generate images, videos, music, and 3D models with VAR2.ai through the VAR2
  MCP server. Use when the user wants to create or edit an image, make a video
  (text/image/reference/video-to-video), compose music, turn an image into a 3D
  mesh, upscale an image, or remove a background — especially with Hebrew or
  Arabic on-image text. Also use to estimate token cost before generating or to
  list available models. NOT for installing software, training face/identity
  models, building marketing-campaign automation, or generating media without
  the VAR2 MCP server configured (see INSTALL_FOR_AGENTS.md first).
argument-hint: "[what to create — e.g. 'a cinematic 9:16 video of a fox in snow']"
allowed-tools: mcp__var2__var2_list_models, mcp__var2__var2_estimate_cost, mcp__var2__var2_create_image, mcp__var2__var2_get_image_result, mcp__var2__var2_modify_image, mcp__var2__var2_create_video, mcp__var2__var2_get_video_result, mcp__var2__var2_create_audio, mcp__var2__var2_get_audio_result, mcp__var2__var2_create_3d, mcp__var2__var2_get_3d_result
---

# VAR2 Generate

Create and edit **images, videos, music, and 3D models** through the VAR2 MCP
server. This skill teaches you to pick the right model, set sane parameters,
estimate cost, submit one job, poll it to completion, and hand the user clean
share links.

The tool names below assume the VAR2 MCP server is registered as `var2` (tools
appear as `var2_create_image`, etc.). If your host prefixes MCP tools, the
names may look like `mcp__var2__var2_create_image` — same tools.

## Step 0 — Connection check

Do this **once** at the start of a session, not before every job.

1. Call `var2_list_models`. If it returns a model list, the MCP server is
   reachable and your API key is valid — proceed.
2. If it fails with an auth error (`401`, `invalid_key`, `expired`,
   `revoked`), the user's VAR2 API key is missing or bad. Point them to
   **https://www.var2.ai/dashboard/settings?tab=developers** to create a
   `vak_...` key, then to re-run the install step in `INSTALL_FOR_AGENTS.md`.
   Do not retry blindly.
3. If it fails with a connection/transport error, the MCP server is not
   configured. Send the user to `INSTALL_FOR_AGENTS.md`.

`var2_list_models` is the **source of truth** for model IDs, pricing, and
per-model capabilities. `references/model-catalog.md` is selection guidance;
when the live list and the catalog disagree, trust the live list.

## UX rules

- **One create per turn.** Submit **at most one** `create_*` (or
  `var2_modify_image`) call per user request. The server enforces a one-job
  call budget; batching will be rejected. Wait for the result, then ask if
  they want another.
- **Always poll to completion.** After a `create_*`/`modify` call returns a
  `placeholder_id` with `state: "waiting"`, call the matching `get_*_result`
  until `state` is `completed` or `failed`. The poll calls long-poll
  server-side — just call again if still waiting.
- **Report share URLs verbatim.** Every result includes a `var2.ai` share URL
  (and sometimes several). Print them exactly. The share page handles preview,
  download, and progress. Do **not** paste raw JSON, placeholder IDs, internal
  task IDs, or base64 blobs into the reply.
- **Reply in the user's language.** If they wrote Hebrew, reply in Hebrew.
  Model IDs and technical parameters stay in English.
- **Pick sensible defaults, don't interrogate.** Choose model, aspect ratio,
  resolution, and duration from intent. Ask at most one clarifying question,
  and only when the brief is genuinely ambiguous (e.g. portrait vs. landscape
  for a hero banner).
- **Estimate cost when it matters.** For anything beyond a quick single image,
  or whenever the user asks "how much", call `var2_estimate_cost` first and
  state the token cost before submitting.
- **Pass media by URL.** Source/reference images, first frames, and source
  videos are passed as public URLs. If the user gives a local file, ask them
  to provide a URL or upload it first.

## Workflow — image

1. Pick a model from `references/model-catalog.md` (default: `nano-banana-pro`).
   For Hebrew/Arabic on-image text see `references/non-latin-text.md`.
2. `var2_create_image` with `prompt`, `model`, `type`
   (`text-to-image` | `image-to-image`), `aspect_ratio`, optional `resolution`
   (`1K` | `2K` | `4K`, model-dependent). For edits, set
   `type: image-to-image` and pass `image_url`; pass `image_refs` for extra
   reference images.
3. Poll `var2_get_image_result` with the `placeholder_id` until done.
4. Report the share URL(s).

## Workflow — video

1. Pick a model (default: `veo-3.1`). See `references/model-catalog.md` for
   duration/resolution/aspect support — these are model-specific.
2. `var2_create_video` with `prompt`, `model`, `type`
   (`text-to-video` | `image-to-video` | `reference-to-video` |
   `video-to-video`), plus `aspect_ratio`, `resolution`, `duration`, `mode` as
   the model allows. For image-to-video pass `first_frame_url`; for
   reference-to-video pass `reference_image_urls`; for video-to-video pass
   `source_video_url`. See `references/media-inputs.md`.
3. Poll `var2_get_video_result` until done (video takes longer than image).
4. Report the share URL.

## Workflow — music

1. `var2_create_audio` (model `suno`) with `type`
   (`create-music` | `extend-music` | `replace-music-section`), `prompt`,
   optional `title`, `style` (≤200 chars), `model_version`
   (`V4` | `V4_5` | `V4_5PLUS` | `V4_5ALL` | `V5` | `V5_5`), and
   `instrumental` (bool). Suno is English-strong; Hebrew lyrics are
   unreliable — see `references/non-latin-text.md`.
2. Poll `var2_get_audio_result`. A create call returns **two** track
   variations — report both share URLs.

## Workflow — 3D

1. `var2_create_3d` with `image` (a public image URL), `model` (default
   `trellis-2`), optional `resolution` (`512` | `1024` | `1536`) and
   `texture_size` (`1024` | `2048` | `3072` | `4096`).
2. Poll `var2_get_3d_result`. Report the share URL (textured GLB output).

## Workflow — modify (upscale / remove background)

1. `var2_modify_image` with `image_url`, `type` (`upscale` | `remove-bg`),
   and `model` (`topaz-upscale` | `recraft-upscale` for upscale;
   `remove-background` for background removal).
2. Poll `var2_get_image_result` with the returned `placeholder_id`.
3. Report the share URL.

## Cost estimation

`var2_estimate_cost` takes an array of `{ model_id, type, params }` and returns
per-item and total token cost — no job is submitted. Use it before any
non-trivial generation or whenever the user asks about price. See
`references/cost-and-tokens.md`.

## Webhooks (optional)

Every `create_*`/`modify` tool accepts an optional `webhook_url`. When set,
VAR2 POSTs the final result to that URL (signed; see
`references/polling-and-webhooks.md`) instead of requiring you to poll. Most
agent sessions should just poll.

## Errors

On a failed job or tool error, read the message, consult
`references/troubleshooting.md`, fix the input (model name, media role,
unsupported param), and try again — still within the one-create-per-turn rule.
Never invent a model ID; if unsure, call `var2_list_models`.

## Reference docs

- `references/model-catalog.md` — every model and which to pick by intent
- `references/prompt-engineering.md` — writing strong prompts per modality
- `references/media-inputs.md` — image/video input roles and URL rules
- `references/cost-and-tokens.md` — estimating and reporting token cost
- `references/non-latin-text.md` — Hebrew/Arabic text and lyrics guidance
- `references/polling-and-webhooks.md` — polling cadence and webhook payloads
- `references/troubleshooting.md` — common errors and fixes
