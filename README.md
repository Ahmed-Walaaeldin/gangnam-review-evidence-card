# Review Evidence Card

A static, interactive product concept for Gangnam Beauty Guide. A collector saves the public English review listing; a build script embeds five selected records into the standalone page. Three have reviewed evidence-card annotations, and the duplicate matcher checks all five. The core distinction is **reported**, **qualified**, and **not mentioned**. It does not claim to verify patient identities, procedures, surgeons, or the underlying Korean posts.

## Why this feature

A single rating can conceal uncertainty. One five-star review on the current reviews page describes a promising early result while the patient withholds a firm recommendation. Other summaries omit price, recovery, or the name of a surgeon. The card makes those limits visible before a buyer compares clinics.

## Try it

Open `index.html` in any modern browser. Select among three reviews, click a field to highlight its source sentence (or see that no supporting detail is available), toggle “Show gaps only,” or print the selected card. Scroll down to see the duplicate review queue. The published page needs no backend, account, API key, or build step.

## Source and scope

- Source: https://gangnambeautyguide.com/en/reviews/
- Public English summaries visible on 13 October 2026: AB PS (5.0, 13 April), View PS (4.0, 13 April), and Hit PS (4.5, 12 April).
- Clinic, rating, source, date, and the English summary in each card come from collected records. Card field values and interpretations were reviewed manually; they are not automatic extraction or independent verification.
- The duplicate matcher uses five collected English summaries and manually assigned procedure labels. It requires matching clinic, date, and procedure plus distinctive-word overlap. Its output is a candidate queue, never a verified merge.
- This is an independent prototype, not an official Gangnam Beauty Guide feature or medical recommendation.

## A production path

Keep the source URL, original Korean, translation, extraction version, and a citation span for every field. Let extraction abstain. Send claims about surgeon identity, procedure verification, and conflicting time points to human review before publication.

## Free publishing

Upload the generated `index.html` and this README to the **root of a public** GitHub repository. In **Settings → Pages**, choose **Deploy from a branch**, `main`, and `/ (root)`. GitHub will give the project a public `github.io` URL. `index.html` embeds the five selected source records and duplicate logic, so it works as one file.

Run `node dedupe.test.js` to check that similar same-clinic records enter the review queue while different clinics or procedures stay separate.

## Collect real public reviews

Run `python collect_reviews.py` to fetch the current English review listing once and save structured records to `data/reviews.json`. Each record includes the clinic and clinic URL, rating, source platform, review date, English summary, listing position, and a stable content fingerprint. The script uses Python's standard library and writes no output if the layout cannot be parsed.

On this Windows workspace, Python is bundled with Codex but is not on `PATH`. From this folder in PowerShell, rerun it with:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" .\collect_reviews.py
```

The collector was checked against the live page on 13 October 2026 and found 90 summaries. It collects the public English summaries shown by Gangnam Beauty Guide; it does not retrieve original Korean posts, patient identities, individual review permalinks, or independent verification. The `data/` folder is ignored by Git so the full text snapshot is kept local rather than republished with the prototype.

After collecting, run `python build_cards.py` (or use the bundled Python command above with `build_cards.py`) to refresh the three published cards and the duplicate queue from the local snapshot. The build fails if any manually reviewed source record has disappeared or changed, so its annotations are not silently attached to different text. Five selected summaries are embedded in the page; the full 90-record snapshot remains local.
