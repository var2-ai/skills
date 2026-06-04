---
name: ai-music-video-maker
description: >
  Build a complete, end-to-end AI music video on VAR2.ai — generate the song, design a consistent on-model singer, produce one talking-head/performance clip per song section, and stitch everything into one final video synced to the music. Use this skill WHENEVER the user wants a music video, lyric video, song clip, "make a clip for this song", "turn this song into a video", a singer/avatar performing a track, or any multi-scene video built around a generated or supplied song — even if they only say "make me a clip". It handles Hebrew (and other) lyrics with niqqud via Suno custom mode, talking-head lip-sync via the pruna-avatar model, audio segmentation for perfect sync, varied per-scene camera angles, and the final stitched render. Trigger it for any request that combines music + a performing character + multiple scenes.
---

# AI Music Video Maker (VAR2.ai, end-to-end)

You are a music-video director with a full VAR2.ai studio. This skill takes a song concept (or an existing song's lyrics) and produces a finished, music-synced video: song → consistent singer → per-section performance clips with lip-sync → one stitched final cut. It is built on hard-won knowledge of VAR2's quirks — follow it rather than improvising the pipeline from scratch.

**This is a multi-step pipeline with cost gates.** Each stage costs tokens. Always estimate cost up front, run ONE test scene end-to-end before committing to all scenes, and get explicit user approval at the gates marked below.

## Tools this skill orchestrates

All are VAR2 MCP tools (load via tool_search if deferred): `var2_list_models`, `var2_estimate_cost`, `var2_create_audio`, `var2_create_image`, `var2_create_video`, `var2_request_upload` / `var2_confirm_upload` / `var2_upload_asset` (durable first-party uploads), `var2_join_videos`, and the matching `var2_get_*_result` / `var2_check_join_status` pollers. Plus `bash_tool` with `ffmpeg`/`ffprobe` for audio segmentation. Plus `ask_user_input_v0` for taste questions.

## Phase 0 — Brief (ask, don't assume)

Use `ask_user_input_v0` to lock these before generating anything. Keep it to a few tappable questions:
- **Genre / style** of the song (rock, pop, hip-hop, ballad, etc.)
- **Lead character** (male singer / female singer / duo / let AI decide)
- **Visual mood** (neon-night, cinematic-moody, colorful-energetic, nature, etc.)
- **Aspect ratio**: 16:9 (YouTube) or 9:16 (TikTok/Reels/Shorts)
- **Lyrics source**: write new lyrics, use lyrics the user pastes, or instrumental
- **Language** of the lyrics (Hebrew, English, etc.)

If the user pastes existing lyrics, do NOT invent new ones — use theirs verbatim.

## Phase 1 — The song (Suno)

Read `references/suno.md` for the full Suno recipe. Key points:
- Use `var2_create_audio` with `model: suno`, `model_version: V5_5` (best quality) unless the user wants cheaper.
- **For real, controlled lyrics you MUST use custom mode.** Pass `customMode: true`, put the full lyrics in `prompt`, and supply BOTH `style` (short genre/mood/instrumentation description, keep under ~200 chars) and `title`. In custom mode the 500-char prompt cap does NOT apply; without it, prompts over 500 chars are rejected.
- **Hebrew lyrics: add niqqud (vowel points).** Niqqud measurably improves Suno's syllable accuracy and pronunciation. When the user gives unpointed Hebrew lyrics, add full niqqud yourself before sending. Structure tags like `[Verse 1]`, `[Chorus]`, `[Bridge]` help.
- Suno returns 2 variations per call. Share both share URLs verbatim, poll each with `var2_get_audio_result`, and let the user pick.
- **You need the exact final duration** (in seconds) of the chosen track before segmenting. Ask the user, or download the mp3 and run `ffprobe`.

## Phase 2 — The singer (consistent across all scenes)

The singer must look identical in every scene — same face, hair, outfit — only the location/angle changes.
- Generate ONE canonical singer portrait with `var2_create_image`, model `nano-banana-2` (preferred — fast, cheap, excellent; do NOT default to nano-banana-pro). Aspect ratio = the user's chosen ratio.
- **The face must be clearly visible and roughly front-facing, with the mouth unobstructed** — this is mandatory because pruna-avatar lip-syncs the mouth. Put a handheld microphone near the mouth if the user wants a performance look (it also helps focus the sync).
- Get user approval on the singer before generating the rest.
- For every other scene, reuse the canonical portrait as `image_refs` (and `image_url` with `type: image-to-image`) so identity stays locked. Change ONLY the location/background/lighting in each prompt; keep "identical face, same hair, same outfit" in the text.

## Phase 3 — Plan the scenes & segment the audio

Read `references/pipeline.md` for the exact segmentation + sync method. Summary:
- Pick N scenes (commonly 6–8). Compute `seg = total_duration / N` seconds per scene.
- Cut the song into N **contiguous, gapless** segments with ffmpeg (segment k covers `[k·seg, (k+1)·seg)`). See the script in `references/pipeline.md`.
- Each segment drives exactly one scene's clip. **Contiguity is what preserves lip-sync** in the final cut: clip k is synced to its segment, and in the stitch the clips sit back-to-back in the same order, so they line up against the full song.
- Upload each segment to VAR2 storage to get a stable, fetchable URL — VAR2's backend can't read local files. The bytes are resolved client-side, so don't push to a third-party host: use `var2_request_upload` (preferred for these real audio files — mint the signed `upload_url`, PUT the segment, use `public_url`) or `var2_upload_asset` (small inline `data`, type `audio`). Both store durably in first-party var2 (Supabase) storage with no expiry.

## Phase 4 — pruna-avatar setup & per-scene clips

**pruna-avatar is a talking-head / lip-sync model** (provider runware). It animates a portrait to sing/speak a given audio track. It is NOT a cinematic camera-motion model — it only does front-facing performance. Get realistic variety by varying location, lighting, framing distance, and *mild* angle (three-quarter, slight low/high) — never extreme angles that hide the mouth.

Required `var2_create_video` params for this model (verified):
- `model: "pruna-avatar"`
- `type: "audio-to-video"`
- `first_frame_url`: the scene's portrait URL
- `audio_url`: the scene's uploaded segment URL
- `audio_duration_seconds`: the segment length (REQUIRED — distinct from `duration`)
- `duration`: same segment length
- `resolution`: `"720p"` (cheap, 85 tok/s) or `"1080p"` (150 tok/s)
- `prompt`: describe the performance + scene, and to keep the mouth synced to only the lead voice, append: *"Lip-sync ONLY to the lead singing voice; ignore background gang vocals, crowd shouts, and instruments."*

If a `create_video` call returns a bare `Denied.` or other hard error, STOP and surface it to the user verbatim — it usually means an account/quota/rate limit, not a bad request. Do not hammer retries.

**Call budget:** `var2_create_video` allows at most 4 calls per turn. For 8 scenes, do them in two batches (4 + 4) across turns. Poll each with `var2_get_video_result` (long-polls ~5 min server-side; usually one poll per clip).

If the MCP rejects `audio-to-video` or `pruna-avatar` in its schema enums, the model isn't wired into `create_video` on the user's deployment yet. Tell the user (they may be the developer) exactly what to add: `audio-to-video` to the `type` enum and `pruna-avatar` to the `model` enum, then retry.

## Phase 5 — Final stitch (var2_join_videos)

Read `references/pipeline.md` for the exact join call. Summary:
- One `video` segment per clip, in scene order, each with its `placeholder_id` and `duration_seconds`.
- `video_audio_when_stacked: "mute"` (mute the clips' own audio).
- `background_audio_url` = the FULL original song; `background_audio_placeholder_id` = the song's id. This lays the clean full track over the muted, in-order clips — sync is preserved.
- `aspect_ratio` + `resolution` per the brief.
- **Always call with `dry_run: true` first**, show the plan + estimated render time, get approval, THEN call once with `dry_run: false`.
- Renders are slow (10+ min, sometimes 20–30). Poll `var2_check_join_status` ONCE per user check-in — never loop. If a render fails with a worker timeout, you may re-queue it once.

## Cost discipline

Before Phase 1 and again before Phase 4, run `var2_estimate_cost` for the whole batch (song + N images + N clips) and show the user the total. A typical 8-scene 720p video is ~20k–23k tokens. Always run ONE full test scene (1 image + 1 clip on its real segment) and get the user's sign-off before generating the remaining scenes.

## Quick checklist
1. Brief via `ask_user_input_v0`
2. Estimate cost, show user
3. Song (Suno custom mode + niqqud for Hebrew), user picks variation, get exact duration
4. Canonical singer (nano-banana-2, mouth visible), user approves
5. Segment audio into N contiguous parts, upload each
6. TEST SCENE end-to-end, user approves
7. Remaining scenes' portraits (image-to-image off the canonical) + clips (pruna-avatar), in batches of 4
8. `var2_join_videos` dry_run → approve → real run
9. Deliver final share/download URL verbatim
