#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Merge downloaded sales tax CSVs into docs/rates.csv.

Usage:  python3 build_rates.py downloads/ [--state CA]

Reads every .csv in the folder. Understands:
  - Avalara's free per-state tables (State, ZipCode, TaxRegionName, EstimatedCombinedRate, ...)
  - any CSV whose header names a place column (city, location, jurisdiction) and a rate column
  - headerless lines of: state, county, place, rate
Rates stored as decimals (0.0875) are converted to percent. --state supplies the state
for files that have no state column, such as a single state's city list.
"""
import csv, re, sys
from pathlib import Path

PLACE = [r"^taxregionname$", r"^(place|city|cityname|location|jurisdiction|jurisdictionname|region|name)$"]
RATE = [r"^estimatedcombinedrate$", r"combined", r"^(rate|totalrate|taxrate|salestaxrate|totaltaxrate)$", r"rate"]
STATE = [r"^(state|statecode|stateabbr|stateabbreviation|st)$"]
COUNTY = [r"^county(name)?$"]


def num(s):
    try:
        return float(re.sub(r"[%$\s]", "", s))
    except ValueError:
        return None


def find(header, patterns):
    for pat in patterns:
        for i, h in enumerate(header):
            if re.search(pat, h):
                return i
    return -1


def title(s):
    """MIXED case is kept; ALL CAPS becomes Title Case (matching the web page)."""
    if re.search(r"[a-z]", s):
        return s
    return re.sub(r"(^|[\s\-/(.])([a-z])", lambda m: m.group(1) + m.group(2).upper(), s.lower())


def read(path, fallback_state):
    # Some source files carry a damaged apostrophe (U+FFFD), as in O'Kean, Arkansas.
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
        lines = [r for r in csv.reader(line.replace("\ufffd", "'") for line in f) if r and not r[0].lstrip().startswith("#")]
    if not lines:
        return []
    out = []
    if all(num(x) is None for x in lines[0]):
        h = [re.sub(r"[^a-z0-9]", "", x.lower()) for x in lines[0]]
        si, ci, pi, ri = find(h, STATE), find(h, COUNTY), find(h, PLACE), find(h, RATE)
        if pi < 0 or ri < 0:
            sys.exit(f"{path.name}: need a place column and a rate column in the header")
        if si < 0 and not fallback_state:
            sys.exit(f"{path.name}: no state column; rerun with --state XX")
        for r in lines[1:]:
            rate = num(r[ri]) if ri < len(r) else None
            if rate is None or pi >= len(r) or not r[pi].strip():
                continue
            out.append([(r[si].strip().upper() if si >= 0 else fallback_state), title(r[ci].strip()) if ci >= 0 else "", title(r[pi].strip()), rate])
        if out and 0 < max(x[3] for x in out) <= 0.3:
            for x in out:
                x[3] = round(x[3] * 100, 4)
    else:
        for r in lines:
            rate = num(r[-1])
            if len(r) >= 4 and rate is not None:
                out.append([r[0].strip().upper(), r[1].strip(), ", ".join(c.strip() for c in r[2:-1]), rate])
    return out


def main():
    args = sys.argv[1:]
    state = ""
    if "--state" in args:
        i = args.index("--state")
        state = args[i + 1].upper()
        del args[i:i + 2]
    folder = Path(args[0] if args else "downloads")
    rows, seen = [], set()
    for path in sorted(folder.glob("*.csv")):
        got = read(path, state)
        print(f"{path.name}: {len(got)} rows")
        for r in got:
            key = (r[0], r[2].lower(), r[3])
            if key not in seen:
                seen.add(key)
                rows.append(r)
    rows.sort(key=lambda r: (r[0], r[2], r[3]))
    dest = Path(__file__).parent / "docs" / "rates.csv"
    with open(dest, "w", newline="", encoding="utf-8") as f:
        f.write("# state, county, place, combined rate (%)\n")
        csv.writer(f, lineterminator="\n").writerows(rows)
    print(f"Wrote {len(rows)} unique places to {dest}")


if __name__ == "__main__":
    main()
