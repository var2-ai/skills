# Composition — Trim, Stitch, Timelines, Galleries

Turning generated assets into a finished piece: cutting audio, concatenating
clips, building precise multi-track timelines with captions, and showing a set
of results together.

## Trim / split audio — `var2_trim_audio`

The only tool for cutting an existing track by time. Returns **new** asset(s)
(`url` + `placeholder_id`); the original is untouched. `audio_url` accepts a
storage URL, a var2 share link (`www.var2.ai/music/<id>`), or a
placeholder_id.

Three modes:

1. **Single cut** — `start_seconds` + (`end_seconds` or `duration_seconds`):
   "keep only 0:12–0:40", "first 45 seconds".
2. **Batch split** — `segments: [{start_seconds, end_seconds, id?}, ...]`
   (≤32 in one call): cut a song into contiguous scene segments in a single
   call. Give each an `id` like `"scene_1"` — it's echoed on the result.
3. **Smart lyrics split** — `lyrics_timestamps` (word-level `{word, start,
   end, break?}`; mark line/chorus ends with `break`) + `target/min/
   max_segment_seconds`. The server picks cut points that **never land
   mid-word** and prefer line/chorus ends. Default max is 60s — exactly the
   `pruna-avatar` audio cap, which is the main use: slicing a song into
   lip-syncable scene segments.

`max_segment_seconds` is a hard ceiling in every mode; explicit ranges that
overshoot are rejected.

## Stitch / final cut — `var2_join_videos`

Concatenates videos, images, and audio into one mp4. **Two-pass, always:**

### Pass 1 — plan (`dry_run: true`, the default)

```json
{
  "segments": [
    { "type": "video", "placeholder_id": "<clip1-id>", "duration_seconds": 8,
      "transition": "fade", "transition_seconds": 0.5 },
    { "type": "image", "url": "<poster-url>", "duration_seconds": 4,
      "ken_burns": true },
    { "type": "video", "placeholder_id": "<clip2-id>", "duration_seconds": 8 }
  ],
  "aspect_ratio": "16:9",
  "resolution": "1080p",
  "background_audio_url": "<song-url>",
  "background_audio_placeholder_id": "<song-id>",
  "video_audio_when_stacked": "mute"
}
```

- `duration_seconds` is **required on every segment** — there is no
  server-side probing. You already know it for var2-generated media (you chose
  it at create time); for external URLs and images, ask the user.
- `aspect_ratio` (16:9 | 9:16 | 1:1) and `resolution` (720p | 1080p) are
  required — **ask the user** rather than assuming; 1080p renders ~2× slower.
- Ask about segment **order** too — it can't be changed after rendering
  starts.
- Pass `placeholder_id` on every var2-generated segment (and
  `background_audio_placeholder_id` with `background_audio_url`). The render
  works without them, but the user's in-app editor would open empty clips.
- When the timeline stacks video + music, recommend
  `video_audio_when_stacked: "mute"` (cleanest); `reduce` ducks video audio to
  0.2×; `keep` usually clashes.
- Optional per-segment: `trim_start_seconds`, `playback_rate` (video),
  `filter` (sepia/grayscale/blur/vignette), `object_fit` (`contain` to
  letterbox instead of crop), `volume`, `muted`; `ken_burns` on images
  (subtle 1.0→1.1 zoom — recommended for slideshows).

### Pass 2 — render

Show the returned plan (order, durations, estimated render time) to the user
and get explicit approval — renders take **minutes to hours** and use compute
budget. Then call `var2_join_videos` with **only `{plan_id}`** (the `jp_...`
id). If any parameter changed after the dry run, resend full args instead;
`{plan_id, dry_run: true}` re-displays a stored plan.

### Status

Poll `var2_check_join_status` with the **plain-UUID placeholder_id** returned
by the render call.

- A `jp_...` id is a **plan**, not a render — it goes back to
  `var2_join_videos` to start the render, never to the status tool.
- Never poll a join render with `var2_get_video_result`.
- Renders are slow; report progress to the user rather than hammering the
  status tool. If a render fails with a worker timeout, re-queue once.

### Music-video sync pattern

To lay a full song over N scene clips without drift: keep the clips in
scene order, `video_audio_when_stacked: "mute"`, and pass the **full**
original song as `background_audio_url` (+ its placeholder_id). If each clip
was lip-synced to a contiguous segment of the song (see `var2_trim_audio`
batch mode), the muted clips line up against the clean full track and sync is
preserved.

## Precise timelines — `var2_render_timeline`

For anything `var2_join_videos` can't express — explicit per-clip start times,
overlapping tracks, text/caption overlays, per-clip volume/fade/trim — build a
multi-track project:

- `tracks: [{type: video|image|audio|text, clips: [...]}]` — each clip takes
  `asset` (url / share link / placeholder_id) or `text`, `duration_seconds`
  (required), optional `start_seconds` (omit to append after the previous
  clip), `trim_start_seconds`, `volume`, `fade_in/out_seconds`, `muted`,
  `objectFit`.
- `captions` builds a styled caption/lyrics track server-side from word- or
  line-level `timestamps: [{text, start_seconds, end_seconds}]` — no frame
  math needed; `max_words_per_caption` (default 4), `position`, `style`.
- `render: false` (default) saves an **editable project** the user can open in
  the var2 GUI editor; `render: true` also queues the render — poll
  `var2_check_join_status`.
- Simple back-to-back concatenation → prefer `var2_join_videos`.

## Showing multiple results — `var2_get_results`

"Show me all of those", "line these three up", "compare them" → one gallery
call with 2–24 `items` (placeholder_ids and/or var2 share links, any mix of
modalities). Finished items show instantly; rendering ones fill in.

- Never call it with fewer than 2 items — a single asset is the matching
  `var2_get_*_result`.
- `display: false` returns states + URLs as plain data — use it to check a
  batch or collect URLs for chaining without re-rendering media into the
  conversation.
