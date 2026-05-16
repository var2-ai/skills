# Media Inputs

How to pass images and videos into VAR2 tools.

## URLs only

All media inputs are **public HTTPS URLs**. VAR2 fetches them server-side.

- If the user gives a **local path**, ask them to upload it somewhere public
  (or to the VAR2 web app) and share the URL. Do not attempt to attach binary
  data — these tools take URLs, not file uploads.
- A URL produced by a previous VAR2 result (the asset URL on a share page) can
  be fed straight into the next call (e.g. generate an image, then animate it
  with `first_frame_url`, then turn a frame into 3D).

## Image inputs

| Param | Tool | Role |
|---|---|---|
| `image_url` | `var2_create_image` (`type: image-to-image`) | The image being edited / transformed. |
| `image_refs` | `var2_create_image` | Extra reference images (style/identity/composition). Model-dependent count. |
| `image_url` | `var2_modify_image` | The image to upscale or background-remove. |
| `image` | `var2_create_3d` | Single source image for the 3D mesh. |

For `image-to-image` you must set `type: "image-to-image"` **and** pass
`image_url`. Reference images alone (without `image_url`) do not switch the job
to edit mode.

## Video inputs

| Param | `type` | Role |
|---|---|---|
| `first_frame_url` | `image-to-video` | Still that the clip animates from. |
| `reference_image_urls` | `reference-to-video` | One or more references the model should stay consistent with. |
| `source_video_url` | `video-to-video` | The clip being edited / motion-driven. |

Pick the `type` that matches the intent, then pass only the media that `type`
requires. Passing a `source_video_url` to a `text-to-video` job is a
validation error.

## Model-specific capability

Accepted roles, max counts, durations, resolutions, and aspect ratios vary per
model. `var2_list_models` returns the authoritative capabilities for each
model — consult it rather than assuming. `references/model-catalog.md` gives
the quick intent map; the live list gives the exact limits.

## Good source images for 3D

`trellis-2` works best from a single, sharp, evenly lit image of one object on
a plain background. If the user's source is busy, run `var2_modify_image` with
`type: remove-bg` first, then feed the clean result into `var2_create_3d`
(remember: still only **one** create call per turn — do the remove-bg in one
turn, the 3D in the next).
