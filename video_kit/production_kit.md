# Diecast Promo Remake: Production Kit (41 s, 9:16)

Placeholders to replace: **[STORE]** (store name), **[@HANDLE]** (Instagram), **[GROUP]** (WhatsApp group), **[LOGO]** (your watermark), **₹[PRICE]**.

Format: 720x1280 (or 1080x1920), 30 fps. Every shot is 3 s unless noted.

---

## 1. Voiceover script (Indian English, about 95 words, fits 41 s)

| Time | Line |
|---|---|
| 0:00–0:03 | "Wait… did a Hot Wheels car just open my drink?" |
| 0:03–0:06 | "Meet the Hot Wheels Carbonator!" |
| 0:06–0:12 | "From the side, it looks exactly like a little bottle… but turn it around, and boom, it's a proper race car." |
| 0:12–0:18 | "And yes, the back actually works as a bottle opener. Glass bottle, can, anything!" |
| 0:18–0:21 | "Bring it out with your friends, and everyone will want one." |
| 0:21–0:27 | "But finding these in stores? Almost impossible. They're gone the moment they land." |
| 0:27–0:33 | "That's why you should follow [STORE] on Instagram, for all the latest diecast drops." |
| 0:33–0:39 | "Join our WhatsApp group to get Hot Wheels, Matchbox and Mini GT at MRP, before anyone else." |
| 0:39–0:41 | "Link in bio. Don't miss the next drop!" |

**Delivery:** friendly, energetic Indian English, like a young Bangalore or Mumbai creator. Medium-fast pace, with a small pause after "boom".

## 2. Voice settings

- **ElevenLabs:** search the Voice Library for "Indian English male, young, energetic". Stability 40, Similarity 75, Style 30.
- **Azure TTS / Edge:** `en-IN-PrabhatNeural` (male) or `en-IN-NeerjaNeural` (female), rate +8%. Example SSML:
```xml
<speak version="1.0" xml:lang="en-IN"><voice name="en-IN-PrabhatNeural"><prosody rate="+8%">
Wait… did a Hot Wheels car just open my drink?<break time="300ms"/> Meet the Hot Wheels Carbonator!
</prosody></voice></speak>
```
- Export as `voiceover.mp3`.

## 3. Shot prompts (image-to-video or text-to-video: Kling / Veo / Runway / Hailuo)

Add this to every prompt: *"vertical 9:16, photorealistic, cinematic product commercial, shallow depth of field, 3 seconds"*

1. **0–3 s:** Extreme close-up of an amber beer bottle neck in warm dark lighting. A hand uses the rear of a small metallic pink-and-teal toy race car to pop off the bottle cap, and the cap flips upward.
2. **3–6 s:** A hand holds a dark beer bottle labelled "Your favourite drink" next to the toy car on a grey studio background, with wisps of cold vapour. Leave space at the top for a title.
3. **6–9 s:** On a seamless beige backdrop, a small pink-and-teal translucent toy shaped exactly like a soda bottle lies on its side. Slow camera orbit.
4. **9–12 s:** The camera continues its orbit, revealing that the bottle-shaped toy is a race car with gold wheels and a chrome rear wing. Same beige backdrop.
5. **12–15 s:** A clear glass soda bottle with a label reading "YOUR FAVOURITE DRINK". A hand pops the cap using the toy car's rear. Cool grey studio.
6. **15–18 s:** The same action on a frosty silver can with condensation, the car's rear lifting the ring pull.
7. **18–21 s:** Three young Indian friends at an outdoor café, cheering. One holds the toy car up in the air, and the background is bokeh with plants and string lights.
8. **21–24 s:** A toy-shop pegboard wall packed with carded 1:64 diecast cars (generic packaging, no logos). Slow push-in.
9. **24–27 s:** A hand pulls one carded red sports-car diecast off the peg towards the camera.
10. **27–30 s:** A smartphone floats at an angle on a dark tech background showing an Instagram profile. Glowing text sweeps in: "[STORE]". *(Easier: screen-record your real profile, then add a tilt and glow in the edit.)*
11. **30–33 s:** A straight-on phone screen showing the profile, with an animated sticker reading "FOLLOW! Follow for Diecast Drops". *(Screen recording plus a sticker overlay.)*
12. **33–36 s:** A WhatsApp group "[GROUP]" scrolling posts: car photo, "MRP ₹[PRICE]", "DM to claim". *(Screen-record a real or test group.)*
13. **36–39 s:** A hand holds a phone at an outdoor café, and a notification pops up: "[STORE]: New drop is now LIVE! Limited stock, DM to claim".
14. **39–41 s:** A hand holds the carded Carbonator against the pegboard. Add the end card: "[@HANDLE]".

**Tip:** for shots 1–6 and 14, upload a real photo of the car as the reference image so the toy looks the same in every shot.

## 4. On-screen text

- 0:03: **HOT WHEELS: CARBONATOR** (big, yellow-red, slight shake)
- 0:12: "It opens bottles! 🍾"
- 0:21: "Sold out everywhere 😩"
- 0:27: **[STORE]**
- 0:33: "MRP drops on WhatsApp"
- 0:39: **Follow [@HANDLE]**
- [LOGO] watermark in the bottom-right corner throughout

## 5. Audio

Use upbeat trap or phonk at a low level (−18 dB under the voice). Add sound effects: a cap pop at 0:01, 0:13 and 0:16, a whoosh at 0:09 and 0:27, and a notification ding at 0:36.

## 6. Hand-back to me

Name the files `01.mp4` … `14.mp4`, then upload them with `voiceover.mp3` (and optionally `music.mp3` and `logo.png`). I'll put them together with ffmpeg: trims, captions, sound effects, ducking and the watermark, rendered as a 1080x1920 MP4.
