# Cost & Tokens

VAR2 bills generation in **tokens**. Different models and modalities cost
different amounts; many video models price **per second** rather than per job,
so duration/resolution/mode choices change the price directly.

## Estimate before you generate

`var2_estimate_cost` is a dry run — it submits nothing and returns per-item
and total token cost.

Input shape:

```json
{
  "items": [
    { "model_id": "veo-3.1", "type": "text-to-video",
      "params": { "duration": 8, "aspect_ratio": "9:16" } },
    { "model_id": "nano-banana-pro", "type": "text-to-image",
      "quantity": 4 }
  ]
}
```

- `type` covers every job kind: image (`text-to-image`, `image-to-image`),
  video (`text-to-video`, `image-to-video`, `reference-to-video`,
  `video-to-video`, `audio-to-video`), audio (`create-music`, `extend-music`,
  `replace-music-section`, `create-dialog`), `image-to-3d`, and modify
  (`upscale`, `remove-bg`).
- `quantity` (1–100) prices a repeated job — use it for "what would 6 scene
  clips cost" instead of duplicating items.
- The `params` you pass should match what you intend to send to the real
  `create_*` call, because cost depends on them (duration, resolution, mode).

## When to estimate

Always estimate and state the cost up front when:

- the user asks "how much" / "what does this cost",
- the job is video, music, or 3D (these are the expensive modalities),
- you're about to use a high-resolution, high-mode (`pro`), or long-duration
  setting,
- the pipeline has 3+ generations — estimate the **whole batch** and show the
  total before starting,
- the user is iterating and cost could add up.

For a single quick low-cost image you can skip the estimate.

## Reporting cost to the user

State it plainly before submitting, e.g.:

> "This will cost about **1,200 tokens** (veo-3.1, 8s, 9:16). Generate it?"

- Costs are **VAR2 tokens, never dollars**. Never guess or invent a dollar
  figure — rates can change; a made-up number is misleading.
- For batch-output models (`grok-imagine` returns several images, `suno`
  returns two tracks) the estimate already reflects the batch — don't multiply
  it yourself.
- For multi-step pipelines, show the per-step breakdown plus the total, and
  re-check before the expensive phase (video) even if you estimated at the
  start.

## Spending less without looking cheap

- Draft on the cheap tier, finalize on the strong one: `z-image-turbo` /
  `flux-schnell` / `gpt-image-15` medium for image drafts; `seedance-2`
  `mode: fast` for video drafts, `pro` for the final.
- For an expensive multi-scene video job, run **one test scene end-to-end**
  and get sign-off before generating the rest.
- Upscaling (`topaz-upscale`) is cheap — generate at 1K/2K and upscale rather
  than paying for 4K when 4K text rendering isn't needed.

## Live pricing is authoritative

Token costs can change. `var2_list_models` carries current pricing metadata
(`pricing_actions`, `typical_cost_range`) and `var2_estimate_cost` reflects
live rules. Never quote a hardcoded price from memory — always estimate.

## Out of tokens / spend cap

If a create call fails with an insufficient-balance or spend-cap error, tell
the user plainly, report what the job would have cost, and point them to
**https://www.var2.ai/dashboard/settings?tab=developers** (and their billing
page). Do not retry the same call in a loop.

## Retries never double-bill — if you use the key

Every `create_*` tool accepts an `idempotency_key`. When retrying a flaky
call, reuse the same key so VAR2 dedupes the job instead of charging twice.
