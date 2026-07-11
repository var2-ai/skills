---
name: var2-routing
version: 0.3.0
description: >-
  Dispatch rules for the VAR2 MCP server — which var2 tool to call for image /
  video / audio / voice / 3D / upload / stitch / status requests. Use when a
  user prompt could map to multiple var2 tools (upload vs. generate, create
  vs. status poll, music vs. TTS, join vs. timeline) and you need the routing
  decided fast. NOT for learning how to run the tools end-to-end (that is
  var2-generate) and not for use without the VAR2 MCP server connected.
---

# VAR2.ai routing

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

**STOP — a local path is NEVER a valid tool argument.** If the value you would pass for `image_url` / `first_frame_url` / `reference_image_urls` / `audio_url` / `source_video_url` / `image` is a filesystem path or attachment — anything like `./logo.png`, `logo.png`, `/Users/me/pic.jpg`, `/mnt/data/x.png`, `C:\photo.png`, `file://…`, or a chat-attachment handle — DO NOT pass it. var2's backend cannot read your disk; the call fails. You MUST upload the bytes first and pass the returned var2 URL instead. (The MCP boundary rejects path-like values with an upload-first error, so a raw path just wastes a turn.)

**The upload procedure (do this BEFORE the create/modify/animate/3d call):**
1. Read the file's raw bytes on YOUR side (you have the file; var2 does not).
2. **Can run an HTTP PUT (preferred for any real file) →** call `var2_request_upload({ filename, type })`, PUT the raw bytes to the returned `upload_url`, then use the returned `public_url` — bytes never pass through model context.
   **No PUT available and the file is ≤1 MB →** base64-encode the bytes and call `var2_upload_asset({ type, data: "<base64>", content_type, expected_bytes })`. Use the returned `url`.
3. Pass that `url` / `public_url` verbatim as the next tool's `image_url` / `first_frame_url` / `reference_image_urls` / `audio_url` / `source_video_url`.

| You have… | Use | Result |
|---|---|---|
| a local path (relative/absolute) or an attachment, AND can run an HTTP PUT | `var2_request_upload` → PUT bytes to `upload_url` → use `public_url` | **durable** first-party var2 URL (no expiry) — preferred for real files |
| a small file (≤1 MB), no way to PUT | `var2_upload_asset` with base64 `data` | durable var2 URL + `placeholder_id` |
| a third-party / temp URL to pull in | `var2_upload_asset` with `url` | downloaded + stored durably in var2 storage — first-party, no expiry |

All three paths land DURABLE first-party var2 URLs — no third-party host, no expiry. Never push a user's file to an external temp host to mint a URL. File paths and native attachments are resolved to bytes by YOU (the client); never send a raw path to a tool argument. After a `var2_request_upload` PUT, optionally call `var2_confirm_upload` (`path` + `type`) to validate the bytes and get a `placeholder_id` for join_videos chaining.

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
| Cut / split / trim a track by time ("first 45s", "split into pieces") | `var2_trim_audio` |
| Stitch / join / merge clips back-to-back | `var2_join_videos` (dry_run first) |
| Precise timeline / overlaps / captions / text overlays | `var2_render_timeline` |
| "Save this character / product as X" | `var2_save_character` |
| "Use my saved character X" / "which characters do I have" | `var2_get_character` (fetch FIRST, never regenerate) |
| "Show / line up / compare these" + 2+ ids/links | `var2_get_results` |

`type: "image-to-video"` does not exist on var2_create_image — that's a video type, use var2_create_video.

## Video `type`

- prompt only → `text-to-video`
- prompt + 1 image → `image-to-video` (`first_frame_url`; grok-imagine uses `reference_image_url`)
- prompt + N images → `reference-to-video` (`reference_image_urls[]`; veo-3.1 uses `reference_images[]`)
- prompt + video → `video-to-video` (`video_url`; wan-2.7 restyle, ltx-retake segment replace, kling-motion-control motion transfer)
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

Pollers long-poll server-side and return the current snapshot. If `state` is still `waiting`, call the same poller again (pass `inline_media: false` on repeats) until `completed`/`failed` — re-call, don't sleep-loop. In hosts with an inline viewer that auto-polls, one snapshot is enough.

## Asset URLs

Tool inputs (`image_url`, `first_frame_url`, `reference_image_url(s)`, `video_url`, `audio_url`, `image`) accept — in order of preference:

- ✅ the `url` returned by a previous var2 tool (create/get/upload) — pass it verbatim; the normal chaining path
- ✅ a var2 **share link** (`https://www.var2.ai/image|video|music|3d/<id>`) — auto-resolved server-side
- ✅ a public https URL the user pasted (third-party image/audio/video CDN)
- ❌ a bare placeholder_id in a URL-only parameter (params documented as accepting ids DO take them: join/timeline segments, `var2_trim_audio`'s `audio_url`, `audioRecordId`, `var2_save_character` images)
- ❌ any URL you constructed or invented

To chain a placeholder_id through a URL-only downstream param: call `var2_get_<modality>_result` first (`inline_media: false`), take the `url` from its response, and pass that.

## Other shortcuts

- Cost-sensitive request ("how much", "what would 4 sora-2 videos cost"): `var2_estimate_cost` before the create_* call.
- Storyboard / multi-frame / consistent character: chain N `var2_create_image` calls — frame 1 text-to-image, frames 2..N image-to-image with `image_url` = the storage URL from the previous frame's response and `image_refs` for character lock.

## Per-model gotchas (video)

- kling (2.6): `duration` = "5" | "10" (string), `aspect_ratio` ∈ 1:1 / 16:9 / 9:16, `mode` std | pro. No end frame.
- kling-3: refs ride on type=text-to-video — `image_urls` ([start] or [start, end]) + `kling_elements` (named subjects, 2+ images each); multi-shot via `multi_shots: true` + `shots[]`.
- grok-imagine: `duration` = "6" | "10" (string), `resolution` 480p | 720p, `mode` normal | fun | spicy. i2v uses singular `reference_image_url`.
- grok-imagine-video-1-5: i2v only, `duration` 3–15 (number), aspect follows the input image.
- veo-3.1 / sora-2: `aspect_ratio` portrait | landscape
- ltx-2.3: `duration` in seconds (number, per-second pricing); first + last frame
- ltx-retake: `mode` replace_audio | replace_video | replace_audio_and_video; billed on full trimmed source duration
- seedance-2: ≤15s, `mode` pro | fast, `generate_audio` default true
- wan-2.7: 720p/1080p, v2v via `video_url` (`source_video_url` is a deprecated alias)
- pruna-avatar: type=audio-to-video; `first_frame_url` + `audio_url` (MP3/WAV/M4A, ≤60s) + `audio_duration_seconds`; `resolution` 720p (default) | 1080p

## Reply

Include the share URL verbatim. One sentence + URL — do not narrate.
