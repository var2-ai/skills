---
version: 0.3.1
name: var2-generate
description: >-
  Generate and edit images, videos, music, voice-overs, and 3D models with
  VAR2.ai through the VAR2 MCP server. Use when the user wants to create or
  edit an image, make a video (text/image/reference/video-to-video, or a
  lip-synced talking head), compose music, generate TTS narration or dialog,
  browse voices, turn an image into a 3D mesh, upscale an image or remove a
  background, upload a local/attached file as generation input, trim or split
  audio, stitch clips and images into one video (with captions), keep a
  character consistent across generations, or estimate token cost before
  generating — especially with Hebrew or Arabic on-image text. NOT for
  installing software, training face/identity models, building
  marketing-campaign automation, or generating media without the VAR2 MCP
  server configured (see INSTALL_FOR_AGENTS.md first).
argument-hint: "[what to create — e.g. 'a cinematic 9:16 video of a fox in snow']"
allowed-tools: mcp__var2__var2_list_models, mcp__var2__var2_estimate_cost, mcp__var2__var2_create_image, mcp__var2__var2_get_image_result, mcp__var2__var2_modify_image, mcp__var2__var2_create_video, mcp__var2__var2_get_video_result, mcp__var2__var2_create_audio, mcp__var2__var2_get_audio_result, mcp__var2__var2_create_dialog, mcp__var2__var2_get_dialog_result, mcp__var2__var2_get_voice_list, mcp__var2__var2_create_3d, mcp__var2__var2_get_3d_result, mcp__var2__var2_upload_asset, mcp__var2__var2_request_upload, mcp__var2__var2_confirm_upload, mcp__var2__var2_trim_audio, mcp__var2__var2_join_videos, mcp__var2__var2_check_join_status, mcp__var2__var2_render_timeline, mcp__var2__var2_save_character, mcp__var2__var2_get_character, mcp__var2__var2_get_results
---

# VAR2 Generate

Create and edit **images, videos, music, voice-overs, and 3D models** through
the VAR2 MCP server. This skill teaches you to pick the right model, set sane
parameters, get user files into VAR2, estimate cost, submit jobs, poll them to
completion, compose results into a finished video, and hand the user clean
share links.

The tool names below assume the VAR2 MCP server is registered as `var2` (tools
appear as `var2_create_image`, etc.). If your host prefixes MCP tools, the
names may look like `mcp__var2__var2_create_image` — same tools.

## Step 0 — Connection check

Do this **once** at the start of a session, not before every job.

1. Call `var2_list_models`. If it returns a model list, VAR2 is connected and
   the user is signed in — proceed.
