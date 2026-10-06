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
equipped-2024.json
equipped-2023.json
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
  literal `"room": "TBA"` (newer app builds then show no room chip and
  don't link to a "TBA" room; older ones show a "TBA" chip, so keep the
  word rather than a blank); an unknown speaker is `"speakers": []`; a class
  the schedule doesn't put in a track is `"track": ""` — keep the key, old
  app builds require it (they show such a class under the first track; newer
  builds show no track label). That's why 2027's `tracks` still starts
  with `main` though no session uses it — don't tidy it away, or old
  builds label those classes "Singing".
- **Nothing to list yet?** Leave `hotels`, `foodTrucks` or `vendors` as an
  empty list and put the "coming soon" sentence in its note (`lodgingNote`,
  `foodTrucksNote`, `vendorAreaNote`); the app shows the note in the list's
  place (lodging on the Info tab, food trucks and vendors on the Venue tab). Once the event is over, blank those notes — an archive year
  with an empty list and a leftover note would show the note. (Older app
  builds simply hide an empty section.)
- **How long a class runs** decides the Schedule's "Now" and "Up Next"
  marks during the event. Nothing needs stating in the usual case: a class
  runs 40 minutes, or until the day's next time slot if that starts
  sooner (which is how the 15-minute classes around Saturday lunch come
  out right). To change the usual length for a year, add
  `"sessionMinutes": 45` at the top of the file. For one class that
  differs, such as a long Sunday worship, add `"minutes": 75` to that
  session. If two time slots ever overlap, give the longer class its
  `minutes`, or it will be cut off where the next slot starts. Older app
  builds ignore both keys.
- `venue.mapImage` names the building map the Venue tab shows, by its
  name in the app's asset catalog. Leave the key out for the current
  building (the app then uses `BuildingMap`). A year held somewhere else
  gets `"mapImage": ""`, which means no map: 2023 and 2024 were at Lehman
  Avenue, and without it they showed Cumberland Trace's. Older app builds
  ignore the key and show the current map for every year.
- `video` is a YouTube video id; `podcast` is an Apple Podcasts episode
  id. Add them after the event as recordings post.
- `podbean` is the episode's slug on the Equipped Workshop podcast site
  (the last part of `equippedworkshop.podbean.com/e/<slug>/`). Prefer it:
  that site keeps every episode, while Apple Podcasts only opens a show's
  newest 100, so an old `podcast` id ends up on the show page. Keep
  `podcast` too while the episode is still on Apple — older app builds
  only know that one.
- `womenSpeakers` (top of the file) lists that year's women speakers,
  spelled exactly as in `sessions`. It feeds the Speakers tab's
  All / Men / Women filter; anyone not listed shows under Men.
- `pastPlaylists` holds **that year's own** YouTube playlist and nothing
  else (the name is historical). Leave it `[]` for the upcoming year and
  add the playlist once the recordings are up.
- `speakerBios` is keyed by the speaker's name **exactly** as it appears
  in `sessions`. The app shows the bio from the **newest** year's file
  that has one, whichever year is being viewed, so update a bio in the
  newest file. Older app builds read it from the year on screen, so keep
  copying each bio into every year's file that speaker appears in.
- `notice` (top of the file) shows a dismissible banner on the Schedule
  tab. Editing its wording re-shows it to people who dismissed the old
  one. Set to `null` to remove. 2027's said most rooms hadn't been
  assigned, and came out on 2026-10-06 when the website posted them.
- **A class under two filters** gets `extraTracks`: a list of further
  track ids beside `track`. 2027's Ladies Panel is `"track": "panel"`
  with `"extraTracks": ["ladies"]`, so the app's Tracks filter shows it
  under both and it carries both labels. Older app builds ignore the key
  and show `track` only, so keep the more important label in `track`.
- **Order within a time slot is the file's order**, until rooms break the
  tie (the app sorts a slot by room). 2027 follows the church website's
  order, which leads each slot with the Through The Text class. Moving a
  session up or down the file is safe; its id goes with it.
- Bump `revision` (any short label, e.g. `"2027-final"`) and
  `publishedAt` on every push — the app shows them so you can tell what's
  live.
- **2027's schedule is final** (revision `2027-final-4`, matched to
  ctchurchofchrist.com/equipped on 2026-10-06): `scheduleIsPlaceholder` is
  `false` and `placeholderNote` is `null`, so the app no longer shows its
  "tentative" notice. The website now gives a room and an audience label
  for most classes. Its "Preachers/Leaders" (also written
  "Leaders/Preachers", "Preachers, Leaders" and, once, "Elders/Leaders")
  is the `preachers-leaders` track, "Special Studies" is
  `special-studies`, "Ladies Only" is `ladies`,
  "Youth/College/Young Adult" is `youth`, and "MPR" is the room
  "Multipurpose Room", as the building map spells it. The 16 classes
  titled "Through The Text:" are the `through-the-text` track; that one
  is Michael's choice, taken from the titles, not a label on the
  website. It is second in `tracks`: `main` stays first (see above).
  Where the website
  says "Room 118" the catalog says "Room 129": the organizers told
  Michael on 2026-10-06 that every Room 118 class is in Room 129, so
  don't change it back to match the website. Four classes are
  still `"TBA"` because the website names no room for them: the Friday
  and Saturday 6:30 and 7:00 PM lessons. (It names none for Thursday's
  singing either; Michael confirmed singing is in the auditorium.) As each
  is assigned, set the session's `room` and keep its id. For a future year's
  placeholder, the same two keys are what switch the notice on and off.

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
   In the year that just became an archive, blank the venue's `address`,
   `phone` and `email` (`""` — keep the keys), delete `mapsURL`, and blank
   `gettingThere`. Past years show the venue's name only, so nobody takes
   an old year's details for the current ones.
3. Also add the file to the app's bundled `Resources/` folder in the next
   app release, so new installs work offline. (Remote-only years work
   too — the bundle is just the offline fallback.)
