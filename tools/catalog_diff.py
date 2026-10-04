#!/usr/bin/env python3
"""Pre-push sanity diff for equipped-data catalogs.

Compares the working tree's catalog JSONs against the last commit and
reports, per year: added sessions, removed sessions, PROBABLE ID CHURN
(a removed id whose title closely matches an added one — renumbering
that would orphan users' saved schedules), and field-level drift on
surviving ids. Report-only: it never blocks a push.

Usage: python3 tools/catalog_diff.py [--base HEAD]
"""

import argparse
import difflib
import glob
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_FIELDS = ["day", "time", "title", "speakers", "room", "track",
                  "details", "video", "podcast", "podbean"]


def committed(path, base):
    rel = os.path.relpath(path, REPO)
    try:
        out = subprocess.run(["git", "show", f"{base}:{rel}"], cwd=REPO,
                             capture_output=True, check=True)
        return json.loads(out.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def sessions_by_id(catalog):
    return {s["id"]: s for s in catalog.get("sessions", [])}


def similarity(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def diff_catalog(name, old, new):
    print(f"\n=== {name} ===")
    if old is None:
        print(f"  new file ({len(new.get('sessions', []))} sessions) — nothing to diff")
        return

    old_s, new_s = sessions_by_id(old), sessions_by_id(new)
    added = sorted(set(new_s) - set(old_s))
    removed = sorted(set(old_s) - set(new_s))
    kept = set(old_s) & set(new_s)

    # Probable id churn: removed id whose title ~matches an added id.
    churn = []
    for r in removed:
        for a in added:
            score = similarity(old_s[r]["title"], new_s[a]["title"])
            if score >= 0.75:
                churn.append((r, a, score))

    drift = []
    for sid in sorted(kept):
        changes = [f for f in SESSION_FIELDS
                   if old_s[sid].get(f) != new_s[sid].get(f)]
        if changes:
            drift.append((sid, changes))

    if not (added or removed or drift):
        print("  sessions: no changes")
    if added:
        print(f"  added ({len(added)}):")
        for a in added:
            print(f"    + {a}  {new_s[a]['title']}")
    if removed:
        print(f"  removed ({len(removed)}):")
        for r in removed:
            print(f"    - {r}  {old_s[r]['title']}")
    if churn:
        print("  ⚠️  PROBABLE ID CHURN — same class, new id? Users' stars on the")
        print("     old id will be orphaned. If it's the same class, KEEP the old id.")
        for r, a, score in churn:
            print(f"    {r} -> {a}  ({score:.0%} title match)  {old_s[r]['title']!r}")
    if drift:
        print(f"  changed ({len(drift)}):")
        for sid, changes in drift:
            print(f"    ~ {sid}  [{', '.join(changes)}]")

    for field in ["revision", "publishedAt", "scheduleIsPlaceholder",
                  "notice", "datesText", "eventName", "theme"]:
        if old.get(field) != new.get(field):
            print(f"  {field}: {old.get(field)!r} -> {new.get(field)!r}")
    if old.get("revision") == new.get("revision") and sessions_by_id(old) != sessions_by_id(new):
        print("  ⚠️  sessions changed but `revision` didn't — bump it so what's live is traceable")

    for coll in ["days", "tracks", "rooms", "hotels", "foodTrucks", "vendors",
                 "pastPlaylists", "womenSpeakers"]:
        if old.get(coll) != new.get(coll):
            print(f"  {coll}: changed")
    old_bios, new_bios = old.get("speakerBios", {}), new.get("speakerBios", {})
    if old_bios != new_bios:
        b_added = set(new_bios) - set(old_bios)
        b_removed = set(old_bios) - set(new_bios)
        b_edited = {k for k in set(old_bios) & set(new_bios) if old_bios[k] != new_bios[k]}
        parts = [f"+{sorted(b_added)}" if b_added else "",
                 f"-{sorted(b_removed)}" if b_removed else "",
                 f"~{sorted(b_edited)}" if b_edited else ""]
        print(f"  speakerBios: {' '.join(p for p in parts if p)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="HEAD",
                        help="git rev to diff against (default HEAD)")
    args = parser.parse_args()

    paths = sorted(glob.glob(os.path.join(REPO, "equipped-*.json")))
    if not paths:
        sys.exit("no equipped-*.json catalogs found")

    for path in paths:
        with open(path) as f:
            new = json.load(f)
        diff_catalog(os.path.basename(path), committed(path, args.base), new)

    manifest_path = os.path.join(REPO, "manifest.json")
    with open(manifest_path) as f:
        new_manifest = json.load(f)
    old_manifest = committed(manifest_path, args.base)
    print("\n=== manifest.json ===")
    if old_manifest is None:
        print("  new file")
    elif old_manifest == new_manifest:
        print("  no changes")
    else:
        print(f"  {json.dumps(old_manifest)}\n  -> {json.dumps(new_manifest)}")
    print()


if __name__ == "__main__":
    main()
