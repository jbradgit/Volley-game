# Original-game mechanics reference (decompiled ActionScript)

These `.as` files are the decompiled ActionScript of the 2007 Flash game whose
physics/scoring SCORDAGOL's engine transcribes (HANDOVER constraint #1: `logicStep()`,
`savedCheck()` and the constants block in `index.html` are 1:1 from `frame_9`/`frame_10`
here, and must never change without the CI goldens proving outcomes identical).

**This folder is the ONLY original-game material left in the working tree.** The rest of
the reverse-engineering workshop (`original.swf`, `gamezip/`, `ruffle/` + `ruffle.html`,
`decomp/` exports incl. `swf.xml`, ripped sprite/bg/sound exports, ref screenshots) was
removed on 2026-07-02 (owner call: "only the grid layout and game mechanics info are
still needed"). The stadium geometry lives in `docs/STADIUM_ASSET_SPEC.md` +
`docs/stadium_grid_template.png`; the original SFX provenance is recorded in
`docs/AUDIO_SHORTLIST.md` §1b. Everything deleted remains recoverable from Git history
until the planned ROADMAP C.3 history rewrite.

⚠ **IP note:** this is still third-party code kept purely as an engineering reference.
It must move to the private archive repo (and out of public history) when ROADMAP C.3's
`git filter-repo` step runs. Do not ship, quote, or translate it into new features.
