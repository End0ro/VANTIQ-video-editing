# Video Editing Styles

Style references for `/video-editor`, built from two reels Ahmed analyzed in Claude Cowork. Use these as the default look for each content type — read before editing a new video, alongside the general video-editor skill.

*Last updated: 2026-09-19. Talking head section replaced with the approved house style.*

---

## Educational videos

**Reference:** Reel 1, @bradfordmarais — "Turn Claude into a master scriptwriter"

**Fonts**
- Heavy bold sans-serif throughout, condensed/grotesk style (Helvetica Now/Inter Bold family).
- Hook title: two weights stacked — huge bold keyword, smaller regular text wrapped around it.
- Captions: lowercase, medium-bold, sitting in a rounded gray pill/chip, roughly centered just above the split line between graphic and face-cam.
- No dramatic size jumps beyond the hook-vs-caption contrast.

**Text animation**
- Captions appear phrase-by-phrase (2-4 words at a time) inside the gray pill, not word-by-word.
- Hook title: fade/scale-in on a static hold, not a continuous reveal.
- Clean cut/swap between caption chip and b-roll graphics above it, not a slide.

**Colors**
- Neutral base: white/light-gray text on a soft light-gray-to-white gradient for the top graphic zone, black text for headings.
- Caption pill: translucent dark gray background, white text.
- One consistent brand accent: warm coral/orange, used on the Claude starburst icon, the "Brand Brain" diamond icon, and outlined boxes. This is the through-line accent color for the whole video.

**Motion graphics**
- Screen-recording-style explainer layered with icon graphics: app icon (orange starburst in rounded square), hand-drawn-style winding dashed path with flag markers, a labeled diagram with pill buttons, a grid of thumbnails, a small status chip with a checkmark, gear icons, dashed connector lines linking icons (flowchart/whiteboard style).
- Near the end: a big, faded oversized word layered behind the presenter as a background watermark, with a small label above it, cueing a comment-based CTA.

**Overall style**
- Clean, tutorial/SaaS-demo energy — "founder explains his workflow."
- Split-screen: talking-head video on the bottom half, static explainer graphics on top half.
- Polished, minimal, brand-consistent (one accent color, one font family). Reads like a mini product demo, not chaotic.

---

## Talking head videos

**Status:** Approved house style, 2026-09-19. Ahmed signed off on this after the "нейросети и работа" reel. Use it by default for every talking-head video. Don't fall back to the old Reel 2 look (below) unless he asks.

**Worked example:** `references/examples/talking-head-captions.py`, a full build script for that reel. Copy it into `<videos_dir>/edit/`, swap in the new words and cards, and keep the engine.

**What Ahmed rejected (don't repeat)**
- Generic heavy fonts (Montserrat Black). "No feeling of style."
- Black outline around the words.
- Pop/bump-in scale animations. Words must start invisible and fade in.

**Fonts**
- **Manrope ExtraBold** for regular words, white.
- **Playfair Display Italic SemiBold** for one accent word per phrase, about 1.2x the sans size. Pick the payoff word ("работу.", "меньше.", "на месте.").
- Both are free Google Fonts with Cyrillic. Download the variable files from `github.com/google/fonts` (`ofl/manrope/Manrope[wght].ttf`, `ofl/playfairdisplay/PlayfairDisplay-Italic[wght].ttf`). Then instance them to static weights with fontTools (Manrope wght=800, Playfair wght=600) and rename the families to `VQ Manrope XB` / `VQ Playfair It`. libass ignores variable weights, so this step is required.
- Sizes at 1080x1920: sans 96, accent 116.

**Caption layout**
- 1-2 lines per phrase, 2-6 words, broken on natural pauses. Mixed case, normal punctuation.
- Centered, bottom of the block at about y=590, sitting above the head. Check against a real frame for each new video, since framing changes.
- No outline and no box. Only a soft diffuse shadow: a black copy of each word, blur 16, about 40% opacity, 4px down.
- Numbers as digits (2030, 92, 180).
- Drop fillers ("ну", "там", repeated words) from captions. The audio keeps them. If Ahmed misspoke in a way that flips the meaning, ask whether to caption the intended words.

**Text animation**
- Every word is its own event and appears when it's spoken (word start from the transcript, minus 60ms).
- Reveal: fade in 280ms + blur 6 to 0 over 300ms + rise 12px over 320ms.
- Exit: the whole phrase fades out together over 200ms while blurring back to 6, ending just before the next phrase starts. No overlap and no scaling.

**Rounded cards for key points**
- Use 3-5 per reel on the beats that matter: big numbers, the core reframe, the closing question. The card replaces the caption for that beat.
- Card: warm white fill (`#F7F5F2`, about 97% opacity), radius 34, padding 46/34, soft black drop shadow (blur 22, about 30% opacity, 14px down).
- Card entrance: fade 300ms + blur 8 to 0 + slide up 24px over 420ms. Words inside still reveal as they're spoken.
- Card text: a small gray label on top (Manrope 48, `#88827E`), the main line in Playfair Italic (up to 120) or Manrope 72, dark ink (`#161616`).
- Accents: red `#D9433B` for losses/negatives, green `#2E9D5B` for gains. Two cards side by side work for a comparison (−92 млн vs +180 млн).
- "Wrong question → right question" beat: a red strike line draws left to right through the first card (320ms), the card exits, then the answer card enters in the next pause.

**Motion graphics / other**
- No stickers or emoji icons. The cards do that job.
- No cuts, no color grade unless the footage needs it. The rhythm comes from the word reveals and the cards.

**Render**
- Build an ASS file (PlayRes 1080x1920) and burn it in one pass: `ffmpeg -i src -vf "ass=captions.ass:fontsdir=fonts" -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart final.mp4`.
- Check a contact sheet of frames, including mid-animation frames, before showing Ahmed.

**Old reference (superseded):** Reel 2, @abubakarsakaev. Bold Montserrat-style captions with an outline, pop-in scaling, and a red X sticker. Kept only for history.

---

## Quick reference: which style to use

| Content type | Style |
|---|---|
| Tutorial, workflow demo, "how I use X," product explainer | Educational (Reel 1) |
| Solo talking-head monologue, motivational/mindset, opinion piece | Talking head (house style, see `references/examples/talking-head-captions.py`) |

If a video doesn't clearly match either, ask Ahmed before defaulting to one.
