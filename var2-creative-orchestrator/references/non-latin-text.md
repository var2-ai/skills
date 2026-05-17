# Non-Latin Text (Hebrew / Arabic)

> Supplementary reference. **`SKILL.md` is authoritative** — if anything here
> conflicts with it, follow `SKILL.md`.

VAR2 is built with strong Hebrew/Arabic support, but **model choice decides
whether on-image text renders correctly**. This is the single most common
cause of disappointing output for RTL-language users.

## On-image text in images

Render reliable Hebrew/Arabic text with:

1. **`gpt-image-2`** — first choice. Strong prompt adherence with reliable
   Hebrew/Arabic glyph rendering; up to 15 reference images for character
   continuity.
2. **`nano-banana-2`** — when you need 4K or factual grounding alongside the
   non-Latin text.
3. **`nano-banana-pro`** — backup only. Use it if `gpt-image-2` and
   `nano-banana-2` have specifically misfired on a given prompt.

Avoid for Hebrew/Arabic captions: `flux-2`, `flux-flex`, `z-image` — they
mangle non-Latin glyphs.

Tips:
- Quote the exact string in the prompt: `the Hebrew text "פתוח 24 שעות"`.
- Keep on-image copy short; long RTL strings degrade fastest.
- If text comes out garbled, regenerate with a different model from the list
  above before tweaking the prompt — it's almost always a model-choice
  problem, not a prompt problem.

## Prompts written in Hebrew/Arabic

You can write the descriptive prompt itself in Hebrew/Arabic for
`gpt-image-2`, `nano-banana-2`, `nano-banana-pro`, and for `veo-3.1` /
`ltx-2.3` video. If results are weak, keep the *quoted on-image text* in the
target language but write the surrounding scene description in English — the
visible glyphs are what matter.

## Video

`veo-3.1` and `ltx-2.3` handle non-Latin prompts and on-screen text best.
`seedance-2` produces the strongest motion and composition but is weaker on
non-Latin text in the frame — for cinematic shots that don't need legible
Hebrew/Arabic text inside the video, prefer `seedance-2`; for shots that
require on-screen RTL text, prefer `veo-3.1` or `ltx-2.3`. On-screen text in
video is less reliable than in images across all models — set expectations and
keep any required on-screen text minimal.

## Music (Suno)

Suno is **English-strong**; Hebrew/Arabic lyrics are unreliable and often
phonetically wrong. Options, in order:
1. Instrumental (`instrumental: true`) — sidesteps the problem entirely.
2. English lyrics with the requested mood/style.
3. If the user insists on Hebrew/Arabic lyrics, set the expectation that
   pronunciation may be off before generating.

## Replying to the user

If the user wrote in Hebrew or Arabic, reply in that language (model IDs and
parameters stay English). Share URLs are printed as-is.
