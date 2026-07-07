# Polling & Webhooks

VAR2 generation is asynchronous. A `create_*` / `var2_modify_image` /
`var2_join_videos` (render) call returns quickly with a `placeholder_id` and
`state: "waiting"`; the asset is produced in the background.

## Polling (default)

After a create/modify/render call, call the matching getter with the
`placeholder_id`. **Pick the getter by media, not by guesswork** — one always
matches:

| Create tool | Poll with |
|---|---|
| `var2_create_image`, `var2_modify_image` | `var2_get_image_result` |
| `var2_create_video` | `var2_get_video_result` |
| `var2_create_audio` (music) | `var2_get_audio_result` |
| `var2_create_dialog` (voice-over/TTS) | `var2_get_dialog_result` |
| `var2_create_3d` | `var2_get_3d_result` |
| `var2_join_videos` / `var2_render_timeline` (render) | `var2_check_join_status` |

Behavior:

- The getter **long-polls server-side** — a single call blocks for a while and
  returns as soon as the job finishes or the wait window elapses.
- If it returns still `waiting`, just call the getter again with the same
  `placeholder_id`. Image jobs usually resolve in one or two polls; video,
  music, and 3D take longer (several polls); join/stitch renders are the
  slowest (minutes to hours — check in occasionally rather than continuously).
- Stop when `state` is `completed` (report share URL[s]) or `failed` (read the
  error, see `troubleshooting.md`).
- `var2_get_image_result`, `var2_get_audio_result`, and
  `var2_get_dialog_result` accept `inline_media` (default true) so the host
  can preview the result inline. **Pass `inline_media: false` on repeat
  status checks and when you only need the URL for chaining** — never render
  the same media into context twice.
- Do not sleep-loop or spin: each getter call already waits efficiently. Just
  re-call when it says waiting.

Join-status gotcha: a `jp_...` id is a **plan** — it goes back to
`var2_join_videos` (`{plan_id}`) to start the render. Only the plain-UUID
placeholder_id of a queued render goes to `var2_check_join_status`.

## Result payload

A completed result includes one or more **`var2.ai` share URLs** plus the
direct asset `url` (use the `url` for chaining into the next tool, the share
URL for the user). Always surface the share URL(s) to the user verbatim — that
page handles preview, download, and sharing. Some models return multiple
outputs (`grok-imagine` images, `suno`'s two tracks) — report **all** share
URLs.

## Webhooks (optional, advanced)

Every `create_*` / `var2_modify_image` tool accepts an optional `webhook_url`.
When provided, VAR2 POSTs the final result to that URL when the job completes,
so a backend can receive results without polling.

- The request is **signed**: `X-VAR2-Signature: t=<unix>,
  v1=<hex(hmac_sha256(webhook_secret, t + "." + body))>`. The receiving
  service must validate the signature before trusting the payload.
- Delivery is retried with exponential backoff (8 attempts over ~4 days).
- Webhooks are for server integrations. In a normal interactive agent session,
  **prefer polling** — you can't receive an inbound webhook mid-conversation.
- Only set `webhook_url` if the user explicitly asks for callback delivery to
  their own endpoint.
