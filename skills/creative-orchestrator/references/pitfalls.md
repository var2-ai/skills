# Pitfalls

> Supplementary reference. **`SKILL.md` is authoritative** — if anything here
> conflicts with it, follow `SKILL.md`.

Failure modes and the exact mitigations. The short list in `SKILL.md` covers
the must-knows; the full detail lives here.

## Backgrounds before 3D

Trellis-2 interprets every visible pixel as geometry. Run `remove-bg` even if
the source looks clean — leftover background fragments become garbage mesh.

## Local files can't be passed directly to VAR2

VAR2's backend fetches over HTTPS — a local path or chat attachment isn't
reachable. Upload it first with VAR2's own durable upload tools
(`var2_request_upload` for real/large files — signed PUT; `var2_upload_asset`
for small inline base64 or importing a third-party `url`) and pass the
returned `public_url` / `url` verbatim. Full decision table:
`references/media-inputs.md`. This is the #1 reason a "use my photo" request
blows up on the first VAR2 call. Never fabricate a URL to satisfy a tool
argument (no `example.com`, `local_file_url`, `path_to_*`, `attachment://*`,
`data:*`).

## image-to-video vs reference-to-video — and the question you MUST ask

These look interchangeable but produce fundamentally different videos:

- **`image-to-video`** — the image is the **literal first frame**. The model
  freely improvises everything after it. Good for: single-shot clips, one
  composition that moves, hero shots, ambient motion. Pass `first_frame_url`
  (one image).
- **`reference-to-video`** — the images are **target compositions / identity
  anchors** that the video should pass through or honor visually. Good for:
  multi-beat storyboards where the video should hit each panel in sequence,
  character/style consistency across a sequence, narrative shorts. Pass
  `reference_image_urls` (array of up to ~9 on seedance).

### Mandatory check before generating ANY video when references exist

If the user has produced or referenced more than one image — a storyboard, a
multi-panel sequence, a "scene A / scene B" plan, anything where the video is
implicitly supposed to traverse multiple compositions — DO NOT pick the mode
silently. Pause and ask explicitly which approach they want, with the
tradeoffs spelled out in their language:

- **Option A — One single shot, animated from one frame** (image-to-video).
  The video is one continuous moment built off that single first frame.
  Cheaper to reason about, but the model invents anything not in that frame.
- **Option B — One stitched video that traverses all panels**
  (reference-to-video). The video tries to hit each panel as a beat in
  sequence. Better for storyboards and multi-beat shorts, since the model is
  anchored to the compositions you actually designed.
- **Option C — Multiple short shots, one per panel, edited together later**
  (image-to-video × N). Maximum fidelity per beat, more tokens — and with
  `var2_join_videos` you can deliver the stitched cut yourself instead of
  sending the user to an editor.

Frame the question for what they're actually trying to make. Don't pick on
their behalf. The default to lean toward when a storyboard exists is B over A
— but always confirm before spending video tokens, because the choice is
irreversible once the job runs.

## Veo's reference params are model-specific

Veo 3.1 takes its reference images via **`reference_images`** (1–3 images) —
not `reference_image_urls` like seedance/happyhorse. If a Veo
reference-to-video call rejects the param twice, fall back to image-to-video
with the strongest single reference frame as `first_frame_url` and describe
the other references in the prompt text. For true multi-reference video,
`seedance-2` is the reliable pick (up to 9 image refs).

## Character identity across generations

Don't describe the character textually each time — `image_refs` beats prose.
Generate one canonical character image, reuse its URL everywhere. To persist a
character across sessions, `var2_save_character` stores the sheet by name and
`var2_get_character` fetches it back — fetch first, never regenerate a saved
character from a prompt.

## Video duration types vary by model

- `kling` (2.6), `grok-imagine` → STRING (`"5"`/`"10"`, `"6"`/`"10"`)
- `ltx-2.3`, `seedance-2`, `grok-imagine-video-1-5`, `kling-3` → NUMBER
  (seconds)

Validation rejects the wrong type. When unsure, `var2_list_models` confirms.

## Aspect ratios vary by family

- `veo-3.1`, `sora-2` → `"portrait"` or `"landscape"`
- `kling*`, `grok-imagine` → `"1:1"`, `"16:9"`, `"9:16"`

## Upscale before videoing a generated image

Generated 1K often looks soft when moving. Topaz 2x takes ~5s and is cheap —
run it before the image becomes a `first_frame_url` for a final render.

## Don't poll-loop

`var2_get_*_result` long-polls server-side (50s for images, ~5min for
video/audio/3D). One call is usually enough. Only call again if it returns
`state: waiting`, and pass `inline_media: false` on repeat checks.

## Idempotency on retries

Reuse `idempotency_key` when retrying a flaky generation so VAR2 doesn't
double-bill.

## Suno + Hebrew

Stick to English lyrics or instrumental by default. If the user insists on
Hebrew, use custom mode with full niqqud — see `references/non-latin-text.md`.
