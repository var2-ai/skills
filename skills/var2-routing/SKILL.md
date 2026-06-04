---
name: var2-routing
description: Dispatch rules for the var2 MCP connector — which tool to call for image / video / audio / 3D / asset-import requests. Use when the user prompt could map to multiple var2 tools.
---

# VAR2.ai routing

> Mirrors `ROUTING_INSTRUCTIONS` in `api/mcp-experimental.ts`. Edit both together.

## Assets

var2 fetches https URLs and resolves placeholder_ids. It cannot read attachments and never invents URLs or placeholder_ids.

| Situation | Action |
|---|---|
| User attached / uploaded / "from my phone" / "this image" / "my logo" / "I just sent" — and gave NO https URL | `var2_request_upload` (durable) — or `var2_upload_asset` — first, then chain |
| Third-party URL (imgur / 0x0.st / dropbox / drive / CDN / tweet) + user asks "pull into var2" / "import" | `var2_upload_asset` (`url`) |
| Third-party URL + user asks for an end action (upscale / animate / remove-bg / 3d / join) without saying "import" | call the create/modify/join tool with that URL directly |
| var2.ai / supabase.co URL, or a placeholder_id | call the create/modify/join tool directly — never re-upload |

Neither upload tool is right when:
- the user already has a placeholder_id (the asset exists — poll or chain into create/modify);
- the URL is on var2.ai / api.var2.ai / *.supabase.co (already var2-hosted);
- there is no URL **and** no "attached / uploaded / local" wording (the request is text-only — pick a generator or reply null).

**STOP — a local path is NEVER a valid tool argument.** If the value you would pass for `image_url` / `first_frame_url` / `reference_image_urls` / `audio_url` / `source_video_url` / `image` is a filesystem path or attachment — anything like `./logo.png`, `logo.png`, `/Users/me/pic.jpg`, `/mnt/.../x.png`, `C:\photo.png`, `file://…`, or a chat-attachment handle — DO NOT pass it. var2's backend cannot read your disk; the call fails. You MUST upload the bytes first and pass the returned var2 URL instead. (The MCP boundary rejects path-like values with an upload-first error, so a raw path just wastes a turn.)

**The upload procedure (do this BEFORE the create/modify/animate/3d call):**
1. Read the file's raw bytes on YOUR side (you have the file; var2 does not).
2. **≤1 MB →** base64-encode the bytes yourself and call `var2_upload_asset({ type, data: "<base64>", content_type })`. Use the returned `url`.
   **>1 MB (or you can run an HTTP PUT) →** call `var2_request_upload({ filename, type })`, PUT the raw bytes to the returned `upload_url`, then use the returned `public_url`.
3. Pass that `url` / `public_url` verbatim as the next tool's `image_url` / `first_frame_url` / `reference_image_urls` / `audio_url` / `source_video_url`.

| You have… | Use | Result |
|---|---|---|
| a local path (relative/absolute) or an attachment, AND can run an HTTP PUT | `var2_request_upload` → PUT bytes to `upload_url` → use `public_url` | **durable** first-party var2 URL (no expiry) — preferred for real files |
| a small file (≤1 MB) | `var2_upload_asset` with base64 `data` | durable var2 URL + `placeholder_id` |
| a third-party / temp URL to pull in | `var2_upload_asset` with `url` | downloaded + stored durably in var2 (Supabase) storage — first-party, no expiry |

All three paths land DURABLE first-party var2 (Supabase) URLs — no third party, no expiry. File paths and native attachments are resolved to bytes by YOU (the client); never send a raw path to a tool argument. After a `var2_request_upload` PUT, optionally call `var2_confirm_upload` (`path` + `type`) to validate the bytes and get a `placeholder_id` for join_videos chaining.

