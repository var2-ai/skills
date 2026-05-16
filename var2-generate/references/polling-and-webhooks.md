# Polling & Webhooks

VAR2 generation is asynchronous. A `create_*` / `var2_modify_image` call
returns quickly with a `placeholder_id` and `state: "waiting"`; the asset is
produced in the background.

## Polling (default)

After a create/modify call, call the matching getter with the
`placeholder_id`:

| Create tool | Poll with |
|---|---|
| `var2_create_image`, `var2_modify_image` | `var2_get_image_result` |
| `var2_create_video` | `var2_get_video_result` |
| `var2_create_audio` | `var2_get_audio_result` |
| `var2_create_3d` | `var2_get_3d_result` |

Behavior:

- The getter **long-polls server-side** — a single call blocks for a while and
  returns as soon as the job finishes or the wait window elapses.
- If it returns still `waiting`, just call the getter again with the same
  `placeholder_id`. Image jobs usually resolve in one or two polls; video,
  music, and 3D take longer (several polls).
- Stop when `state` is `completed` (report share URL[s]) or `failed` (read the
  error, see `troubleshooting.md`).
- `var2_get_image_result` and `var2_get_audio_result` accept `inline_media`
  (default true) so the host can preview the result inline. Leave it default.

Do not sleep-loop or spin: each getter call already waits efficiently. Just
re-call when it says waiting.

## Result payload

A completed result includes one or more **`var2.ai` share URLs** plus the
direct asset reference. Always surface the share URL(s) to the user verbatim —
that page handles preview, download, and sharing. Some models return multiple
outputs (`grok-imagine` images, `suno`'s two tracks) — report **all** share
URLs.

## Webhooks (optional, advanced)

Every `create_*` / `var2_modify_image` tool accepts an optional `webhook_url`.
When provided, VAR2 POSTs the final result to that URL when the job completes,
so a backend can receive results without polling.

- The request is **signed**: an `X-VAR2-Signature` header lets the receiver
  verify authenticity. The receiving service must validate it before trusting
  the payload.
- Webhooks are for server integrations. In a normal interactive agent session,
  **prefer polling** — you can't receive an inbound webhook mid-conversation.
- Only set `webhook_url` if the user explicitly asks for callback delivery to
  their own endpoint.
