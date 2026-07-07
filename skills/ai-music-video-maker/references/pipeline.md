# Segmentation, Sync & the Final Stitch

The mechanical heart of the music video: cutting the song into scene segments
that preserve lip-sync, and stitching the clips back into one video over the
clean full track.

## Why contiguous segments preserve sync

Each scene's clip is lip-synced (pruna-avatar) to one **contiguous, gapless**
segment of the song: segment k covers `[k·seg, (k+1)·seg)`. In the final
stitch the clips sit back-to-back **in the same order**, so frame 0 of clip k
lands exactly at second `k·seg` of the full song. Mute the clips, lay the
clean full track underneath, and the mouths line up. Any gap, overlap, or
reordering breaks this.

## Cutting the song — `var2_trim_audio` (one call)

The track is already a var2 asset (Suno output), so pass its `placeholder_id`
directly — no download, no upload:

```json
{
  "audio_url": "<song-placeholder-id>",
  "segments": [
    { "start_seconds": 0,  "end_seconds": 24, "id": "scene_1" },
    { "start_seconds": 24, "end_seconds": 48, "id": "scene_2" },
    { "start_seconds": 48, "end_seconds": 72, "id": "scene_3" }
  ],
  "max_segment_seconds": 60
}
```

- Segments must be **contiguous** (each `start_seconds` = previous
  `end_seconds`) and ≤60s each (the pruna-avatar audio cap; also a hard
  ceiling the tool enforces via `max_segment_seconds`).
- Up to 32 segments in one call. Each result carries your `id`, a durable
  `url`, and a `placeholder_id` — the `url` goes straight into pruna-avatar's
  `audio_url`.

**Smart lyrics split** (better cuts, if you have word-level timestamps): pass
`lyrics_timestamps: [{word, start, end, break?}]` (mark line/chorus ends with
`break`) plus `target_segment_seconds` (e.g. 8–12 for fast-cut,
20–30 for long takes). The server picks cut points that never land mid-word
and prefer line/chorus ends — segments come back as `scene_1..N`. Segment
lengths will vary slightly; use each segment's actual length as that clip's
`audio_duration_seconds` and `duration`.

**Fallback (track not in var2):** upload the full track first
(`var2_request_upload` → PUT the bytes → `public_url`; ≤1 MB files can go
base64 via `var2_upload_asset`), then trim as above. Local ffmpeg cutting
(`ffmpeg -ss <start> -t <len> -i song.mp3 -c copy seg_k.mp3`) plus one upload
per segment also works but is strictly more steps and more failure points.

## Per-scene clips (recap)

One `var2_create_video` per scene: `model: pruna-avatar`,
`type: audio-to-video`, `first_frame_url` = the scene's portrait,
`audio_url` = the segment's URL, `audio_duration_seconds` = **that segment's
actual length** (required, drives pricing), `duration` the same,
`resolution` 720p (draft/cheap) or 1080p (final). Respect the per-turn call
budget stated in the tool response; poll each clip with
`var2_get_video_result`.

## The final stitch — `var2_join_videos`

Two-pass, always:

### 1. Plan (`dry_run: true`, default)

```json
{
  "segments": [
    { "type": "video", "placeholder_id": "<clip1-id>", "duration_seconds": 24 },
    { "type": "video", "placeholder_id": "<clip2-id>", "duration_seconds": 24 },
    { "type": "video", "placeholder_id": "<clip3-id>", "duration_seconds": 24 }
  ],
  "video_audio_when_stacked": "mute",
  "background_audio_url": "<full-song-url>",
  "background_audio_placeholder_id": "<song-placeholder-id>",
  "aspect_ratio": "9:16",
  "resolution": "1080p",
  "name": "My music video"
}
```

- One `video` segment per clip, **in scene order**, each with its
  `placeholder_id` and its segment's `duration_seconds`.
- `video_audio_when_stacked: "mute"` — the clips' own audio (the segments) is
  muted; the **full original song** underneath supplies clean, continuous
  audio. Because the clips are contiguous and in order, sync is preserved.
- `background_audio_placeholder_id` matters: without it the render is fine but
  the user's in-app editor opens the project with an empty audio clip.
- No transitions between scenes by default — crossfades desync the mouth
  during the overlap. If the user insists, keep them ≤0.3s.

### 2. Render

Show the plan + estimated render time, get explicit approval, then call
`var2_join_videos` with **only `{plan_id}`** (the `jp_...` id). Poll
`var2_check_join_status` with the plain-UUID placeholder_id it returns —
renders take 10–30 minutes; check in occasionally, never loop. A worker
timeout may be re-queued once.

## Sanity checks before rendering

- Sum of segment `duration_seconds` == song duration used (or trimmed intro/
  outro accounted for).
- Clip order == segment order == chronological song order.
- Every segment has a `placeholder_id`.
- Aspect ratio matches what every portrait/clip was generated at.
