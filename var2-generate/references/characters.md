# Characters & Consistency

The most common failure in multi-asset work is the "same" character looking
like a different person in every generation. VAR2 gives you three consistency
mechanisms — use them in this order.

## 1. One canonical image, referenced everywhere (within a session)

Generate **one** canonical character/product image first: full body or
three-quarter, neutral pose, plain background, the defining details (face,
hair, wardrobe, build) clearly readable. Get user approval on it before
generating anything downstream.

Then pass its URL into every subsequent generation:

- **Images:** `image_refs` on `var2_create_image` (nano-banana*, gpt-image-2;
  up to 15 refs on gpt-image-2). For scene variations, also use
  `type: image-to-image` with `image_url` = the canonical image and change
  only the background/lighting/angle in the prompt — keep "identical face,
  same hair, same outfit" in the text.
- **Video:** `reference_image_urls` (seedance-2 ≤9, happyhorse ≤4),
  `reference_images` (veo-3.1, 1–3), or `kling_elements` (kling-3 — named
  subjects, each backed by 2+ images; strongest when you have several angles).

`image_refs` beats prose: don't re-describe the character textually each time.

## 2. Storyboard-first for multi-shot video

Image refs into *video* are weaker than image refs into *images*. For any
deliverable with 2+ video shots that must cut together:

1. **Character sheet(s)** — one canonical image per named character/product
   (cheap).
2. **Storyboard frames** — the first frame of every shot as a still, each
   generated with the character sheet as `image_refs` (cheap; approval gate
   before video tokens are spent).
3. **Videos** — each shot as `image-to-video` with its storyboard frame as
   `first_frame_url` (maximum per-shot fidelity), or one `reference-to-video`
   traversing the frames as beats. When multiple frames exist, **ask the user
   which traversal they want** before generating — the choice is irreversible.

This passes the strong image-to-image identity lock *into* each video's first
frame, where it gets baked into the motion.

## 3. Saved character sheets (across sessions) — `var2_save_character`

Persist a character/product/style so it survives the session:

```json
{
  "name": "Dana",
  "kind": "character",
  "images": [
    { "url": "<front-url>", "angle": "front" },
    { "url": "<profile-url>", "angle": "profile" },
    { "url": "<full-body-url>", "angle": "full-body" }
  ],
  "notes": "mid-20s, dark curly hair, denim jacket, silver pendant"
}
```

- 1–12 images (urls / share links / placeholder_ids — auto-resolved). Angle
  labels (`front`, `profile`, `3quarter`, `full-body`) help downstream picks.
- `kind`: `character` (default) | `product` | `style`.
- Saving the same `name` again **replaces** the sheet.
- Typical build: hero image → `var2_modify_image` upscale → a few
  `image-to-image` angle variations → save all angles here.

**Fetching:** when the user mentions a saved name ("use Dana", "our hero
product"), call `var2_get_character` with that `name` **first** — never
regenerate a saved character from a text prompt. It returns durable reference
URLs to pass as `image_refs` / `reference_image_urls` / `kling_elements`.
Called with no `name`, it lists all saved sheets — that's the answer to
"which characters do I have saved?".

## Prompting alongside refs

Refs carry identity; the prompt still steers the scene. Say what to take from
the refs ("the character in ref 1, the palette in ref 2"), state what changes
("same person, now in a rain-soaked street at night"), and repeat the
invariants that must not drift ("identical face, same hair, same outfit").
