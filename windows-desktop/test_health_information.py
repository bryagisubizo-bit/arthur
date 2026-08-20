from health_information import find_condition_reference, summarise_article_excerpt


def test_known_condition_uses_reviewed_source_without_diagnosing():
    reference = find_condition_reference("malaria")
    assert reference.exact_match is True
    assert reference.source_name == "World Health Organization"
    assert reference.source_url.startswith("https://www.who.int/")
    assert "cannot confirm" in reference.notice


def test_unknown_condition_returns_search_not_a_diagnosis():
    reference = find_condition_reference("rare example syndrome")
    assert reference.exact_match is False
    assert reference.source_name == "MedlinePlus Health Topics"
    assert "query=rare+example+syndrome" in reference.source_url
    assert "not a diagnosis" in reference.notice


def test_article_note_requires_trusted_source_and_user_pasted_text():
    blocked = summarise_article_excerpt("https://unreviewed.example/article", "This text is deliberately long enough to pass the source check, but the source is not a reviewed public-health domain and must not be accepted by Arthur.")
    assert blocked.summary == ""
    assert "MedlinePlus" in blocked.notice
    note = summarise_article_excerpt("https://medlineplus.gov/example.html", "First sentence has information about a topic. Second sentence adds context that belongs to the article. Third sentence explains another general point. Fourth sentence should normally be outside the short local note.")
    assert note.source_name == "MedlinePlus"
    assert note.summary.startswith("First sentence")
    assert "not diagnose" in note.notice
