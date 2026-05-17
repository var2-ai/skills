# Pitfalls

> Supplementary reference. **`SKILL.md` is authoritative** — if anything here
> conflicts with it, follow `SKILL.md`.

Failure modes and the exact mitigations. The short list in `SKILL.md` covers
the must-knows; the full detail lives here.

## Backgrounds before 3D

Trellis-2 interprets every visible pixel as geometry. Run `remove-bg` even if
the source looks clean — leftover background fragments become garbage mesh.

## Local files can't be passed directly to VAR2

VAR2's backend fetches over HTTPS — local paths (`/mnt/user-data/uploads/...`,
`/home/claude/...`) fail. Upload to `tmpfile.link` first (see the tmpfile.link
section in `SKILL.md`), then pass the returned `downloadLink` as the URL.
This is the #1 reason a "use my photo" request blows up on the first VAR2
call.

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
  Picks any one panel as the starting frame and lets the rest be improvised.
- **Option B — One stitched video that traverses all panels**
  (reference-to-video). The video tries to hit each panel as a beat in
  sequence. Better for storyboards and multi-beat shorts, since the model is
  anchored to the compositions you actually designed. Pass all panels as
  references and describe each beat in the prompt.
- **Option C — Multiple short shots, one per panel, edited together later**
  (image-to-video × N). Each panel becomes its own short clip starting from
  that exact frame. Maximum fidelity per beat, but more tokens and the user
  has to stitch in an editor. Best when each panel deserves its own moment.

Frame the question for what they're actually trying to make. Don't pick on
their behalf. The default to lean toward when a storyboard exists is B
(reference-to-video) over A (image-to-video) — but always confirm before
spending video tokens, because the choice is irreversible once the job runs.

## Veo's `reference-to-video` is finicky

In practice, Veo's MCP signature for reference-to-video has rejected both
`reference_image_urls` and `reference_images` parameter names in real runs
(the error messages contradict each other). When you specifically need
reference-anchored video with Veo and the call fails twice, **fall back to
image-to-video** with the strongest single reference frame as
`first_frame_url` and describe the other references in the prompt text. For
true multi-reference video, `seedance-2` is more reliable (up to 9 image
refs).

## Character identity across generations

Don't describe the character textually each time — `image_refs` beats prose.
Generate one canonical character image, reuse its URL everywhere.

## Video duration types vary by model

- `kling*`, `grok-imagine` → STRING (`"5"`, `"10"`)
- `ltx-2.3`, `seedance-2` → NUMBER

Validation rejects the wrong type. When unsure, `var2_list_models` confirms.

## Aspect ratios vary by family

- `veo-3.1`, `sora-2` → `"portrait"` or `"landscape"`
- `kling*`, `grok-imagine` → `"1:1"`, `"16:9"`, `"9:16"`

## Upscale before videoing a generated image

For polish. Generated 1K often looks soft when moving. Topaz 2× takes ~5s and
is cheap.

## Don't poll-loop

`var2_get_*_result` long-polls server-side (50s for images, ~5min for
video/audio/3D). One call is usually enough. Only call again if it returns
`state: waiting`.

## Video prompts need motion and camera, not still-image prose

The #1 reason a video clip comes back nearly frozen is a prompt written like
an image prompt — "a woman standing in a kitchen, soft window light,
photoreal." That describes a still, not a shot. Always include camera
language ("slow dolly-in", "handheld follow", "static wide shot, character
walks across frame") and one motion beat per few seconds. For
`image-to-video`, the prompt should describe how the still *comes to life*,
consistent with `first_frame_url`.

## Idempotency on retries

Reuse `idempotency_key` when retrying a flaky generation so VAR2 doesn't
double-bill.

## Suno + Hebrew

Stick to English lyrics or instrumental. Suno can't pronounce Hebrew
reliably.
