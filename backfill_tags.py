"""One-off backfill: cleans up column I (tags) using tags.py's TAG_ALIASES.

Merges casing/diacritics/separator duplicates and a few obvious same-lexeme
variants (see tags.py's module docstring for what is and isn't merged) so the
map's tag filter (map_page.py) isn't swamped with near-duplicate chips.

Run locally: venv\\Scripts\\python backfill_tags.py [--dry-run]
"""
import sys
from dotenv import load_dotenv
load_dotenv()

import gspread
from sheets import _get_sheet, NUM_COLS
from tags import normalize_tags_field

TAGS_COL = 9  # column I

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

    old_tags = row[8] or ""
    new_tags = normalize_tags_field(old_tags)
    if new_tags != old_tags:
        report.append(f"row {i}: {name} -> {old_tags!r} => {new_tags!r}")
        updates.append(gspread.Cell(row=i, col=TAGS_COL, value=new_tags))

print("\n".join(report))
print(f"\nRows changed: {len(updates)}")
if DRY_RUN:
    print("DRY RUN - nothing written.")
elif updates:
    sheet.update_cells(updates, value_input_option="USER_ENTERED")
    print("WRITTEN.")
