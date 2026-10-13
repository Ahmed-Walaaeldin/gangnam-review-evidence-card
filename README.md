# Review Evidence Card

A static product prototype for Gangnam Beauty Guide. It collects the site's public English review summaries and turns the snapshot into a searchable 90-review browser. Three selected reviews have manually checked evidence annotations; the other 87 remain visible as **summary only** so the interface does not invent structured claims.

## What the published page does

- Search all 90 collected summaries by clinic or text and open any review.
- Inspect the full public English summary, rating, source, date, and snapshot position for each review.
- On three reviewed cards, distinguish **reported**, **qualified**, and **not stated** fields, and click a field to highlight the relevant source sentence.
- See two possible duplicate pairs from a small, deterministic five-record triage sample. These are candidates for human review, never verified merges.

The page works without a backend or API key. The 90 records are embedded into `index.html` at build time, so GitHub Pages and a local file preview both work. It is a dated snapshot, not a live feed.

## Data and judgment boundary

Source: https://gangnambeautyguide.com/en/reviews/ . The collector found 90 public English summaries on 13 October 2026. These are summaries published by Gangnam Beauty Guide, not original Korean posts. Patient identity, procedure records, and surgeon identity were not independently verified.

The collector supplies clinic, clinic URL, rating, source platform, date, English summary, and listing position. The three detailed cards' field values, statuses, procedure labels, and sentence links were reviewed manually. The remaining 87 summaries have no field-level annotation. Duplicate similarity is a screening signal, not proof that accounts share a patient or original post.

## Rebuild from the public listing

1. Run `python collect_reviews.py` to fetch the current public English listing once into `data/reviews.json`.
2. Run `python build_cards.py` to embed that snapshot and the duplicate logic into `index.html`.
3. Run `node dedupe.test.js` to check the duplicate-candidate rules, then open `index.html` and inspect the cards.

The build stops if one of the manually annotated source records changes or disappears, so a reviewed claim cannot silently attach to a different summary. Python's standard library is the only collector dependency.

On this Windows workspace, Python is bundled with Codex but is not on `PATH`. From this folder in PowerShell, replace `collect_reviews.py` with `build_cards.py` for the second step:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\collect_reviews.py
```

## Publish on GitHub Pages

Put the generated `index.html` in the repository root. The page is self-contained; GitHub Pages does not run the Python scripts. To show the engineering work, also publish `collect_reviews.py`, `build_cards.py`, `dedupe.js`, `dedupe.test.js`, and this README. In **Settings → Pages**, use **Deploy from a branch → main → /(root)**.

This repository may also include `data/reviews.json` as a public snapshot. That file is not loaded by the published page, because its contents are already embedded in `index.html`. The `.gitignore` in the local project prevents future accidental tracking but does not remove a file already committed to GitHub.

## Production path

Keep an original-post identifier and URL, Korean text, translation, extraction version, and exact source span for every field. Let extraction abstain, and review any claim about surgeon identity, procedure verification, conflicting timelines, or duplicate identity before publication.

This is an independent prototype, not an official Gangnam Beauty Guide feature or medical recommendation.
