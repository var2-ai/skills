# Model Catalog

Selection guidance for VAR2 models. **`var2_list_models` is the source of
truth** for exact model IDs, live pricing, and per-model capabilities — call it
when unsure or when the user asks "what models are available" (filter with
`modality`: image | video | audio | 3d | modify). Match by **intent**, not
surface keywords. When two entries could apply, the higher one wins.

Preferred defaults:
- **Image:** `nano-banana-pro` (general + non-Latin text + character
  consistency); `gpt-image-2` (strong prompt adherence, wide aspect support).
- **Video:** `veo-3.1` (all-purpose); `seedance-2` (cinematic);
  `pruna-avatar` (talking head).
- **Music:** `suno`. **Speech/TTS:** `var2_create_dialog` (ElevenLabs, not in
  the model list — voices come from `var2_get_voice_list`).
- **3D:** `trellis-2` (or `tripo` for high fidelity).

---

## Image models

| Model ID | What it's for |
|---|---|
| `nano-banana-pro` | **Default.** Best for Hebrew/Arabic on-image text and character consistency at 2K. Reach for this first. |
| `nano-banana-2` | Non-Latin text plus **4K** output (cheapest path to 4K) and factual grounding via search. |
| `gpt-image-2` | High prompt adherence, the widest aspect-ratio support, up to 15 reference images. Good Hebrew/Arabic. Strong general/design pick. |
| `gpt-image-15` | Quality-tiered (medium/high). Medium for cheap OpenAI-style drafts, high for finals. |
| `flux-2` | Photorealism and sharp fine detail. Weak on non-Latin text — avoid for Hebrew/Arabic captions. |
| `flux-flex` | Flexible, more stylised variant of the Flux line. |
| `seedream-v4` | Seedable / deterministic — reproducible or A/B output. |
| `seedream-5-lite` | Lightweight, social-format friendly (square). |
| `grok-imagine` | Returns a **batch** of variations in one call (6 text-to-image / 2 image-to-image). Use when the user wants options fast. |
| `z-image` | Cheap single-output drafts. |
| `flux-schnell`, `z-image-turbo` | **Cheapest tier** — 4-step distilled text-to-image at a small fraction of standard-tier price. Bulk drafts, concepting. No i2i, no fine text. |
| `flux-2-klein` | Cheapest-tier **image-to-image** + multi-reference (the only i2i in the fast tier). |
| `nano-banana` | **Legacy.** Only if the user explicitly asks for it. |

## Video models

Duration, resolution, and aspect support are **model-specific** — check
`var2_list_models`. Defaults below are starting points.

| Model ID | What it's for |
|---|---|
| `veo-3.1` | **Default all-purpose video.** 1–3 reference images (via `reference_images`, not `reference_image_urls`); good with non-Latin prompts; flat per-job price, ~8s. |
| `seedance-2` | **Cinematic specialist.** Up to 15s, `mode` fast (drafts) / pro (finals), up to 9 image + 3 video + 3 audio refs, native audio (`generate_audio`). Weak on Hebrew/Arabic in scene. |
| `ltx-2.3` | Cinematic with native audio; per-second pricing; first + last frame; good Hebrew/Arabic. |
| `ltx-retake` | **Surgical segment retake** on an existing clip — replace 1–10s of audio, video, or both without re-rendering. Billed on full trimmed source duration. |
| `wan-2.7` | **Video-to-video editing** (the proper V2V model). 720p/1080p, prompt-extend, good Hebrew/Arabic. |
| `pruna-avatar` | **Talking head / lip-sync** (`type: audio-to-video`): portrait + audio (≤60s) → spokesperson clip. The cheapest per-second video path. Requires `audio_duration_seconds`. |
| `happyhorse` | All-in-one: text/image/reference/video-to-video in one model, up to 4 refs, audio control. |
| `kling` | Kling 2.6 — fixed 5s/10s tiers (`duration` as STRING `"5"`/`"10"`), 1:1/16:9/9:16, optional sound. No end frame. |
| `kling-3` | **Multi-shot narratives** (`multi_shots: true` + `shots[]`), first/last frame, subject refs via `kling_elements` (named subjects, 2+ images each). Per-second std/pro pricing. |
| `kling-motion-control` | Motion transfer: drive a still image's subject with a reference motion video. Up to 30s in 10s tiers. |
| `sora-2` | OpenAI aesthetic; frame-count tiers; portrait/landscape. |
| `grok-imagine` | Stylised social shorts, 6/10s (STRING), 480p/720p, modes normal/fun/spicy. |
| `grok-imagine-video-1-5` | Image-to-video only, fine duration control (3–15s slider), widest aspect support (follows the input image). No sound. |