Never fabricate URLs to satisfy a tool argument. Specifically never invent: example.com, abc123, placeholder.X, local_file_url, path_to_*, /uploads/*, attachment://*, data:*.

## Modality

| User wants | Tool |
|---|---|
| New image / "image of X" / variation / "Y instead of X" | `var2_create_image` |
| Edit content/style of an image ("add lens flare", "change background", "blue version") | `var2_create_image` (type=image-to-image) |
| Upscale / "to 4K" / sharper / enhance resolution | `var2_modify_image` (type=upscale) |
| Remove background / transparent PNG / cutout | `var2_modify_image` (type=remove-bg) |
| Animate / "make a video of this" / spin / pan / "i2v" | `var2_create_video` (type=image-to-video) |
| 3D / GLB / mesh / "rotate in 3d" — with image source | `var2_create_3d` |
| 3D without image source ("a kitten in 3d") | `var2_create_image` then `var2_create_3d` |
| Song / music / extend track / "replace seconds X-Y" | `var2_create_audio` |
| Voice-over / narrate / TTS | `var2_create_dialog` |
| Stitch / join / merge / timeline | `var2_join_videos` |

`type: "image-to-video"` does not exist on var2_create_image — that's a video type, use var2_create_video.

## Video `type`

- prompt only → `text-to-video`
- prompt + 1 image → `image-to-video` (`first_frame_url`; grok-imagine uses `reference_image_url`)
- prompt + N images → `reference-to-video` (`reference_image_urls[]`)
- prompt + video → `video-to-video` (wan-2.7; `source_video_url`)
- portrait + audio → `audio-to-video` (pruna-avatar; `first_frame_url` + `audio_url` + `audio_duration_seconds`)

## Audio `type`

- New song → `create-music`
- "Extend by N seconds" / "make it longer" / "continue past X" → `extend-music` + `audioRecordId` + `continueAt`
- TIME RANGE + replace/swap/redo/infill on an existing track ("replace seconds X-Y", "swap the chorus", "infill X-Y") → `replace-music-section` + `audioRecordId` + `infillStartS` + `infillEndS` (NEVER create-music)

## Catalog vs. generate

User asking about options, not asking to generate:
- "what voices do you have", "browse voices", "I need a [kid] voice — what do you have" → `var2_get_voice_list`
- "what models", "available models", "list 3d/image/video/audio models", "show me available <X> models", "any other <X> options", "browse models" → `var2_list_models` (use `modality`)

A user asking to **show / list / browse** anything is always a catalog query, never a generation request — even if a modality word ("3d", "image", "video") appears in the same sentence.

## Text-only requests (no URL, no local-file wording)

When the user's message contains neither an https URL nor any local-asset wording ("attached", "uploaded", "my X", "this X", "from my phone"), the request is text-only. Route by intent:
- image / variation / "Y instead of X" → `var2_create_image`
- video → `var2_create_video` (type=text-to-video)
- song / music → `var2_create_audio`
- voice / narration → `var2_create_dialog`
- "song AND cover" / "song with cover art" → `var2_create_audio` (then a second call to `var2_create_image` for the cover)
- "X in 3d" without an image → `var2_create_image` first

Never call `var2_upload_asset` for a text-only request. There is nothing to upload.

## Polls (placeholder_id + …)

| Mentions | Tool |
|---|---|
| image / "is the image ready" | `var2_get_image_result` |
| song / audio / music / track | `var2_get_audio_result` |
| narration / voice-over / dialog | `var2_get_dialog_result` |
| video | `var2_get_video_result` |
| joined / stitched / merged / timeline / "the join render" | `var2_check_join_status` |
| 3d / glb / mesh | `var2_get_3d_result` |

Polls return immediately. The inline viewer auto-polls — never loop a poll yourself.

## Asset URLs — CRITICAL

Tool inputs (`image_url`, `first_frame_url`, `reference_image_url(s)`, `source_video_url`, `audio_url`, `image`, and every other URL argument on **every tool except var2_upload_asset**) MUST be a **storage URL** that returns the raw bytes:

- ✅ `https://api.var2.ai/storage/v1/object/public/<bucket>/<path>`
- ✅ `https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>`
- ✅ a public https URL the user pasted (third-party image/audio/video CDN)
- ❌ `https://www.var2.ai/image/<placeholder_id>` — this is a **share page** (HTML). Backend cannot fetch image bytes from it; the call will fail.
- ❌ any URL constructed from a placeholder_id alone

Where the storage URL comes from: **every create_\*/upload_asset/get_\*_result tool returns a `url` field on completion** — that's the storage URL. Pass that value verbatim into the next tool.

To chain a placeholder_id through a downstream tool: call `var2_get_<modality>_result` first, take the `url` from its response, then pass that `url` into `var2_modify_image` / `var2_create_video` / `var2_create_3d` / `var2_join_videos`.

## Other shortcuts

- Cost-sensitive request ("how much", "what would 4 sora-2 videos cost"): `var2_estimate_cost` before the create_* call.
- Storyboard / multi-frame / consistent character: chain N `var2_create_image` calls — frame 1 text-to-image, frames 2..N image-to-image with `image_url` = the storage URL from the previous frame's response and `image_refs` for character lock.

## Per-model gotchas (video)

- kling*: `duration` = "5" | "10" (string), `aspect_ratio` ∈ 1:1 / 16:9 / 9:16, `mode` std | pro
- grok-imagine: `duration` = "6" | "10" (string), `resolution` 480p | 720p, `mode` normal | fun | spicy. i2v uses singular `reference_image_url`.
- veo-3.1 / sora-2: `aspect_ratio` portrait | landscape
- ltx*: `duration` in seconds (number, per-second pricing)
- seedance-2: ≤15s, `mode` pro | fast
- wan-2.7: 1080p, v2v via `source_video_url`
- pruna-avatar: type=audio-to-video; `first_frame_url` + `audio_url` (MP3/WAV/M4A, ≤60s) + `audio_duration_seconds`; `resolution` 720p (default) | 1080p

## Reply

Include the share URL verbatim. One sentence + URL — do not narrate.
