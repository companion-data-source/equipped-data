# equipped-data

Live event data for the **Equipped** iOS app (Cumberland Trace church of
Christ's annual workshop). The app fetches these files from this repo's
raw URLs at launch and when it returns to the foreground, so **pushing a
commit here updates every installed app within about an hour — no App
Store release needed.** (GitHub's raw-file CDN caches for ~5 minutes, so
don't expect a change to appear the same minute you push; the app also
waits at least an hour between checks within one run.)

```
manifest.json        which years exist and which is newest
equipped-2027.json   one catalog per year: schedule, speakers, rooms, info
equipped-2026.json
equipped-2025.json   archive years keep their recordings (`video`) linked
tools/catalog_diff.py   run before every push (see below)
```

## THE ONE RULE: session ids are forever

Every session has an `id` (like `"fri-9"`). Users' **My Schedule stars
and reminders are tied to these ids.** If you regenerate or renumber
ids, every user's saved schedule silently empties.

- When **correcting** a session (time, room, title, speaker), **keep its
  id**.
- Only assign a **new** id to a genuinely **new** session.
- When the real 2027 schedule replaces the placeholder, reuse ids for
  sessions that survive (the Thursday singing is still `thu-1`), and give
  brand-new classes brand-new ids. Deleting an id is fine — a star with
  no session just disappears quietly.
- Never derive ids from array position.
- **2027's retired ids are not free.** The first 2027 catalog was a
  placeholder: 2026's classes under `thu-1`–`thu-3`, `fri-1`–`fri-22`,
  `sat-1`–`sat-29`, `sun-1`–`sun-6`. People starred those. Number a new
  2027 session above the highest id its day has ever had (the tentative
  schedule starts at `thu-4`, `fri-23`, `sat-30`, `sun-7`), and bring a
  retired id back only for the same class. Four carried over that way:
  singing (`thu-1`, `fri-20`, `sat-27`) and Kathy & Carla (`fri-9`, now
  on Saturday).

## Editing cheat-sheet

Sessions look like this (`day` must match an id in `days`, `track` an id
in `tracks`, `time` is `"6:30 PM"` style):

```json
{
  "id": "fri-9",
  "day": "friday",
  "time": "11:00 AM",
  "title": "Looking Up With Kathy And Carla",
  "speakers": ["Kathy Pollard", "Carla Moore"],
  "room": "Room 114",
  "track": "ladies",
  "video": "YeRBFglG2Q4",
  "podcast": "1000769354911"
}
```

- **Not decided yet? Say so, don't guess.** An unassigned room is the
  literal `"room": "TBA"`; an unknown speaker is `"speakers": []`; a class
  the schedule doesn't put in a track is `"track": ""` — keep the key, old
  app builds require it (they show such a class under the first track; newer
  builds show no track label). That's why 2027's `tracks` still starts
  with `main` though no session uses it — don't tidy it away, or old
  builds label those classes "Singing".
- **Nothing to list yet?** Leave `hotels`, `foodTrucks` or `vendors` as an
  empty list and put the "coming soon" sentence in its note (`lodgingNote`,
  `foodTrucksNote`, `vendorAreaNote`); the Info tab shows the note in the
  list's place. Once the event is over, blank those notes — an archive year
  with an empty list and a leftover note would show the note. (Older app
  builds simply hide an empty section.)
- `video` is a YouTube video id; `podcast` is an Apple Podcasts episode
  id. Add them after the event as recordings post.
- `speakerBios` is keyed by the speaker's name **exactly** as it appears
  in `sessions`.
- `notice` (top of the file) shows a dismissible banner on the Schedule
  tab. Editing its wording re-shows it to people who dismissed the old
  one. Set to `null` to remove.
- Bump `revision` (any short label, e.g. `"2027-final"`) and
  `publishedAt` on every push — the app shows them so you can tell what's
  live.
- When the real 2027 schedule lands: update `sessions`, set
  `scheduleIsPlaceholder` to `false` and `placeholderNote` to `null`.

## Safety rails built into the app

- Old app builds ignore files with a newer `formatVersion` and keep their
  last good data; a `minAppBuild` on a manifest year entry hides that year
  from builds that are too old (they show an "update the app" note).
- Core links (venue, YouTube, podcast, maps) only work if they point at
  known hosts; vendor websites must be https.
- A malformed push never breaks the app — it keeps the previous data. But
  don't rely on that; run the diff.

## Before every push

```bash
python3 tools/catalog_diff.py
```

Compares your working tree against the last commit (`HEAD`) and reports
added/removed sessions, **probable id churn** (a removed id whose title
closely matches an added one — the bug the ONE RULE exists to prevent),
and field-level drift. It reports; it never blocks. If it flags id churn
you didn't intend, fix the ids before pushing.

## Adding a year (annual turnover)

1. Copy the newest catalog to `equipped-20XX.json`; update `year`,
   `eventName`, `theme`, `datesText`, `days` (real dates), sessions.
2. Add the year to `manifest.json` and point `latestYear` at it.
3. Also add the file to the app's bundled `Resources/` folder in the next
   app release, so new installs work offline. (Remote-only years work
   too — the bundle is just the offline fallback.)
