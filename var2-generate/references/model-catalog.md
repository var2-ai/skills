# Model Catalog

Selection guidance for VAR2 models. **`var2_list_models` is the source of
truth** for exact model IDs, live pricing, and per-model capabilities — call it
when unsure or when the user asks "what models are available". Match by
**intent**, not surface keywords. When two entries could apply, the higher one
wins.

Preferred defaults:
- **Image:** `nano-banana-pro` (general + non-Latin text + character
  consistency); `gpt-image-2` (strong prompt adherence, wide aspect support).
- **Video:** `veo-3.1` (all-purpose, reference-image support).
- **Music:** `suno`.
- **3D:** `trellis-2`.

---

## Image models

| Model ID | What it's for |
|---|---|
| `nano-banana-pro` | **Default.** Best for Hebrew/Arabic on-image text and character consistency. Reach for this first. |
| `nano-banana-2` | Non-Latin text plus **4K** output and factual grounding. Step up from pro when you need 4K or accuracy on real-world facts. |
| `gpt-image-2` | High prompt adherence, the widest aspect-ratio support, up to many reference images. Good Hebrew/Arabic. Strong general/design pick. |
| `gpt-image-15` | Quality-tiered (medium/high). Use medium for cheap drafts, high for finals. |
| `flux-2` | Photorealism and sharp fine detail. Weak on non-Latin text — avoid for Hebrew/Arabic captions. |
| `flux-flex` | Flexible, more stylised variant of the Flux line. |
| `seedream-v4` | Seedable / deterministic — use when the user wants reproducible or A/B output. |
| `seedream-5-lite` | Lightweight, social-format friendly (square). |
| `grok-imagine` | Returns a **batch** of variations in one call (6 text-to-image / 2 image-to-image). Use when the user wants options fast. |
| `z-image` | Cheapest active model. Fast, low fidelity — drafts and quick iteration only. |
| `nano-banana` | **Legacy.** Only if the user explicitly asks for it. |

## Video models

Duration, resolution, and aspect support are **model-specific** — check
`var2_list_models`. Defaults below are starting points.

| Model ID | What it's for |
|---|---|
| `veo-3.1` | **Default all-purpose video.** Supports reference images; good with non-Latin prompts. ~8s default. |
| `ltx-2.3` | Cinematic with native audio; per-second pricing; supports first + last frame; good Hebrew/Arabic. |
| `wan-2.7` | The only model with **video-to-video** editing. 720p/1080p, prompt-extend. |
| `seedance-2` | Cinematic, long-form (up to ~15s), draft (`fast`) vs. final (`pro`) modes, heavy multi-reference. |
| `happyhorse` | All-in-one: text/image/reference/video-to-video in one model, 720p/1080p, audio. |
| `kling` | Fixed duration tiers (`5`/`10`, string), 1:1/16:9/9:16, optional sound. |
| `kling-3` | **Multi-shot narratives** — pass an array of shot prompts. Per-second pricing. |
| `kling-motion-control` | Motion transfer: drive a clip from a reference motion video (video-to-video). |
| `sora-2` | OpenAI aesthetic; portrait/landscape. |
| `grok-imagine-video` | Stylised short clips (6/10s), batch-friendly. |

## Music model

| Model ID | What it's for |
|---|---|
| `suno` | Music generation. Versions `V4`, `V4_5`, `V4_5PLUS`, `V4_5ALL`, `V5`, `V5_5`. Types: `create-music`, `extend-music`, `replace-music-section`. English-strong; Hebrew lyrics unreliable. A create call returns **two** variations. `style` ≤200 chars. |

## 3D model

| Model ID | What it's for |
|---|---|
| `trellis-2` | Image-to-3D. Single image URL in, textured GLB out. `resolution` 512/1024/1536, `texture_size` 1024/2048/3072/4096. Higher = more detail and cost. |

## Modify models

| Model ID | Type | What it's for |
|---|---|---|
| `topaz-upscale` | `upscale` | Reliable 2x upscale. |
| `recraft-upscale` | `upscale` | Crisp upscale, capped at 2048px. |
| `remove-background` | `remove-bg` | Transparent-PNG background removal. |

---

## Picking flow

### Image
1. **On-image Hebrew/Arabic text** → `nano-banana-pro` (or `nano-banana-2` for 4K). See `non-latin-text.md`.
2. **Need 4K or factual accuracy** → `nano-banana-2`.
3. **Design / banners / heavy prompt adherence / many references** → `gpt-image-2`.
4. **Photoreal, sharp detail, Latin text only** → `flux-2`.
5. **Reproducible / A-B / seeded** → `seedream-v4`.
6. **Want several options in one shot** → `grok-imagine`.
7. **Fast cheap drafts** → `z-image` or `gpt-image-15` (medium).
8. **Everything else** → `nano-banana-pro`.

### Video
1. **Video-to-video edit** → `wan-2.7` (or `kling-motion-control` for motion transfer, `happyhorse` general).
2. **Multi-shot story** → `kling-3` (shot-prompt array) or `seedance-2`.
3. **Needs native audio** → `ltx-2.3`.
4. **Reference-image driven** → `veo-3.1` or `seedance-2`.
5. **Default** → `veo-3.1`.

### Music
- Always `suno`. Pick a recent `model_version` (`V5`/`V5_5`) unless the user names one. `instrumental: true` for no vocals.

### 3D
- Always `trellis-2`. Raise `resolution`/`texture_size` only when the user wants high detail (costs more).

## Rules of thumb

- **Never invent a model ID.** Unknown IDs are rejected. Verify with `var2_list_models`.
- **Don't downgrade for convenience.** If the right model fits the intent, use it; don't pick a cheaper/simpler one just because its params look easier.
- **When the user names a model, use it.** Defaults cover common intent; the rest of the catalog exists for users who know what they want.
