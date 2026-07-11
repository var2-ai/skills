# Media Inputs & Uploads

How to get media **into** VAR2 tools. VAR2's backend fetches **https URLs**
and resolves **var2 assets** (share links / placeholder_ids) server-side. It
cannot read your disk or chat attachments.

## What counts as a valid media input

- ✅ a `url` returned by a previous var2 tool (create/get/upload) — pass it
  verbatim; this is the normal way to chain steps
- ✅ a var2 share link (`https://www.var2.ai/image/<id>`, `/video/<id>`,
  `/music/<id>`, `/3d/<id>`) — auto-resolved server-side
- ✅ a `placeholder_id`, where the parameter says it's accepted (join/trim
  segments, `audio_url` on trim, etc.)
- ✅ any public https URL the user pasted (image/audio/video CDN, Dropbox,
  etc.) — VAR2 fetches it directly
- ❌ a filesystem path (`./logo.png`, `/Users/me/pic.jpg`, `C:\photo.png`),
  `file://…`, `attachment://…`, or a chat-attachment handle
- ❌ any URL you invented to satisfy a parameter (`example.com`,
  `local_file_url`, `path_to_*`, `data:*` as a URL)

**A local path is never a valid tool argument.** If the value you'd pass isn't
a real https URL or a var2 asset reference, you haven't uploaded the file yet.

## The upload decision table

| Situation | Action |
|---|---|
| User attached/uploaded a file, or names a local path — no URL exists yet | **Upload first** (below), then chain the returned URL |
| Third-party URL + user asks to "import / pull into var2" | `var2_upload_asset` with `url` (re-hosts durably in var2 storage) |
| Third-party URL + user asks for an end action (upscale/animate/3D…) | Pass the URL directly to the create/modify tool — no upload |
| var2 share link, storage URL, or placeholder_id | Use directly — **never re-upload** |
| Text-only request (no URL, no "my file" wording) | Nothing to upload — pick a generator |

## How to upload

1. **Real local file, you can run an HTTP PUT** (preferred):
   `var2_request_upload({ filename, type, content_type })` → returns a signed
   single-use `upload_url` (~2h) + a durable `public_url`. PUT the raw bytes:
   `curl -X PUT --data-binary @./logo.png -H "Content-Type: image/png" "<upload_url>"`
   — bytes never pass through model context. Then use `public_url` verbatim.
2. **Small file (≤1 MB), no shell/PUT available:** `var2_upload_asset` with
   base64 `data` + `content_type`. **Always pass `expected_bytes`** (and
   `sha256` if known) so a truncated transfer is rejected instead of stored.
   Base64 over ~1.4M chars → split into parts (~200K chars each) via
   `chunk_index` / `chunk_total` / `upload_id`.
3. **Third-party URL to import:** `var2_upload_asset` with `url`.

All paths land a **durable first-party var2 URL** (no expiry) plus a
`placeholder_id`. `type` (image | video | audio) is validated against the
actual bytes — a mismatch rejects the upload. ≤100 MB per file. Never
pre-shrink or downscale a file just to fit an upload path, and **never push a
user's file to a third-party temp host** (imgur, transfer.sh, etc.) to mint a
URL — that leaks their private media and the link expires; var2's own upload
tools exist precisely for this.

**If the PUT is blocked** (sandboxed egress / host_not_allowed), recover in
order, silently: (1) file ≤ ~1 MB → `var2_upload_asset` base64 with
`expected_bytes`, chunked if needed; (2) last resort → give the user the
`user_upload_page` link from the `var2_request_upload` response (drag-and-drop
in the browser); when they say done, `var2_confirm_upload` with `path` +
`type`, then continue with `public_url`.

**`var2_confirm_upload`** (after a successful PUT) is optional: it validates
the stored bytes and registers the asset in the user's library, returning a
real `placeholder_id` — needed when the upload feeds `var2_join_videos`
chaining. Skip it if you only need the `public_url`.

## Image inputs

