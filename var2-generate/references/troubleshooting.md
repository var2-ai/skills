# Troubleshooting

Work through the symptom; fix the input; retry once (still one create per
turn). Never invent a model ID — call `var2_list_models` when unsure.

## Auth / connection

| Symptom | Cause | Fix |
|---|---|---|
| `401`, `WWW-Authenticate` / sign-in challenge | OAuth sign-in not completed | Reconnect VAR2 and finish the browser sign-in (`INSTALL_FOR_AGENTS.md` Step 1). |
| `expired`, `revoked` | Session/grant ended | Reconnect and sign in again. (Headless key users: recreate the `vak_` key at https://www.var2.ai/dashboard/settings?tab=developers.) |
| Connection/transport error, tool not found | MCP server not connected in this agent | Follow `INSTALL_FOR_AGENTS.md`; confirm the server URL is `https://www.var2.ai/api/mcp`. |
| `403` / scope error | Grant missing required access | Reconnect and approve all requested access on the consent screen. |
| `429` / rate or concurrency limit | Too many concurrent jobs | Wait for the in-flight job to finish, then retry. |

## Job submission

| Symptom | Cause | Fix |
|---|---|---|
| `unknown model "..."` | Bad/guessed model ID | Call `var2_list_models`; use an exact ID. |
| Validation error on a param | Param not supported by that model | Check the model's capabilities in `var2_list_models`; drop or correct the param. |
| Media role error | Wrong `type` for the media passed | Match `type` to the media (see `media-inputs.md`): e.g. `source_video_url` requires `video-to-video`. |
| "more than one create" / budget error | Two create calls in one turn | Submit one job per turn; wait for the result before the next. |
| Insufficient tokens / spend cap | Out of balance or cap hit | Report the cost; point user to the dashboard/billing. Don't retry in a loop. |

## Results

| Symptom | Cause | Fix |
|---|---|---|
| Stuck `waiting` after several polls | Slow modality (video/3D/music) | Keep polling; the getter long-polls — re-call. If it never resolves, report it and let the user retry later. |
| `state: failed` | Provider error or bad input | Read the error message, adjust prompt/params/model, retry once. |
| Garbled Hebrew/Arabic text in image | Wrong model | Regenerate with `nano-banana-pro` (or `nano-banana-2`). See `non-latin-text.md`. |
| Frozen / barely-moving video | Image-style prompt on a video model | Rewrite with camera + motion language (`prompt-engineering.md`). |
| Poor 3D mesh | Cluttered source image | `remove-bg` the source first, then `var2_create_3d` (next turn). |
| Wrong language in reply | Ignored user's language | Reply in the user's language; keep model IDs/params English. |

## When to ask the user vs. decide

- **Decide:** model, aspect ratio, resolution, duration, style — infer from
  intent.
- **Ask (one question max):** only a genuine fork that changes the deliverable
  (portrait vs landscape hero, vocal vs instrumental, which of two source
  images to animate).

## Escalation

If a tool consistently errors in a way none of the above explains, report the
exact error message to the user and point them to
https://www.var2.ai/dashboard/settings?tab=developers — do not keep retrying.
