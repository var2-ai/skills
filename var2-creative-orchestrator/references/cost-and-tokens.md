# Cost & Tokens

> Supplementary reference. **`SKILL.md` is authoritative** — if anything here
> conflicts with it, follow `SKILL.md`.

VAR2 bills generation in **tokens**. Different models and modalities cost
different amounts; some video/audio models price **per second** rather than
per job. Costs are always reported in tokens, never dollars.

## Estimate before you generate

`var2_estimate_cost` is a dry run — it submits nothing and returns per-item and
total token cost.

Input shape:

```json
{
  "items": [
    { "model_id": "veo-3.1", "type": "text-to-video", "params": { "duration": 8, "aspect_ratio": "9:16" } }
  ]
}
```

Output: a per-item token cost and a total. The `params` you pass should match
what you intend to send to the real `create_*` call, because cost depends on
them (duration, resolution, mode, etc.).

## When to estimate

Always estimate and state the cost up front when:

- the user asks "how much" / "what does this cost",
- the pipeline has 3+ generations,
- any step is video, music, or 3D,
- you're about to use a high-resolution or long-duration setting.

For a single quick low-cost image you can skip the estimate.

## Reporting cost to the user

State it plainly before submitting. Show per-step token breakdown plus the
total, e.g.:

> "Pipeline total: **~4,000 tokens** (1× key-art image 400 + 3× storyboard panels 1,200 + 1× seedance-2 8s pro 2,200 + 1× suno track 200). Run it?"

For batch-output models (`grok-imagine` returns several images, `suno` returns
two tracks) the estimate already reflects the batch — don't multiply it
yourself.

## Live pricing is authoritative

Token costs can change. `var2_list_models` carries current pricing metadata
(see the `pricing_actions` array) and `var2_estimate_cost` reflects live rules.
Never quote a hardcoded price from memory — always estimate.

## Out of tokens / spend cap

If a create call fails with an insufficient-balance or spend-cap error, tell
the user plainly, report what the job would have cost, and point them to
**https://www.var2.ai/dashboard/settings?tab=developers** (and their billing
page). Do not retry the same call in a loop.