| Param | Tool | Role |
|---|---|---|
| `image_url` | `var2_create_image` (`type: image-to-image`) | The image being edited / transformed. |
| `image_refs` | `var2_create_image` | Reference images for character/style lock (nano-banana*, gpt-image-2 — up to 15; ignored by non-ref-aware models). |
| `image_url` | `var2_modify_image` | The image to upscale or background-remove. |
| `image` | `var2_create_3d` | Single source image for the 3D mesh. |

For `image-to-image` you must set `type: "image-to-image"` **and** pass
`image_url`. Reference images alone (without `image_url`) do not switch the
job to edit mode.

## Video inputs — pick `type` by input

| Param | `type` | Role |
|---|---|---|
| `first_frame_url` | `image-to-video` | Still the clip animates from (all models except grok-imagine). Also the portrait for `pruna-avatar`. |
| `last_frame_url` | `image-to-video` | Optional end frame (kling-3, veo-3.1, ltx-2.3, seedance-2, wan-2.7) — renders a start→end transition. |
| `reference_image_url` | `image-to-video` | **grok-imagine only** (singular). |
| `reference_image_urls` | `reference-to-video` | Character/style references — seedance-2 (≤9) / happyhorse (≤4). |
| `reference_images` | `reference-to-video` | **veo-3.1 only** — veo takes this param, not `reference_image_urls`. |
| `video_url` | `video-to-video` | The clip being edited (wan-2.7 / happyhorse: must be var2-hosted; ltx-retake: any public URL; kling-motion-control: the motion-reference video). `source_video_url` is a deprecated alias. |
| `audio_url` + `first_frame_url` + `audio_duration_seconds` | `audio-to-video` | Talking head (`pruna-avatar`): portrait + MP3/WAV/M4A ≤60s; `audio_duration_seconds` is required and drives per-second pricing. |

A `/video/<id>` link or "this clip" means `video-to-video`, not
`image-to-video`. "Animate this image" — even as a `/image/<id>` share link —
is `image-to-video` with that URL as `first_frame_url`.

## Per-model parameter gotchas (video)

- `kling` (2.6): `duration` = `"5"` | `"10"` (**string**), `aspect_ratio`
  1:1 / 16:9 / 9:16, `mode` std | pro. No end frame.
- `kling-3`: per-second. Start/end frames work two ways: `first_frame_url` /
  `last_frame_url` on `type: image-to-video`, OR `image_urls` ([start] or
  [start, end]) riding on `type: text-to-video`. Subject refs
  (`kling_elements`, named subjects with 2+ images each) and multi-shot
  (`multi_shots: true` + `shots: [{prompt, duration}]`, optional
  `total_duration` 5–15s) ride on `text-to-video`. Also `negative_prompt`,
  `sound`.
- `grok-imagine`: `duration` = `"6"` | `"10"` (**string**), `resolution`
  480p | 720p, `mode` normal | fun | spicy; i2v uses singular
  `reference_image_url`.
- `grok-imagine-video-1-5`: image-to-video only, `duration` 3–15 (number),
  aspect follows the input image.
- `veo-3.1` / `sora-2`: `aspect_ratio` = `portrait` | `landscape` (not
  ratios).
- `ltx-2.3`: `duration` in seconds (**number**), per-second pricing,
  `sound` for audio, first+last frame.
- `ltx-retake`: `mode` replace_audio | replace_video |
  replace_audio_and_video, `start_time`, `video_duration` (full trimmed
  source — drives pricing).
- `seedance-2`: `duration` 1–15 (number), `mode` pro | fast,
  `generate_audio` (default true), plus `reference_video_urls` /
  `reference_audio_urls` (≤3 each) in reference mode.
- `wan-2.7`: 720p/1080p, `negative_prompt`, V2V via `video_url`.
- `pruna-avatar`: `resolution` 720p (default) | 1080p; front-facing portrait
  with the mouth unobstructed works best.

## Model-specific capability

Accepted roles, max counts, durations, resolutions, and aspect ratios vary per
model — `var2_list_models` returns the authoritative capabilities. The tables
above are the quick map; the live list wins on conflict.

## Good source images for 3D

`trellis-2` / `tripo` work best from a single, sharp, evenly lit image of one
object on a plain background. If the user's source is busy, run
`var2_modify_image` with `type: remove-bg` first, then feed the clean result
into `var2_create_3d`.
