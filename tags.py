"""Canonical tag vocabulary for the sheet's tags column (I).

The 2026-08-24 tag audit found 562 distinct raw tag strings across 693 rows -
mostly casing/diacritics/separator variants (e.g. "příroda"/"priroda"/"Příroda")
and a handful of obvious same-lexeme merges (plurals, typos) of the same ~80
recurring concepts, plus a long tail of one-off proper nouns (place names)
that are fine as free-text search keywords but should not each become their
own chip in the map's tag filter (map_page.py's buildTagFilters() renders one
chip per distinct string in this column - 562 chips is not a usable filter).

TAG_ALIASES is deliberately conservative: it only merges variants that are
unambiguously the same tag (casing/diacritics/separators, plurals, country
names normalized to the capitalized form Czech uses for proper nouns). It
does NOT merge related-but-distinct concepts like kemp/karavan/obytný vůz or
hrad/zámek/zřícenina - those stay separate tags on purpose.

Single source of truth for backfill_tags.py; not yet wired into the live
save path (main.py/analyzer.py) or enforced as a whitelist.
"""
import re

# raw tag (as typed in the sheet, after .strip()) -> canonical spelling
TAG_ALIASES: dict[str, str] = {
    'rakousko': 'Rakousko',
    'slovensko': 'Slovensko',
    'polsko': 'Polsko',
    'rumunsko': 'Rumunsko',
    'dolomity': 'Dolomity',
    'pláže': 'pláž',
    'slovinsko': 'Slovinsko',
    'vodopády': 'vodopád',
    'itálie': 'Itálie',
    'italie': 'Itálie',
    'výhledy': 'výhled',
    'švýcarsko': 'Švýcarsko',
    'bazény': 'bazén',
    'chorvatsko': 'Chorvatsko',
    'národní_park': 'národní park',
    'národnípark': 'národní park',
    'priroda': 'příroda',
    'unesco': 'UNESCO',
    'albanie': 'Albánie',
    'albánie': 'Albánie',
    'muzea': 'muzeum',
    'národní.park': 'národní park',
    'opuštěnávesnice': 'opuštěná vesnice',
    'poutnímísto': 'poutní místo',
    'rodinnádovolená': 'rodinná dovolená',
    'skalníútvar': 'skalní útvar',
    'tipnavylet': 'výlet',
    'vylet': 'výlet',
    'výlety': 'výlet',
    'Dovolená': 'dovolená',
    'Historie': 'historie',
    'Hrad': 'hrad',
    'Moře': 'moře',
    'Pláže': 'pláž',
    'Příroda': 'příroda',
    'Tradice': 'tradice',
    'Vesnice': 'vesnice',
    'adrspach': 'Adršpach',
    'bazen': 'bazén',
    'bosna': 'Bosna a Hercegovina',
    'dalmácie': 'Dalmácie',
    'francie': 'Francie',
    'istrie': 'Istrie',
    'kavárny': 'kavárna',
    'krakov': 'Krakov',
    'labské_pískovce': 'Labské pískovce',
    'leto': 'léto',
    'maďarsko': 'Maďarsko',
    'obytný_vůz': 'obytný vůz',
    'opuštěná.vesnice': 'opuštěná vesnice',
    'tip na výlet': 'výlet',
    'tipynavylet': 'výlet',
    'transylvánie': 'Transylvánie',
    'tuscany': 'Tuscany',
    'vodnípark': 'vodní park',
    'vyhled': 'výhled',
    'vyhlídky': 'vyhlídka',
    'útulňa': 'útulna',
    'černá hora': 'Černá Hora',
}

# Curated core vocabulary: canonical tags with >=8 uses after aliasing.
# Not an enforced whitelist (yet) - a reference for what already recurs
# often, e.g. to guide a future analyzer.py prompt change.
CANONICAL_TAGS = [
    'příroda', 'historie', 'turistika', 'hory', 'Rumunsko', 'výlet', 'kemp',
    'Itálie', 'outdoor', 's dětmi', 'ubytování', 'Toskánsko', 'pláž',
    'památky', 'jezero', 'architektura', 'vyhlídka', 'hrad', 'Rakousko',
    'památka', 'moře', 'koupání', 'vodopád', 'UNESCO', 'Polsko', 'město',
    'dovolená', 'Slovensko', 'jeskyně', 'kempování', 'skály', 'výhled',
    'rodiny', 'soutěska', 'národní park', 'muzeum', 'vanlife', 'vesnice',
    'řeka', 'alpy', 'cyklistika', 'Černá Hora', 'Dolomity', 'středověk',
    'zámek', 'cestování', 'děti', 'víno', 'kaňon', 'relaxace', 'klášter',
    'restaurace', 'geologie', 'park', 'gastronomie', 'Dunaj',
]


def normalize_tag(tag: str) -> str:
    """Cleans whitespace/separators and applies TAG_ALIASES if a known variant."""
    t = tag.strip()
    if t in TAG_ALIASES:
        return TAG_ALIASES[t]
    t = re.sub(r"[_.\-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return TAG_ALIASES.get(t, t)


def normalize_tags_field(raw: str) -> str:
    """Normalizes a whole comma-separated tags cell, deduping within the row
    while preserving first-seen order."""
    seen = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        norm = normalize_tag(part)
        if norm not in seen:
            seen.append(norm)
    # no spaces around commas - matches the existing storage convention
    # (analyzer.py's prompt asks Gemini for the same format)
    return ",".join(seen)
