from language_library import (
    create_colloquial_draft,
    find_language,
    merged_catalogue,
    normalise_favourites,
    parse_iso6393_table,
    prepare_colloquial_entry_review,
    prepare_source_confirmed_expression,
    prepare_search_query,
    search_languages,
    source_confirmed_expressions,
)


def test_catalogue_search_matches_native_label_and_code():
    assert find_language("rw").name == "Kinyarwanda"
    assert find_language("Français").name == "French"
    assert any(entry.name == "Arabic" for entry in search_languages("العربية"))
    dine = find_language("Navajo")
    assert dine.name == "Diné Bizaad (Navajo)"
    assert dine.code == "nv"
    assert "community" in dine.community_review.lower()
    assert any(entry.code == "ain" for entry in search_languages("revitalisation")) is False


def test_favourites_are_known_and_deterministic():
    assert normalise_favourites(["French", "not-a-language", "English", "French"]) == ["English", "French"]


def test_search_preparation_keeps_the_original_query_and_never_searches():
    prepared = prepare_search_query("amakuru y'ikoranabuhanga", "Kinyarwanda")
    assert prepared["ready"] is True
    assert prepared["query"] == "amakuru y'ikoranabuhanga"
    assert prepared["code"] == "rw"
    assert "provider" in prepared["reason"].lower()

    missing = prepare_search_query("", "English")
    assert missing["ready"] is False


def test_colloquial_drafts_require_context_and_are_not_community_reviewed():
    draft = create_colloquial_draft("Navajo", "sample expression", "regional context", "community source to verify")
    assert draft["language"] == "Diné Bizaad (Navajo)"
    assert draft["review_status"] == "Private draft — not community reviewed"
    try:
        create_colloquial_draft("English", "", "regional context", "source")
    except ValueError as error:
        assert "expression" in str(error).lower()
    else:
        raise AssertionError("An empty colloquial expression must be rejected")


def test_local_iso_table_stages_identifiers_without_claiming_capability():
    table = "Id\tPart2B\tPart2T\tPart1\tScope\tLanguage_Type\tRef_Name\tComment\nabc\t\t\t\tI\tL\tExample Language\t\n"
    imported = parse_iso6393_table(table)
    assert len(imported) == 1
    assert imported[0].code == "abc"
    assert imported[0].readiness == "language pack or approved provider"
    assert "identifier table only" in imported[0].community_review
    assert find_language("abc", merged_catalogue(imported)).name == "Example Language"


def test_colloquial_review_requires_meaning_source_and_sensitivity():
    preview = prepare_colloquial_entry_review(
        "English", "example expression", "plain meaning", "regional context", "community source", "use only in the stated context"
    )
    assert preview["review_status"] == "Review preview only — not published or verified"
    assert preview["meaning"] == "plain meaning"
    try:
        prepare_colloquial_entry_review("English", "x", "", "context", "source", "note")
    except ValueError as error:
        assert "meaning" in str(error).lower()
    else:
        raise AssertionError("A review preview without meaning must be rejected")


def test_source_confirmed_records_keep_dialect_and_evidence_boundaries():
    records = source_confirmed_expressions("Haida")
    assert len(records) == 1
    assert "Northern dialect" in records[0]["regional_context"]
    assert records[0]["evidence_url"].startswith("https://")
    assert records[0]["review_status"] == "Source-confirmed — not community-reviewed"


def test_source_confirmation_requires_https_and_reviewer_attestation():
    preview = prepare_source_confirmed_expression(
        "Manx", "Example", "Example meaning", "Isle of Man", "Context documented by source",
        "Use only in cited context", "community-language-program", "Named community resource", "https://example.org/source", True,
    )
    assert preview["review_status"] == "Source-confirmed — not community-reviewed"
    assert "not community review" in preview["verification_note"].lower()
    try:
        prepare_source_confirmed_expression(
            "Manx", "Example", "Example meaning", "Isle of Man", "Context", "Note",
            "community-language-program", "Named source", "http://example.org", True,
        )
    except ValueError as error:
        assert "https" in str(error).lower()
    else:
        raise AssertionError("Non-HTTPS evidence must be rejected")


if __name__ == "__main__":
    test_catalogue_search_matches_native_label_and_code()
    test_favourites_are_known_and_deterministic()
    test_search_preparation_keeps_the_original_query_and_never_searches()
    test_colloquial_drafts_require_context_and_are_not_community_reviewed()
    test_local_iso_table_stages_identifiers_without_claiming_capability()
    test_colloquial_review_requires_meaning_source_and_sensitivity()
    test_source_confirmed_records_keep_dialect_and_evidence_boundaries()
    test_source_confirmation_requires_https_and_reviewer_attestation()
    print("language library regression checks passed")