2. If it fails with an auth error (`401`, a `WWW-Authenticate` / sign-in
   challenge, `expired`, `revoked`), the OAuth sign-in was not completed or has
   expired. Ask the user to reconnect and finish the browser sign-in (see
   `INSTALL_FOR_AGENTS.md`, Step 1 — at https://github.com/var2-ai/skills if
   not installed alongside this skill). Do not retry blindly. (Only if they use
   the advanced headless key: their `vak_` key is bad — they recreate it at
   **https://www.var2.ai/dashboard/settings?tab=developers**.)
3. If it fails with a connection/transport error or the tool is missing, the
   MCP server is not connected. Send the user to `INSTALL_FOR_AGENTS.md`.

`var2_list_models` is the **source of truth** for model IDs, pricing, and
per-model capabilities. `references/model-catalog.md` is selection guidance;
when the live list and the catalog disagree, trust the live list. For voices,
the equivalent catalog tool is `var2_get_voice_list`.

## Getting media IN — the upload-first rule

VAR2's backend fetches **https URLs**. It cannot read your disk, your chat
attachments, or a path like `./logo.png` — passing one fails the call.

- **User supplies a local/attached file** (a photo, "my logo", a recording) →
  **upload the BYTES directly to var2 first**: `var2_request_upload` (signed
  PUT — preferred for real files) or `var2_upload_asset` with base64 `data`
  (≤1 MB, chunkable) — then pass the returned `url` / `public_url`
  **verbatim** as the next tool's `image_url` / `first_frame_url` /
  `audio_url` / etc. `var2_upload_asset`'s `url` mode is **never** the path
  for a local file: do not pass an attachment handle as `url`, and do not
  push the file to another host first just to mint a link — direct upload is
  always the first move.
- **User pastes a public https URL** → pass it straight to the create/modify
  tool; VAR2 fetches it. Only re-host via `var2_upload_asset` (`url`) when
  they explicitly ask to *import* it into VAR2 — that mode exists solely for
  content that already lives at a public URL.
- **Asset already lives in VAR2** (a `var2.ai` share link, a storage URL, or a
  `placeholder_id` from an earlier call) → use it directly; share links are
  auto-resolved. Never re-upload.
- **Never invent a URL** to satisfy a parameter, and never pass a filesystem
  path, `attachment://`, or `data:` reference as a media URL.

Full decision table, chunked uploads, and the blocked-PUT recovery ladder:
`references/media-inputs.md`.

## UX rules

- **Respect the live call budget.** Tool responses state how many `create_*`
  calls a turn allows. Independent jobs (e.g. storyboard frames that share the
  same refs) may run in the same turn when the budget allows; when in doubt,
  submit one job, wait for the result, then continue. Never blind-fire a large
  batch.
- **Always poll to completion.** After a `create_*`/`modify` call returns a
  `placeholder_id` with `state: "waiting"`, call the matching `get_*_result`
  until `state` is `completed` or `failed`. The poll calls long-poll
  server-side — just call again if still waiting; never sleep-loop. On repeat
  checks or when only chaining the URL onward, pass `inline_media: false` so
  the same media isn't re-rendered into context.
- **Report share URLs verbatim.** Every result includes a `var2.ai` share URL
  (and sometimes several). Print them exactly. The share page handles preview,
  download, and progress. Do **not** paste raw JSON, placeholder IDs, internal
  task IDs, or base64 blobs into the reply.
- **Reply in the user's language.** If they wrote Hebrew, reply in Hebrew.
  Model IDs and technical parameters stay in English.
- **Pick sensible defaults, don't interrogate.** Choose model, aspect ratio,
  resolution, and duration from intent. Ask at most one clarifying question,
  and only when the brief is genuinely ambiguous (e.g. portrait vs. landscape
  for a hero banner). Exception: `var2_join_videos` requires `aspect_ratio`
  and `resolution` and segment order — ask for those.
- **Estimate cost when it matters.** For anything beyond a quick single image,
  or whenever the user asks "how much", call `var2_estimate_cost` first and
  state the token cost before submitting. Costs are **VAR2 tokens** — never
  invent a dollar figure.
- **Chain outputs forward automatically.** When step N completes, take the
  `url` (and `placeholder_id`) from its result and feed it directly into step
  N+1. Don't make the user copy-paste.

## Workflow — image

1. Pick a model from `references/model-catalog.md` (default:
   `nano-banana-pro`). For Hebrew/Arabic on-image text see
   `references/non-latin-text.md`.
2. `var2_create_image` with `prompt`, `model`, `type`
   (`text-to-image` | `image-to-image`), `aspect_ratio`, optional `resolution`
   (`1K` | `2K` | `4K`, model-dependent). For edits, set
   `type: image-to-image` and pass `image_url`; pass `image_refs` (up to 15 on
   ref-aware models) for character/style lock.
3. Poll `var2_get_image_result` with the `placeholder_id` until done.
4. Report the share URL(s).

## Workflow — video

1. Pick a model (default: `veo-3.1`; cinematic → `seedance-2`). Duration,
   resolution, and aspect support are model-specific — see
   `references/model-catalog.md`.
2. Pick `type` by **input**, not by wording:
   - text only → `text-to-video`
   - one image to animate → `image-to-video` (`first_frame_url`;
     `grok-imagine` uses singular `reference_image_url`; several models also
     take `last_frame_url` for a start→end transition)
   - multiple reference images, consistent character in a new scene →
     `reference-to-video` (`reference_image_urls[]`; **veo-3.1 uses
     `reference_images[]` instead**)
   - an existing clip to edit/restyle → `video-to-video` (`video_url`;
     `source_video_url` is a deprecated alias)
   - a portrait + an audio track (talking head / lip-sync) → `audio-to-video`
     with `pruna-avatar`: `first_frame_url` + `audio_url` (≤60s) +
     `audio_duration_seconds` (required, drives pricing)
3. `var2_create_video` with `prompt`, `model`, `type`, plus `aspect_ratio` /
   `resolution` / `duration` / `mode` as the model allows — see
   `references/media-inputs.md` for per-model parameter gotchas (string vs.
   number durations, `kling_elements`, multi-shot `shots`, etc.).
4. Poll `var2_get_video_result` until done (video takes longer than image).
5. Report the share URL.

## Workflow — music

1. `var2_create_audio` (model `suno`) with `type`
   (`create-music` | `extend-music` | `replace-music-section`).
   - Default mode: `prompt` = a song **description** (≤500 chars); Suno writes
     the lyrics.
   - **Exact lyrics** → `customMode: true`, `prompt` = the full lyrics (the
     500-char cap does not apply), and `style` (≤200 chars) + `title` are
     required.
   - `extend-music` needs `audioRecordId` (the source track's placeholder_id)
     + `continueAt` (seconds). `replace-music-section` needs `audioRecordId` +
     `infillStartS` + `infillEndS` (~6–60s window).
   - `instrumental: true` for no vocals. `model_version` default `V5_5`.
   - Never name real artists or songs — the copyright filter rejects them.
   - Suno is English-strong; Hebrew lyrics are unreliable — see
     `references/non-latin-text.md` (niqqud helps).
2. Poll `var2_get_audio_result`. A create call returns **two** track
   variations — report both share URLs.

## Workflow — speech / voice-over (TTS)

1. Need a specific voice? `var2_get_voice_list` (`source: account` for the
   curated set, `library` to search 10K+; filter by `language`, `gender`,
   `category`). Browsing voices is always this tool, never a generation.
2. `var2_create_dialog` with `dialogue: [{voice, text}, ...]` (multi-speaker
   supported; combined text ≤5000 chars), optional `language_code` (e.g.
   `"he"` — add niqqud for Hebrew), `stability` (0 expressive / 0.5 balanced /
   1 monotone), `title`.
3. Poll `var2_get_dialog_result` (not `var2_get_audio_result` — that's music).
4. Report the share URL. Details: `references/dialog-and-voices.md`.

## Workflow — 3D

1. `var2_create_3d` with `image` (an image URL or var2 share link), `model`
   (default `trellis-2`; `tripo` for high-fidelity/PBR at a higher price —
   estimate first),
   optional `resolution` (`512` | `1024` | `1536`) and `texture_size`
   (`1024` | `2048` | `3072` | `4096`).
2. Best meshes come from a single clean subject — run `var2_modify_image`
   `type: remove-bg` first if the source is busy.
3. Poll `var2_get_3d_result`. Report the share URL (textured GLB output).

## Workflow — modify (upscale / remove background)

1. `var2_modify_image` with `image_url`, `type` (`upscale` | `remove-bg`),
   and `model` (`topaz-upscale` | `recraft-upscale` for upscale;
   `remove-background` for background removal). Image only — "extend the
   track" is `var2_create_audio`, "edit the clip" is `var2_create_video`.
2. Poll `var2_get_image_result` with the returned `placeholder_id`.
3. Report the share URL.

## Workflow — trim / split audio

`var2_trim_audio` cuts an existing track by time — the only tool for that. One
range (`start_seconds` + `end_seconds`/`duration_seconds`), a batch of
`segments` in one call, or a **smart lyrics split** (`lyrics_timestamps` +
target/min/max segment seconds) that never cuts mid-word — ideal for slicing a
song into ≤60s pieces for `pruna-avatar` scenes. Returns new asset(s) with
`url` + `placeholder_id`; the original is untouched. See
`references/composition.md`.

## Workflow — stitch / final cut (join videos)

`var2_join_videos` concatenates videos, images, and audio into one mp4. It is
**two-pass by design**:

1. Call with `dry_run: true` (the default): pass ordered `segments` (each with
   `type`, `url` or `placeholder_id`, and **required** `duration_seconds`),
   `aspect_ratio`, `resolution`, optional `background_audio_url` (+
   `background_audio_placeholder_id`), transitions, Ken Burns for images,
   `video_audio_when_stacked` (`mute` recommended when layering music).
2. Show the returned plan to the user and get explicit approval — renders take
   minutes to hours.
3. Render by calling `var2_join_videos` with **only** `{plan_id}` (the
   `jp_...` id from the dry run). If any parameter changed, resend full args
   instead.
4. Poll `var2_check_join_status` with the returned plain-UUID placeholder_id
   (never `var2_get_video_result`, and never pass a `jp_...` id to the status
   tool).

Pass `placeholder_id` on every segment that came from a var2 generation — the
render works without it, but the user's in-app editor opens empty clips
otherwise. Ask the user about segment order, aspect ratio, and resolution
before rendering. Details and a worked example: `references/composition.md`.

## Workflow — precise timeline (multi-track, captions)

For anything beyond back-to-back concatenation — explicit per-clip start
times, overlaps, text/caption overlays, per-clip volume/fades —
`var2_render_timeline` builds a multi-track project. `captions` turns word- or
line-level `timestamps` into a styled caption/lyrics track server-side.
Default `render: false` saves an editable project for the user's GUI editor;
`render: true` queues the render (poll `var2_check_join_status`). See
`references/composition.md`.

## Workflow — consistent characters

- Within a session: generate one canonical character image, then pass its URL
  as `image_refs` (images) or `reference_image_urls` / `kling_elements`
  (video) in every subsequent generation.
- Across sessions: `var2_save_character` stores a named sheet of reference
  images (`kind`: character | product | style, up to 12 images with optional
  angle labels). When the user mentions a saved character ("use Dana"),
  `var2_get_character` fetches the sheet — call it first, never regenerate the
  character from a text prompt. Call it with no `name` to list saved sheets.
- See `references/characters.md` for the full character-sheet workflow.

## Showing results

- Single asset → the matching `var2_get_*_result` (pick by media word: image /
  video / music-track / voice-over / 3D / join-render each has its own
  getter).
- **2+ finished assets** ("show all three", "line them up") →
  `var2_get_results` with 2–24 placeholder_ids or share links — one gallery,
  any mix of modalities. `display: false` fetches states/URLs as data for
  chaining without re-rendering media.

## Cost estimation

`var2_estimate_cost` takes an array of `{ model_id, type, params, quantity }`
and returns per-item and total token cost — no job is submitted. Use it before
any non-trivial generation (3+ jobs, or any video/audio/3D) or whenever the
user asks about price. See `references/cost-and-tokens.md`.

## Webhooks (optional)

Every `create_*`/`modify` tool accepts an optional `webhook_url`. When set,
VAR2 POSTs the final result to that URL (signed; see
`references/polling-and-webhooks.md`) instead of requiring you to poll. Most
agent sessions should just poll.

## Errors

On a failed job or tool error, read the message, consult
`references/troubleshooting.md`, fix the input (model name, media role,
unsupported param), and try again — reuse the same `idempotency_key` when
retrying a create call so VAR2 never double-bills. Surface VAR2's error
message to the user verbatim when you can't fix it — it's precise. Never
invent a model ID; if unsure, call `var2_list_models`.

## Reference docs

- `references/model-catalog.md` — every model and which to pick by intent
- `references/prompt-engineering.md` — writing strong prompts per modality
- `references/media-inputs.md` — uploads, URL rules, and per-type media roles
- `references/dialog-and-voices.md` — TTS, multi-speaker dialog, voice catalog
- `references/composition.md` — trim/split, join/stitch, timelines, captions
- `references/characters.md` — character sheets and cross-generation consistency
- `references/cost-and-tokens.md` — estimating and reporting token cost
- `references/non-latin-text.md` — Hebrew/Arabic text, lyrics, and TTS guidance
- `references/polling-and-webhooks.md` — polling cadence and webhook payloads
- `references/troubleshooting.md` — common errors and fixes
