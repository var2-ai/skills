# Media Inputs

> Supplementary reference. **`SKILL.md` is authoritative** — if anything here
> conflicts with it, follow `SKILL.md`.

How to pass images and videos into VAR2 tools.

## URLs only

All media inputs are **public HTTPS URLs**. VAR2 fetches them server-side.

- If the user gives a **local path** (or an image they uploaded into the
  chat), upload it to `tmpfile.link` first and pass the returned
  `downloadLink` as the URL. See the "Uploading user-provided images into
  VAR2" section in `SKILL.md` for the exact pattern.
- A URL produced by a previous VAR2 result (the asset URL on a share page) can
  be fed straight into the next call (e.g. generate an image, then animate it
  with `first_frame_url`, then turn a frame into 3D).

## Image inputs

| Param | Tool | Role |
|---|---|---|
| `image_url` | `var2_create_image` (`type: image-to-image`) | The image being edited / transformed. |
| `image_refs` | `var2_create_image` | Extra reference images (style/identity/composition). Model-dependent count — `gpt-image-2` takes up to 15, the highest. |
| `image_url` | `var2_modify_image` | The image to upscale or background-remove. |
| `image` | `var2_create_3d` | Single source image for the 3D mesh. Must be background-removed. |

For `image-to-image` you must set `type: "image-to-image"` **and** pass
`image_url`. Reference images alone (without `image_url`) do not switch the job
to edit mode.

## Video inputs

| Param | `type` | Role |
|---|---|---|
| `first_frame_url` | `image-to-video` | Still that the clip animates from. |
| `reference_image_urls` | `reference-to-video` | One or more references the model should stay consistent with (up to ~9 on `seedance-2`). |
| `source_video_url` | `video-to-video` | The clip being edited / motion-driven (`wan-2.7` only). |

Pick the `type` that matches the intent, then pass only the media that `type`
requires. Passing a `source_video_url` to a `text-to-video` job is a
validation error.

`image-to-video` and `reference-to-video` are NOT interchangeable — see the
"image-to-video vs reference-to-video" pitfall in `SKILL.md` for the
mandatory mode-selection question.

## Model-specific capability

Accepted roles, max counts, durations, resolutions, and aspect ratios vary per
model. `var2_list_models` returns the authoritative capabilities for each
model — consult it rather than assuming.

## Good source images for 3D

`trellis-2` works best from a single, sharp, evenly lit image of one object on
a plain background. **Always** run `var2_modify_image` with `type: remove-bg`
first, then feed the clean transparent PNG into `var2_create_3d`. Trellis bakes
every visible pixel into geometry, so any leftover background becomes garbage
mesh.
