# Prompt Engineering

How to turn a user brief into a strong prompt per modality. The user's request
is intent; your job is to expand it into a concrete, specific prompt without
inventing creative direction they didn't ask for.

## General principles

- **Be concrete.** Subject, setting, lighting, mood, framing, style. Vague
  prompts get generic output.
- **Front-load the subject.** Most important content first.
- **Don't over-stuff.** 1–3 tight sentences beat a wall of adjectives. Models
  dilute attention across very long prompts.
- **Preserve the user's words.** If they said "moody", keep "moody" — don't
  silently replace their intent with your own taste.
- **One creative direction.** Don't hedge with "or maybe..." inside a prompt.

## Image

- Specify: subject, composition/framing, lighting, color/mood, style/medium,
  and aspect ratio (set via the `aspect_ratio` param, not the prompt text).
- For text **on** the image, quote it exactly: `the words "OPEN 24/7" in bold`.
  For Hebrew/Arabic, see `non-latin-text.md` and prefer `nano-banana-pro` /
  `nano-banana-2`.
- For edits (`image-to-image`), describe the **change**, not the whole scene:
  "replace the sky with a sunset, keep everything else" works better than
  re-describing the source.
- Reference images (`image_refs`) carry style/identity — say what to take from
  them ("match the character in ref 1, the palette in ref 2").

## Video

- Describe **motion and camera**, not just a still: "slow dolly-in", "handheld
  follow", "static wide shot". A video prompt that reads like an image prompt
  produces a near-frozen clip.
- One action beat per few seconds. For multi-shot models (`kling-3`), give a
  shot list — one prompt per shot.
- For image-to-video, the prompt should describe how the still should *come to
  life*, consistent with the `first_frame_url`.
- State pacing/energy ("calm", "fast-cut") and any audio intent for
  audio-capable models (`ltx-2.3`, `happyhorse`).

## Music (Suno)

- `prompt` = the song idea / lyrics theme; `style` (≤200 chars) = genre, mood,
  instrumentation, tempo (e.g. "lofi hip-hop, mellow, vinyl crackle, 75 bpm").
- `instrumental: true` when there should be no vocals.
- Keep `title` short. Suno is English-strong — for other languages see
  `non-latin-text.md`.

## 3D

- The `image` input drives the mesh; there is no text prompt. Pick a clean,
  well-lit, single-object source image with a plain background for the best
  mesh. Suggest `remove-bg` first if the source is cluttered.

## Negative space

VAR2 models take a single positive prompt. If the user wants to *avoid*
something, phrase it positively ("a clear blue sky" rather than "no clouds")
or, for edits, describe the desired end state.
