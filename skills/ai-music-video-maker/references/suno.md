# The Suno Recipe (music for a music video)

How to get a controllable, lyric-accurate song out of `var2_create_audio`
(model `suno`) as the foundation of a music video.

## Two modes — pick deliberately

| | Default mode | Custom mode |
|---|---|---|
| `customMode` | false (default) | **true** |
| `prompt` | song **description**, ≤500 chars — Suno writes the lyrics | the **full lyrics**, verbatim — no 500-char cap |
| `style` | optional | **required**, ≤200 chars |
| `title` | optional | **required** |

**For a music video you almost always want custom mode.** You need the exact
lyrics ahead of time to plan scenes, split the track on lyric boundaries, and
lip-sync clips. If the user pasted lyrics, use them **verbatim** — never
rewrite them. If you're writing lyrics, write them first, get user approval,
then generate in custom mode.

## The call

```json
{
  "model": "suno",
  "model_version": "V5_5",
  "type": "create-music",
  "customMode": true,
  "prompt": "[Verse 1]\n...full lyrics...\n[Chorus]\n...",
  "style": "anthemic pop-rock, driving drums, female lead vocal, 120 bpm",
  "title": "Falling Skyward",
  "instrumental": false
}
```

- `model_version: V5_5` is the default and best quality; drop to V4 only for
  cost or a specific older sound.
- Structure tags — `[Intro]`, `[Verse 1]`, `[Chorus]`, `[Bridge]`, `[Outro]` —
  measurably help Suno's arrangement. Use them.
- Keep `style` under 200 chars: genre, mood, instrumentation, vocal type,
  tempo. **Never name real artists or songs** — the copyright filter rejects
  the job. Describe the sound instead ("gravelly blues-rock male vocal", not
  "like Springsteen").

## Hebrew (and other non-English) lyrics

- **Add full niqqud (vowel points) to Hebrew lyrics before sending.** Unpointed
  Hebrew is ambiguous; niqqud measurably improves Suno's syllable accuracy and
  pronunciation. If the user gives unpointed lyrics, point them yourself.
- Keep the structure tags in English (`[Verse 1]`) even when lyrics aren't.
- Set expectations: Suno is English-strong; non-English pronunciation may
  still wobble. Instrumental (`instrumental: true`) sidesteps vocals entirely.

## After the call

- Poll `var2_get_audio_result` with the returned `placeholder_id`. Audio
  long-polls; a couple of calls usually suffice.
- A create call returns **two variations** of the same prompt. Report **both**
  share URLs verbatim and let the user pick. The chosen track's
  `placeholder_id` is what every later phase uses.
- **You need the exact final duration in seconds** before segmentation. Take
  it from the result metadata if present; otherwise ask the user to read it
  off the share page, or download the mp3 and run
  `ffprobe -show_entries format=duration`.

## Fixing a near-miss track

Don't regenerate from scratch when one section is wrong:

- "Make it longer / continue past 2:10" → `type: extend-music` +
  `audioRecordId` (the track's placeholder_id) + `continueAt` (seconds).
- "Redo the chorus / replace seconds 40–70" → `type: replace-music-section` +
  `audioRecordId` + `infillStartS` + `infillEndS` (window ~6–60s).

Both edits bill much cheaper than a fresh create.
