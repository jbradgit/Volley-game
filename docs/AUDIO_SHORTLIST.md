# SCORDAGOL — Audio shortlist & plan (for review)

Prepped 2026-06-30 so the next session can be picked up cold. **Owner: skim §3, audition a few links,
and pick — then a session wires them in.** Nothing is wired yet (you wanted to choose first).

---

## 1. Why this matters (scope = TWO jobs)

1. **Replace the current SFX — they're an IP blocker.** The 6 effects in `assets/snd/` are
   **decompiled from the original Flash SWF** (`index.html` line 302 says so). They MUST be swapped for
   original / open-licence sounds before any commercial launch (HANDOVER Track C). The 6 to replace:

   | file (`assets/snd/`) | used for | `sfx.*` call |
   |---|---|---|
   | `whistle.mp3` | match start / full-time / checkout | `sfx.whistle()` |
   | `goal.mp3` | goal cheer | `sfx.goal()` |
   | `boos.mp3` | loss | `sfx.boos()` |
   | `ooh.mp3` | keeper save / near miss | `sfx.save()` |
   | `kick.mp3` | ball contact | `sfx.kick()` |
   | `post.mp3` | woodwork (post/bar) | `sfx.post()` |

2. **Add menu background music** — a looping **jazzy-chiptune** track for the menu/career screens
   (owner: "classic game style digital but jazz"). New; no music exists today.

---

## 2. Licence primer (READ — gets us in trouble if ignored)

- ✅ **CC0 / Public Domain** — best. Use, modify, sell, no credit needed. (Kenney, OpenGameArt CC0 filter,
  Freesound CC0 filter, some itch.io packs.)
- ✅ **Pixabay Content Licence** — free commercial, no attribution, can't resell the audio standalone. Fine for us.
- ⚠️ **CC-BY** — free commercial **but you MUST credit** the author (keep a CREDITS file). OK if we maintain it.
- ❌ **CC-BY-NC / "non-commercial"** — NOT usable (we intend to monetise). Avoid.
- ❌ **"Royalty-free" sites that need a paid licence / sub** (Artlist, Motion Array, TunePocket, ElevenLabs) — skip unless owner buys a licence.

**Always verify the licence on the individual track/pack page** — a site can host mixed licences.

---

## 3. The shortlist (audition these)

### A. Menu music — jazzy chiptune loop
- **Pixabay Music** (Pixabay licence, no credit): https://pixabay.com/music/search/cc0/ — search
  `jazz chiptune`, `swing 8-bit`, `lo-fi chiptune`, `jazzy game`. Big, fast to audition, download MP3.
- **OpenGameArt — CC0 music**: https://opengameart.org/content/cc0-music-0 and the
  commercial-OK audio list https://opengameart.org/content/audio-commercial-use-ok (has jazz/brass loops + chiptune).
- **itch.io — CC0 music assets**: https://itch.io/game-assets/assets-cc0/tag-music and chiptune
  https://itch.io/game-assets/free/tag-chiptune — look for "jazz-inspired"/"swing" chiptune packs (check each pack's licence).
- **Free Music Archive — Chiptune**: https://freemusicarchive.org/genre/Chiptune/ (mostly CC-BY → credit needed).
- Want it bespoke + 100% ours? A short jazzy-chiptune loop can be **generated** (e.g. a small
  Web Audio / tracker tune) — fully original, zero IP risk. Flag if you'd prefer that over sourcing.

### B. SFX — UI clicks, impacts (CC0, Kenney = gold standard, no attribution)
- **Kenney Interface Sounds** (100, CC0): https://kenney.nl/assets/interface-sounds — menu select/confirm/back.
- **Kenney UI Audio** (50, CC0): https://kenney.nl/assets/ui-audio
- **Kenney Impact Sounds** (130, CC0): https://kenney.nl/assets/impact-sounds — **ball `kick` thud + `post` woodwork**.
- All Kenney audio: https://kenney.nl/assets/category:Audio

### C. SFX — football specific (whistle, crowd cheer/goal, boos, "ooh")
- **Pixabay Sound Effects** (no attribution): https://pixabay.com/sound-effects/search/referee/ —
  `referee whistle`, `crowd cheer`, `stadium goal`, `crowd boo`, `crowd ooh`.
- **Freesound** (FILTER to CC0): https://freesound.org — search the same, set Licence = "Creative Commons 0".
  (Many Freesound clips are CC-BY → either credit them or pick a CC0 one.)
- **gamesounds.xyz** — aggregator of CC0/royalty-free (incl. Kenney) if you want one-stop browsing.

---

## 4. How it wires in (so the next session moves fast)

Audio system already exists in `index.html` (~lines 302–326) and is clean:
- `SND` loads `assets/snd/<name>.mp3?v=hr5` via `new Audio()`; `play(name,vol)` clones+plays; `sfx.*`
  wrappers; `muted` in `localStorage["vc_muted"]`; `toggleMute()` (M key / speaker tap); `audio()`
  unlocks playback on the first user gesture (autoplay policy).

**To swap SFX (job 1):** drop the new MP3s over the 6 files in `assets/snd/`, keep the SAME names, and
**bump the `?v=hr5` cache tag** (e.g. `?v=hr6`). No code change needed. (Keep them short, mono, normalised.)

**To add menu music (job 2):** small addition near the SFX block —
```
const bgm = new Audio("assets/snd/menu_music.mp3?v=1"); bgm.loop = true; bgm.volume = 0.4;
```
Start it inside `audio()` (first gesture) when on a menu state, pause when a match starts; gate on `muted`,
and add a music volume to the pause/options UI. **Autoplay gotcha:** browsers won't let it start before a
user gesture — `audio()` already handles that unlock, so kick `bgm.play()` from there.

**Add a `CREDITS.md`** if any chosen asset is CC-BY (list track, author, source URL, licence).

---

## 5. Recommended path (fastest to "ours & legal")
1. **SFX:** Kenney (impacts → kick/post; interface → UI) + Pixabay (whistle/crowd/boos/ooh). All
   CC0/Pixabay = zero attribution, zero IP risk. ~1 session to grab + drop in + bump cache tag.
2. **Menu music:** start on **Pixabay** "jazz chiptune"; if nothing clicks, generate an original loop.
3. Replace all 6 SWF-derived SFX in the same pass → removes that Track-C launch blocker.

Sources: [OpenGameArt CC0](https://opengameart.org/content/cc0-music-0) ·
[Kenney Audio](https://kenney.nl/assets/category:Audio) ·
[Pixabay music](https://pixabay.com/music/search/cc0/) ·
[Pixabay SFX](https://pixabay.com/sound-effects/search/referee/) ·
[Freesound](https://freesound.org) · [itch.io CC0 music](https://itch.io/game-assets/assets-cc0/tag-music) ·
[Free Music Archive chiptune](https://freemusicarchive.org/genre/Chiptune/)
