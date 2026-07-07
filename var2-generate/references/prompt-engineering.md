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
  them ("match the character in ref 1, the palette in ref 2"). For repeated
  characters see `characters.md`.

## Video

- Describe **motion and camera**, not just a still: "slow dolly-in", "handheld
  follow", "static wide shot". A video prompt that reads like an image prompt
  produces a near-frozen clip.
- One action beat per few seconds. For multi-shot models (`kling-3`
  `shots[]`), give a shot list — one prompt per shot.
- For image-to-video, the prompt should describe how the still should *come to
  life*, consistent with the `first_frame_url`. When chaining segments
  (segment B starts from segment A's last frame), prompt B to **continue** the
  motion, not restart it ("the camera continues to pull back").
- State pacing/energy ("calm", "fast-cut").
- **Native audio** (`seedance-2`, `ltx-2.3`, `veo-3.1`, `kling-3` with
  `sound`): describe the soundtrack in the prompt — speaker voice ("deep male
  narrator"), exact dialogue/VO lines, SFX, ambience. English VO is strongest;
  for Hebrew/Arabic narration prefer `veo-3.1`/`ltx-2.3` or generate the audio
  separately with `var2_create_dialog`.
- **Talking head (`pruna-avatar`)**: describe the performance and scene; to
  keep the mouth locked to the right track, append *"Lip-sync ONLY to the lead
  voice; ignore background vocals, crowd noise, and instruments."* Keep the
  portrait front-facing with the mouth unobstructed — vary location, lighting,
  and framing distance rather than extreme angles.

## Music (Suno)

- Default mode: `prompt` = the song idea / lyrics theme (≤500 chars); `style`
  and `title` optional.
- Exact lyrics: `customMode: true`, `prompt` = the full lyrics (no 500-char
  cap), `style` (≤200 chars: genre, mood, instrumentation, tempo — e.g. "lofi
  hip-hop, mellow, vinyl crackle, 75 bpm") + `title` required. Structure tags
  (`[Verse 1]`, `[Chorus]`, `[Bridge]`) help.
- `instrumental: true` when there should be no vocals.
- **Never name real artists or songs** ("in the style of X") — the copyright
  filter rejects the job. Describe the sound instead.
- Suno is English-strong — for other languages see `non-latin-text.md`.

## Speech / dialog (TTS)

- Write text the way it should be **spoken**: punctuation drives delivery
  (commas pause, em-dashes hesitate). Spell out numbers and abbreviations.
- Split conversations into `dialogue` turns per speaker rather than stage
  directions in one blob. Details: `dialog-and-voices.md`.

## 3D

- The `image` input drives the mesh; there is no text prompt. Pick a clean,
  well-lit, single-object source image with a plain background for the best
  mesh. Suggest `remove-bg` first if the source is cluttered.

## Negative space

Most VAR2 models take a single positive prompt. If the user wants to *avoid*
something, phrase it positively ("a clear blue sky" rather than "no clouds")
or, for edits, describe the desired end state. Exception: `kling`, `kling-3`,
and `wan-2.7` accept a real `negative_prompt` — use it there.