## Music model

| Model ID | What it's for |
|---|---|
| `suno` | Music generation. Versions `V4`…`V5_5` (default `V5_5`). Types: `create-music`, `extend-music`, `replace-music-section`. Default mode: prompt = description ≤500 chars; `customMode: true` for exact lyrics (needs `style` ≤200 chars + `title`; no 500-char cap). English-strong; Hebrew lyrics unreliable. A create call returns **two** variations. Never name real artists/songs. |

## Speech / TTS

Voice-over and dialog are **not** in `var2_list_models` — they run through
`var2_create_dialog` (ElevenLabs v3, multi-speaker, `language_code`,
`stability`). Browse/filter voices with `var2_get_voice_list` (`account`
curated set or 10K+ `library`). See `dialog-and-voices.md`.

## 3D models

| Model ID | What it's for |
|---|---|
| `trellis-2` | **Default.** Image-to-3D, textured GLB. `resolution` 512/1024/1536, `texture_size` 1024–4096. Best price. |
| `tripo` | High-fidelity 3D with PBR materials, up to 20k faces — production assets. A multiple of trellis-2's price — estimate first. |

## Modify models

| Model ID | Type | What it's for |
|---|---|---|
| `topaz-upscale` | `upscale` | Reliable 2x upscale (default). |
| `recraft-upscale` | `upscale` | Crisp upscale, capped at 2048px. |
| `remove-background` | `remove-bg` | Transparent-PNG background removal. |

---

## Picking flow

### Image
1. **On-image Hebrew/Arabic text** → `nano-banana-pro` (or `nano-banana-2` for
   4K). See `non-latin-text.md`.
2. **Need 4K or factual accuracy** → `nano-banana-2`.
3. **Design / banners / heavy prompt adherence / many references** →
   `gpt-image-2`.
4. **Photoreal, sharp detail, Latin text only** → `flux-2`.
5. **Reproducible / A-B / seeded** → `seedream-v4`.
6. **Want several options in one shot** → `grok-imagine`.
7. **Bulk drafts / cheapest possible** → `z-image-turbo` or `flux-schnell`
   (t2i), `flux-2-klein` (i2i), `gpt-image-15` medium for OpenAI-style drafts.
8. **Everything else** → `nano-banana-pro`.

### Video
1. **Talking head / narration over a portrait** → `pruna-avatar`
   (`audio-to-video`).
2. **Edit an existing clip** → `wan-2.7` (restyle/V2V), `ltx-retake` (replace
   a segment), `kling-motion-control` (motion transfer).
3. **Cinematic hero shot** → `seedance-2` (fast for drafts, pro for finals).
4. **Multi-shot story in one prompt** → `kling-3` (`shots[]`) or `seedance-2`.
5. **Needs native audio** → `seedance-2`, `ltx-2.3`, or `kling-3`
   (`sound: true`).
6. **Hebrew/Arabic in scene or narration** → `veo-3.1` (or `ltx-2.3` for
   cinematic-with-non-Latin).
7. **Reference-image driven** → `seedance-2` (`reference_image_urls`, up to 9)
   or `veo-3.1` (`reference_images`, 1–3).
8. **Default** → `veo-3.1`.

### Music / Speech
- Music: always `suno`. Recent `model_version` (`V5_5`) unless the user names
  one. `instrumental: true` for no vocals.
- Spoken word (narration, dialog, character voices): `var2_create_dialog`,
  never `suno`.

### 3D
- Default `trellis-2`. `tripo` when the user says high-quality / detailed /
  production / PBR. Raise `resolution`/`texture_size` only when the user wants
  high detail (costs more).

## Rules of thumb

- **Never invent a model ID.** Unknown IDs are rejected. Verify with
  `var2_list_models`.
- **Don't downgrade for convenience.** If the right model fits the intent, use
  it; don't pick a cheaper/simpler one just because its params look easier.
- **When the user names a model, use it.** Defaults cover common intent; the
  rest of the catalog exists for users who know what they want.
- **Draft cheap, final strong.** For iterative work, draft on the cheap tier
  (`z-image-turbo`, `seedance-2` fast, `gpt-image-15` medium) and re-run the
  winner on the quality tier.
