# Troubleshooting

Work through the symptom; fix the input; retry once (reuse the same
`idempotency_key` so retries never double-bill). Never invent a model ID —
call `var2_list_models` when unsure. When you can't fix it, surface VAR2's
error message to the user **verbatim** — it's precise.

## Auth / connection

| Symptom | Cause | Fix |
|---|---|---|
| `401`, `WWW-Authenticate` / sign-in challenge | OAuth sign-in not completed | Reconnect VAR2 and finish the browser sign-in (`INSTALL_FOR_AGENTS.md` Step 1). |
| `expired`, `revoked` | Session/grant ended | Reconnect and sign in again. (Headless key users: recreate the `vak_` key at https://www.var2.ai/dashboard/settings?tab=developers.) |
| Connection/transport error, tool not found | MCP server not connected in this agent | Follow `INSTALL_FOR_AGENTS.md`; confirm the server URL is `https://www.var2.ai/api/mcp`. |
| `403` / scope error | Grant missing required access | Reconnect and approve all requested access on the consent screen. |
| `429` / rate or concurrency limit | Too many concurrent jobs | Wait for in-flight jobs to finish, then retry. |
| Bare `Denied.` on a create call | Account / quota / rate limit, not a bad request | Stop, surface it verbatim to the user; don't hammer retries. |

## Job submission

| Symptom | Cause | Fix |
|---|---|---|
| `unknown model "..."` | Bad/guessed model ID | Call `var2_list_models`; use an exact ID. |
| Validation error on a param | Param not supported by that model | Check the model in `var2_list_models` / `media-inputs.md`; drop or correct the param (classic: string vs. number `duration`; `reference_images` vs. `reference_image_urls` on veo). |
| Media role error | Wrong `type` for the media passed | Match `type` to the input (see `media-inputs.md`): a video URL means `video-to-video`; portrait+audio means `audio-to-video`. |
| Upload-first error / "cannot fetch" a path-like value | A local path or attachment handle was passed as a URL | Upload the bytes first (`var2_request_upload` / `var2_upload_asset`), then pass the returned URL. See `media-inputs.md`. |
| PUT to `upload_url` blocked (`host_not_allowed`, egress) | Sandboxed network | ≤1 MB → `var2_upload_asset` base64 (+`expected_bytes`, chunked if needed); else give the user the `user_upload_page` link, then `var2_confirm_upload`. |
| Upload rejected: type/size mismatch | Bytes don't match declared `type`, or base64 truncated | Check the file really is image/video/audio; always pass `expected_bytes` with base64 `data`. |
| Call-budget error ("more than N create calls") | Too many creates in one turn | Respect the budget stated in the tool response; batch across turns. |
| Insufficient tokens / spend cap | Out of balance or cap hit | Report the cost; point user to the dashboard/billing. Don't retry in a loop. |
| Suno rejects the prompt | Real artist/song named, or >500 chars without custom mode | Remove artist references; for full lyrics use `customMode: true` + `style` + `title`. |

## Results

| Symptom | Cause | Fix |
|---|---|---|
| Stuck `waiting` after several polls | Slow modality (video/3D/music/join) | Keep polling; the getter long-polls — re-call (`inline_media: false` on repeats). If it never resolves, report it and let the user retry later. |
| `state: failed` | Provider error or bad input | Read the error message, adjust prompt/params/model, retry once. |
| Join render fails with worker timeout | Long render queue | Re-queue once via `var2_join_videos` `{plan_id}`; if it fails again, report. |
| `var2_check_join_status` rejects the id | A `jp_...` plan id was passed | Plans go to `var2_join_videos` `{plan_id}` to START the render; only the plain-UUID placeholder goes to the status tool. |
| Garbled Hebrew/Arabic text in image | Wrong model | Regenerate with `nano-banana-pro` (or `nano-banana-2`). See `non-latin-text.md`. |
| Frozen / barely-moving video | Image-style prompt on a video model | Rewrite with camera + motion language (`prompt-engineering.md`). |
| Talking head won't lip-sync | Mouth obstructed / off-angle portrait, or busy audio | Use a front-facing portrait with the mouth visible; tell the model to sync only to the lead voice. |
| Poor 3D mesh | Cluttered source image | `remove-bg` the source first, then `var2_create_3d`. |
| Character drifts across shots | Prose-only descriptions | Use refs, not text: `image_refs` / `reference_image_urls` / `kling_elements`; storyboard-first for multi-shot (`characters.md`). |
| Editor opens with empty clips after a join | Segments passed by URL only | Re-save with `placeholder_id` on each var2 segment (+ `background_audio_placeholder_id`). The rendered mp4 itself is fine. |
| Wrong language in reply | Ignored user's language | Reply in the user's language; keep model IDs/params English. |

## When to ask the user vs. decide

- **Decide:** model, style, duration for a single asset — infer from intent.
- **Ask:** `var2_join_videos` aspect ratio, resolution, and segment order
  (required by contract); traversal mode when multiple storyboard frames
  exist (one shot vs. beats vs. clip-per-frame); any genuine fork that changes
  the deliverable (portrait vs. landscape hero, vocal vs. instrumental).

## Escalation

If a tool consistently errors in a way none of the above explains, report the
exact error message to the user and point them to
https://www.var2.ai/dashboard/settings?tab=developers — do not keep retrying.
