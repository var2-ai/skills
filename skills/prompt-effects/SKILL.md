---
name: prompt-effects
version: 0.4.2
description: >-
  Write video-model prompts that draw graphic effects into a clip — a neon
  outline that changes colour on the beat, hand-drawn doodles, a big word
  behind the subject, stripes, comic dots, a scrapbook look, a retro sunburst,
  a beat colour flash or a freeze-frame photo card — in a new clip or as an
  edit of an existing one, fitted to whatever the subject is, on Seedance 2 /
  Seedance 2 Mini. Use when the user wants a stylised, playful or rhythmic
  clip (music, dance, fashion, sneakers, launches, food, kids, travel recaps,
  sport) or asks for one of these looks. NOT for documentaries, news,
  explainers, corporate or serious subjects, NOT for effects added in
  post-production (glitch, light leaks, black-and-white colour pop), and not
  without the VAR2 MCP server connected.
---

# Effects by prompt
Use when a clip should carry a graphic drawn by the video model itself: a neon outline that
changes colour, doodles, a big word behind the subject, stripes, comic dots, a scrapbook look,
a retro sunburst, a beat colour flash or a freeze-frame photo card. It works in a new clip
or as an edit of a clip the user already has. Every effect has a recipe with its exact prompt
([references/recipes.md](references/recipes.md)): read the one you pick before writing.

## When to offer it, and when not to
Offer an effect only when the piece is playful, rhythmic or stylish: music videos, beat-cut
reels, dance, fashion and lookbooks, sneakers and streetwear, launches and drops, food and
cafes, kids and toys, travel and creator recaps, sport highlights, retro sales.
Never: documentaries, news, explainers, tutorials, corporate and B2B, finance, health,
talking heads and interviews, serious or sad subjects. With a calm or premium-minimal brand,
offer only word-behind or stripes-behind, in the brand's own colours.
Not on every clip. In a film with several shots, put an effect on one shot in three or four
(the hook, the drop, the reveal) so it lands. One effect per clip; two only when they do not
compete (neon-outline + doodles). When the user did not ask, offer it as one option with a
one-line reason. Never add it silently.

## Pick the effect for the subject and the moment
- neon-outline: a clear silhouette on a dark or plain ground (a sneaker on a turntable, a
  dancer, a car at night). Changes colour on the beat. Music, nightlife, sneakers, sport.
- beat-colour-flash: high-energy music. Works on any subject. It flashes 3 to 6 times in
  5 s, not on every beat; for exact beat sync, cut in the editor instead.
- doodles: food, kids, cute products, lifestyle. The arrow points at the hero detail.
- word-behind: launches, fashion titles, a product name. One Latin word of 3 to 6 letters that
  the user approved.
- stripes-behind: fashion, editorial, interiors. Needs a wall or sky behind the subject.
- comic-dots: pop, toys, drinks, games. New clips only.
- scrapbook: travel, pets, creators, food.
- sunburst: retro, sales, a hero product, a sport hero. It replaces the background.
- photo-card: the moment to remember (a finish line, a first bite, an arrival); recaps.
Not available here: glitch, light leaks, black and white with one colour kept, clones of the
subject. They failed in our tests, so do not promise them.

## The subject decides the prompt
Every recipe has slots. Fill them from this shot, never from the examples:
- {subject}: what it is, what it does and how it moves ("a white leather sneaker slowly
  turning on a small turntable"). In an edit, name it as it appears in Video 1.
- {setting}: the place, the light and the background the graphic sits on (a plain wall, the
  sky, a studio). Effects need clear ground around the subject.
- {camera}: static, slow push-in, side tracking. A steady camera keeps graphics clean.
- {colours}: 2 to 4 named colours or hex values, taken from the brand kit when there is one.
- {beat}: from the song's BPM: beats per second = BPM / 60 (120 BPM = twice a second).
  Without a song, write "a steady beat, twice a second".
Write graphics as 2D, flat, hand-drawn or neon. Place them by saying "BEHIND the {subject}: it
stays in front, they are hidden wherever its body is and never cross over it". Say when they
appear ("in the first second they draw themselves on") and how they move ("they wobble
slightly every few frames like a hand-drawn animation"). End with "No text, no logos" unless
the effect is a word. Write the prompt in English, whatever language the user speaks.

## Model and settings
- Default: seedance-2-mini. Every recipe was tested on it. 480p and 5 s for a draft; 720p for
  the clip the user keeps. Set generate_audio: false when music or a voice-over goes on top.
- seedance-2 (mode pro, 1080p) for a hero shot that must look its best, with the same prompt.
  Make the draft on seedance-2-mini first, and upgrade only the version the user chose.
- New clip: type text-to-video, or image-to-video when the user has a first frame.
- Edit of an existing clip of 15 s or less: type reference-to-video on seedance-2-mini or
  seedance-2, with reference_video_urls: [the clip] and reference_labels: { videos: ["the source
  clip to edit"] }. Set duration to the clip's length rounded up. Start the prompt with "Edit the
  reference video (Video 1). Keep it exactly as it is: the same {subject}, the same motion,
  framing, camera and timing. Only add". End it with "Do not change" plus the subject's face,
  clothes or shape and the parts of the background the effect does not touch.
- The price is the generation tool's own quote (or var2_estimate_cost). Never quote a price
  from this page.
- Make one 5 s draft of one effect first. Make more effects, longer clips or 720p only after
  the user likes it.

## What our tests showed
- Graphics behind or around the subject work well. Effects that repeat on every beat over the
  whole picture are unreliable.
- In an edit, things happen about 1 s later than asked: ask 1 s earlier than you want them.
- In an edit, doodles come out fewer and smaller: ask for big, bold doodles.
- A word in the picture: one short Latin word, spelled letter by letter in the prompt
  (S-T-Y-L-E). Seedance does not write Hebrew or Arabic well, so no Hebrew or Arabic words in
  the picture. Put those in captions on the timeline instead.
