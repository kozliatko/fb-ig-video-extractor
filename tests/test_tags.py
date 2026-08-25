"""Tests for the tags.py canonical vocabulary / normalization helpers."""
from tags import CANONICAL_TAGS, COUNTRY_TAGS, TAG_ALIASES, normalize_tag, normalize_tags_field


class TestNormalizeTag:
    def test_casing_diacritics_alias(self):
        assert normalize_tag("priroda") == "příroda"
        assert normalize_tag("Příroda") == "příroda"

    def test_separator_variant_alias(self):
        assert normalize_tag("národní_park") == "národní park"
        assert normalize_tag("národnípark") == "národní park"

    def test_country_is_capitalized(self):
        assert normalize_tag("rakousko") == "Rakousko"
        assert normalize_tag("slovensko") == "Slovensko"

    def test_unknown_tag_passes_through_cleaned(self):
        assert normalize_tag("  Fagaraš  ") == "Fagaraš"
        assert normalize_tag("skryté_místo") == "skryté místo"

    def test_already_canonical_is_unchanged(self):
        assert normalize_tag("outdoor") == "outdoor"


class TestNormalizeTagsField:
    def test_merges_and_dedupes_within_row(self):
        # "kemp" and a would-be alias of "kemp" collapsing to the same tag
        assert normalize_tags_field("priroda,příroda,hory") == "příroda,hory"

    def test_no_spaces_around_commas(self):
        assert normalize_tags_field("outdoor,s dětmi,bazén") == "outdoor,s dětmi,bazén"

    def test_empty_and_blank_parts_dropped(self):
        assert normalize_tags_field("outdoor,,  ,hory") == "outdoor,hory"

    def test_preserves_first_seen_order(self):
        assert normalize_tags_field("hory,priroda,turistika") == "hory,příroda,turistika"


class TestAliasTableSanity:
    def test_no_alias_targets_another_alias(self):
        for canon in TAG_ALIASES.values():
            assert canon not in TAG_ALIASES, f"{canon!r} is both an alias target and a source"

    def test_canonical_tags_are_not_themselves_aliased(self):
        for tag in CANONICAL_TAGS:
            assert tag not in TAG_ALIASES, f"{tag!r} is in CANONICAL_TAGS but also a TAG_ALIASES key"

    def test_country_tags_excluded_from_canonical_tags(self):
        # country is a separate derived field now (see geocoder.reverse_geocode_country),
        # not something Gemini should be hinted to reuse as a tag
        assert not (COUNTRY_TAGS & set(CANONICAL_TAGS))
