# More Worked Examples

> Supplementary reference. **`SKILL.md` is authoritative** — these examples
> calibrate taste; they are not templates. Two more live inline in `SKILL.md`
> (the 3D cat and the 30-second cinematic).

---

## Example — "Make me a commercial for my new coffee"

**Naive read:** one video clip of coffee being poured. Done.

**Better read:** a real commercial has *beats* — a problem, a hero moment, a
payoff — held together by a consistent visual identity. VAR2 can do that with
reference-to-video.

```
Here's how I'd build the coffee commercial — with a twist:

**The twist:** I'll generate one "key art" image first that defines the visual language (lighting, mood, color), then use it as a reference anchor across every shot so the whole commercial feels like one piece, not three separate AI clips. This is what real ad agencies do — we just do it in 5 minutes.

**Step 1 — Key art / mood frame** (~10s)
Single hero shot that defines the whole spot: warm morning light, your coffee cup, soft shadows, premium feel. This becomes the visual anchor.
Model: flux-2 (photorealistic), 2K, 16:9

**Step 2 — Storyboard panel A: the "before"** (~10s)
Tired person at desk, cold blue light. Same lighting *family* as key art via image_refs.
Model: gpt-image-2 with image_refs=[key art], 16:9

**Step 3 — Storyboard panel B: the "hero moment"** (~10s)
Hands wrapping around the coffee, steam rising. Image_refs again.
Model: gpt-image-2 with image_refs=[key art], 16:9

**Step 4 — Storyboard panel C: the "payoff"** (~10s)
Same person, transformed, looking out a window. Image_refs again.
Model: gpt-image-2 with image_refs=[key art], 16:9

**Step 5 — Cinematic shot from panels B+C** (~90s)
Reference-to-video using panels B and C as anchors — the AI fills the motion between them, keeping the look locked.
Model: seedance-2 reference-to-video, 8s, pro

**Step 6 — Background score** (~60s)
Suno track in the right mood (warm, hopeful, instrumental).
Model: suno V5_5, instrumental

Rough cost: ~4,000 tokens (4 images + 1 cinematic video + 1 music track). I'll run estimate_cost for the exact number.

Ready for Step 1?
```

---

## Example — "Make me a cartoon character, put them in a comic, now turn it into a realistic cinematic video"

**Naive read:** three disconnected generations.

**Better read:** the *same character* across three visual languages. The whole
point is identity persistence. `image_refs` is the secret weapon.

```
Here's the flow — and the trick that makes it actually work:

**The trick:** every step uses the cartoon character image as `image_refs`, so the same face/outfit/proportions carry from comic to live-action. Without this, you'd get three unrelated people.

**Step 1 — Design the character** (~10s)
Full body, T-pose-ish, plain background, distinct design choices (hair, outfit, vibe) so the AI can lock identity.
Model: nano-banana-2, 2K, 1:1, illustrative cartoon style

**Step 2 — Comic page (3-panel)** (~15s)
Single image laid out as 3 panels: same character in three story beats. Pass the Step 1 image as image_refs to keep them on-model.
Model: gpt-image-2 with image_refs=[step1], 2K, 4:5 (vertical comic format) — gpt-image-2 is great at multi-panel layouts because of strong prompt adherence

**Step 3 — Realistic cinematic still** (~12s)
A photoreal version of the character — same outfit, same face structure, but skin/lighting/film grain. This becomes the first frame of the video.
Model: nano-banana-2 with image_refs=[step1] (and optionally step2), prompt steers it to "cinematic photograph, 35mm, shallow DoF"

**Step 4 — Live-action cinematic clip** (~120s)
Image-to-video from Step 3 — cinematic camera move, the character is alive.
Model: seedance-2 (image-to-video), first_frame_url=[step3], 8s, pro mode

Rough cost: ~3,500 tokens (3 images + 1 cinematic video). I'll run estimate_cost for the exact number.

Ready for Step 1?
```

---

## Example — "Make me a music video"

**Naive read:** one video, song over it.

**Better read:** music videos have *sections*. Intro, verse, hook. Visuals
shift on the beat. Generate the music first, then design visuals tied to its
structure. (For the full lip-synced singer pipeline, the dedicated
`ai-music-video-maker` skill goes deeper.)

