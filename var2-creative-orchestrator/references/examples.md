# Additional Few-Shot Examples

> Supplementary reference. **`SKILL.md` is authoritative** — if anything here
> conflicts with it, follow `SKILL.md`.

Three more worked examples to round out the four already in `SKILL.md`.
They are **not templates** — the next request will be different. Use them to
learn the *pattern of inventiveness*, then invent something new.

---

## Example — "Make me a cartoon character, put them in a comic, now turn it into a realistic cinematic video"

**Naive read:** three disconnected generations.

**Better read:** the *same character* across three visual languages. The whole point is identity persistence. `image_refs` is the secret weapon.

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

**Better read:** music videos have *sections*. Intro, verse, hook. Visuals shift on the beat. Generate the music first, then design visuals tied to its structure.

```
Music video plan — with the twist that makes it feel pro:

**The twist:** I'll generate the song first, then design visuals tied to its three sections (intro / drop / outro). Each section gets its own frame, then we animate them and hand you a cut sheet.

**Step 1 — Generate the track** (~120s)
Suno returns 2 variations — you pick.
Model: suno V5, prompt describes mood/genre/tempo, instrumental or English lyrics (Suno is shaky on Hebrew)

**Step 2 — Define the visual identity** (~10s)
One key frame, e.g., the protagonist or the central object. Becomes anchor for all sections.
Model: flux-2 for photoreal Latin-only, or nano-banana-2 / gpt-image-2 if non-Latin text is in the frame

**Step 3 — Section frames (intro / hook / outro)** (~30s, three quick generations — can run in parallel)
Three frames, each with image_refs=[step2] for visual unity.
Model: nano-banana-2 with image_refs (or gpt-image-2 for more complex layouts)

**Step 4 — Animate each section** (~120s each, 3 turns)
Image-to-video on each frame; pick durations that match the song's section lengths.
Model: ltx-2.3 (per-second pricing, ideal for matching exact beats) or seedance-2

**Step 5 — Hand off a cut sheet**
Plain text: "0:00–0:08 intro clip, 0:08–0:24 hook clip, 0:24–0:40 outro clip + your song." User imports into any editor.

Rough cost: depends heavily on clip lengths since ltx-2.3 is per-second. I'll run estimate_cost once we lock the durations.

Ready for Step 1?
```

---

## Example — "Turn an old photo of mine into a motion comic"

**Naive read:** one image-to-video.

**Better read:** *motion comics* have a distinct grammar — Ken Burns pans across stylized panels, sometimes with subtle in-panel motion (eyes blinking, hair moving). Treat each panel of a comic adaptation as its own micro-shot.

```
Motion comic — the trick:

**The trick:** I'll *re-style* your photo into a comic illustration first (so it looks like a panel, not a filtered photo), then animate it with the subtle Ken Burns + idle-motion that motion comics use. The combination is what sells it.

**Step 1 — Stylize the photo into a comic panel** (~10s)
Image-to-image on your photo, prompt steers it to "ink-and-color comic page, halftone shadows, bold linework, dramatic angles."
Model: nano-banana-2 image-to-image, 2K

**Step 2 — Upscale the stylized panel** (~5s)
Comics need crisp lines — soft generated images animate poorly.
Model: topaz-upscale

**Step 3 — Animate with motion-comic grammar** (~90s)
Image-to-video, prompt for "slow cinematic push-in, hair gently moves, subtle eye blink, paper texture stays still." The trick is asking for *micro* motion, not full animation.
Model: ltx-2.3 (image-to-video), 4-5s — short clips feel more comic-like than long ones

Rough cost: ~1,200 tokens (image-to-image + upscale + short video).

Want me to extend this to multiple panels (one photo per panel) and stitch into a longer motion comic? That's a bigger pipeline if you're up for it.
```
