# Dialog & Voices (TTS)

Spoken audio — narration, voice-over, multi-speaker dialog, character voices —
runs through `var2_create_dialog` (ElevenLabs v3). Music is a different tool
(`var2_create_audio`); if the user wants singing over instrumentation, that's
Suno, not TTS.

## Browsing voices — `var2_get_voice_list`

Any "what voices do you have / find me a [deep male] voice / which voice for
Hebrew" request is a **catalog query** — answer it with this tool, never with
a generation and never with a guess.

- `source: "account"` (default) — the curated set (~10–50 voices). Start here.
- `source: "library"` — the full public ElevenLabs library (10K+). Filter with
  `search`, `gender`, `age`, `accent`, `descriptives` ("calm,warm,deep"),
  `use_cases` ("narration,characters_animation"), `featured`; paginate via
  `page_size` + the response's `last_sort_id`.
- `language` (ISO 639-1, e.g. `"he"`) filters to voices **verified** for that
  language — use it whenever the text isn't English.
- `category`: premade | cloned | generated | professional.

Present a short shortlist (name, gender/age/accent, one-line character), let
the user pick, then generate.

## Generating speech — `var2_create_dialog`

```json
{
  "dialogue": [
    { "voice": "JBFqnCBsd6RMkjVDRZzb", "text": "Welcome to the show." },
    { "voice": "EXAVITQu4vr4xnSDxMaL", "text": "Thanks — great to be here!" }
  ],
  "language_code": "en",
  "stability": 0.5,
  "title": "Podcast intro"
}
```

- `dialogue` is an ordered array of `{voice, text}` turns — one entry for a
  plain voice-over, many for a conversation. Combined text ≤5000 chars.
- `voice` is an ElevenLabs voice id from `var2_get_voice_list`. Known-good
  defaults: `EXAVITQu4vr4xnSDxMaL` (Sarah — warm female),
  `JBFqnCBsd6RMkjVDRZzb` (George — warm British male).
- `language_code` (ISO 639-1): omit to auto-detect; set it explicitly for
  non-English text. **Hebrew: set `"he"` and add niqqud** (vowel points) to
  the text — it measurably improves pronunciation. See `non-latin-text.md`.
- `stability`: `0` expressive, `0.5` balanced (default), `1` monotone.
  Narration usually wants 0.5; animated characters 0.
- Poll with **`var2_get_dialog_result`** — not `var2_get_audio_result` (that's
  music) and not `var2_get_video_result`.

## Pairing with video (talking head)

The TTS output's `url` feeds straight into `pruna-avatar`:

1. `var2_create_dialog` → poll `var2_get_dialog_result` → take `url` and the
   clip duration.
2. `var2_create_video` with `model: "pruna-avatar"`, `type: "audio-to-video"`,
   `first_frame_url` (a portrait — front-facing, mouth unobstructed),
   `audio_url` = the dialog URL, `audio_duration_seconds` = the duration
   (required; ≤60s), `resolution` 720p/1080p.
3. Poll `var2_get_video_result`.

For audio longer than 60s, cut it with `var2_trim_audio` first (see
`composition.md`) and generate one avatar clip per segment.

## Writing dialog text

- Punctuation drives delivery: commas pause, em-dashes hesitate, exclamation
  marks energize. Write the text the way it should be *spoken*.
- Spell out numbers, dates, and abbreviations in the target language when
  pronunciation matters ("twenty-five", not "25").
- Keep individual turns short; TTS handles several short sentences better than
  one long tangled one.