```
Music video plan — with the twist that makes it feel pro:

**The twist:** I'll generate the song first, then design visuals tied to its three sections (intro / drop / outro). Each section gets its own frame, we animate them, and I stitch the final cut for you.

**Step 1 — Generate the track** (~120s)
Suno returns 2 variations — you pick.
Model: suno V5_5, prompt describes mood/genre/tempo, instrumental or English lyrics (Suno is shaky on Hebrew)

**Step 2 — Define the visual identity** (~10s)
One key frame, e.g., the protagonist or the central object. Becomes anchor for all sections.
Model: flux-2 for photoreal Latin-only, or nano-banana-2 / gpt-image-2 if non-Latin text is in the frame

**Step 3 — Section frames (intro / hook / outro)** (~30s, three quick generations — can run in parallel)
Three frames, each with image_refs=[step2] for visual unity.
Model: nano-banana-2 with image_refs (or gpt-image-2 for more complex layouts)

**Step 4 — Animate each section** (~120s each)
Image-to-video on each frame; pick durations that match the song's section lengths.
Model: ltx-2.3 (per-second pricing, ideal for matching exact beats) or seedance-2

**Step 5 — Stitch the final cut** (~15min render)
var2_join_videos: the three clips in order, muted, with the full track as background audio — one finished mp4, no external editor needed. (dry_run plan → your approval → render.)

Rough cost: depends heavily on clip lengths since ltx-2.3 is per-second. I'll run estimate_cost once we lock the durations.

Ready for Step 1?
```

---

## Example — "Multiverse versions of myself, from a selfie"

**Naive read:** image-to-image six times. Done.

**Better read:** the *fun* is the reveal moment — show them all at once, plus
a video that morphs through them. Use reference-to-video to anchor identity.

```
Multiverse you — with the twist:

**The twist:** after the six variations, I'll generate one reference-to-video that morphs through them as if traveling between universes. Six images alone is fine; six images + a 6-second morph reel is shareable.

**Step 1 — Clean up the source selfie** (~5s)
Upscale to 2K so face details survive subsequent generations.
Model: topaz-upscale
(If the selfie is a local/attached file: upload it first — see references/media-inputs.md.)

**Steps 2-7 — Generate six universe variants** (can run in parallel — multi-output is allowed for variations)
Each generation uses the upscaled selfie as image_refs to preserve face. Prompts vary the universe: cyberpunk neon, fantasy ranger, astronaut, 1940s noir detective, post-apocalyptic survivor, renaissance painting.
Model: nano-banana-2, image_refs=[upscaled selfie], 2K

**Step 8 — Multiverse morph reel** (~120s)
Reference-to-video with all 6 universe images as `reference_image_urls`. The video shifts identity between universes while holding the face.
Model: seedance-2 reference-to-video, 10s, pro mode

Rough cost: ~5,500 tokens (upscale + 6 images + 1 cinematic video). I'll run estimate_cost for the exact number.

Heads up — six images at once is a chunky parallel batch. Cool with that, or want me to trim it to 3-4 universes?
```

---

## Example — "Turn an old photo of mine into a motion comic"

**Naive read:** one image-to-video.

**Better read:** *motion comics* have a distinct grammar — Ken Burns pans
across stylized panels, sometimes with subtle in-panel motion (eyes blinking,
hair moving). Treat each panel of a comic adaptation as its own micro-shot.

```
Motion comic — the trick:

**The trick:** I'll *re-style* your photo into a comic illustration first (so it looks like a panel, not a filtered photo), then animate it with the subtle Ken Burns + idle-motion that motion comics use. The combination is what sells it.

**Step 0 — Get the photo into VAR2** (~5s)
Your photo is a local file — I'll upload it to VAR2 storage first and use the returned URL.
Tool: var2_request_upload (or var2_upload_asset for small files)

**Step 1 — Stylize the photo into a comic panel** (~10s)
Image-to-image on your photo, prompt steers it to "ink-and-color comic page, halftone shadows, bold linework, dramatic angles."
Model: nano-banana-2 image-to-image, 2K

**Step 2 — Upscale the stylized panel** (~5s)
Comics need crisp lines — soft generated images animate poorly.
Model: topaz-upscale

**Step 3 — Animate with motion-comic grammar** (~90s)
Image-to-video, prompt for "slow cinematic push-in, hair gently moves, subtle eye blink, paper texture stays still." The trick is asking for *micro* motion, not full animation.
Model: ltx-2.3 (image-to-video), 4-5s — short clips feel more comic-like than long ones

Rough cost: ~1,200 tokens (image-to-image + upscale + short video). I'll run estimate_cost for the exact number.

Want me to extend this to multiple panels (one photo per panel) and stitch into a longer motion comic with var2_join_videos? That's a bigger pipeline if you're up for it.
```

---

## What every example has in common

- **A "twist" line** at the top — the non-obvious creative move that elevates
  the request
- **An anchor strategy** — usually `image_refs` to keep identity/style locked
  across generations
- **A medium-crossing move** — almost every flow ends in a different medium
  than where it started (image → video, 3D → video, photo → motion comic)
- **A cost / turn count check-in** when the pipeline gets ambitious
- **Concrete model picks** with reasoning, not vague "let's generate
  something"
- **For multi-shot videos: a storyboard pass before any video generation** —
  character sheets → storyboard frames → videos. Cheap stills as a safety net
  before expensive video tokens.

The next request you get will not match these. Don't try to map it onto
Example N. Instead ask: *given this specific brief, what's the non-obvious
move? What's the anchor? What media should we cross? If it's multi-shot, where
are my approval gates?* Then invent.
