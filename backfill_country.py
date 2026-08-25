"""One-off backfill for the country column (U), added 2026-08-25.

Fills in column U by reverse-geocoding each row's existing lat/lng (via
geocoder.reverse_geocode_country - requires GOOGLE_MAPS_API_KEY with the
Geocoding API enabled), and strips any country name still sitting in the
tags column (I) - see tags.py's COUNTRY_TAGS - now that country is its own
field instead of a tag.

Run locally: venv\\Scripts\\python backfill_country.py [--dry-run]
"""
import sys
from dotenv import load_dotenv
load_dotenv()

import gspread
from sheets import _get_sheet, NUM_COLS
from geocoder import reverse_geocode_country
from tags import COUNTRY_TAGS

COUNTRY_COL = 21  # column U
TAGS_COL = 9       # column I

DRY_RUN = "--dry-run" in sys.argv

sys.stdout.reconfigure(encoding="utf-8")
sheet = _get_sheet()
values = sheet.get_all_values()

updates = []   # gspread.Cell
report = []

for i, row in enumerate(values, start=1):
    if len(row) < NUM_COLS:
        row = row + [""] * (NUM_COLS - len(row))
    name = (row[4] or "").strip()
    if not name:
        continue  # header / invalid row

    try:
        lat = float(str(row[5]).replace(",", "."))
        lng = float(str(row[6]).replace(",", "."))
    except ValueError:
        continue

    old_country = (row[20] or "").strip()
    country = old_country
    if not old_country:
        country = reverse_geocode_country(lat, lng)
        if country:
            report.append(f"row {i}: {name} -> country = {country!r}")
            updates.append(gspread.Cell(row=i, col=COUNTRY_COL, value=country))

    # Only strip a country tag once this row actually has a resolved country
    # (existing or just fetched) - otherwise (e.g. Geocoding API not enabled
    # yet) we'd erase the only record of the country with nothing to replace it.
    if country:
        old_tags = row[8] or ""
        kept = [t.strip() for t in old_tags.split(",") if t.strip() and t.strip() not in COUNTRY_TAGS]
        new_tags = ",".join(kept)
        if new_tags != old_tags:
            report.append(f"row {i}: {name} -> tags {old_tags!r} => {new_tags!r}")
            updates.append(gspread.Cell(row=i, col=TAGS_COL, value=new_tags))

print("\n".join(report))
print(f"\nCells to write: {len(updates)}")
if DRY_RUN:
    print("DRY RUN - nothing written.")
elif updates:
    sheet.update_cells(updates, value_input_option="USER_ENTERED")
    print("WRITTEN.")
