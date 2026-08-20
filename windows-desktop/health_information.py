"""Source-linked health-information helpers; never diagnostic or prescriptive."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote_plus, urlparse


@dataclass(frozen=True)
class ConditionReference:
    query: str
    heading: str
    source_name: str
    source_url: str
    exact_match: bool
    notice: str


@dataclass(frozen=True)
class ArticleReadingNote:
    source_url: str
    source_name: str
    summary: str
    notice: str


_CONDITION_SOURCES = {
    "asthma": ("Asthma", "MedlinePlus", "https://medlineplus.gov/asthma.html"),
    "diabetes": ("Diabetes", "MedlinePlus", "https://medlineplus.gov/diabetes.html"),
    "headache": ("Headache", "MedlinePlus", "https://medlineplus.gov/headache.html"),
    "migraine": ("Migraine", "MedlinePlus", "https://medlineplus.gov/migraine.html"),
    "malaria": ("Malaria", "World Health Organization", "https://www.who.int/news-room/fact-sheets/detail/malaria"),
    "tuberculosis": ("Tuberculosis", "World Health Organization", "https://www.who.int/news-room/fact-sheets/detail/tuberculosis"),
}
_ALIASES = {"tb": "tuberculosis", "sugar diabetes": "diabetes", "sugar disease": "diabetes"}
_TRUSTED_HOSTS = ("medlineplus.gov", "nhs.uk", "who.int", "cdc.gov")


def _normalise(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", (value or "").lower()).split())


def find_condition_reference(query: str) -> ConditionReference:
    """Return a direct reviewed source when known, otherwise a source-index search link."""
    cleaned = _normalise(query)
    cleaned = _ALIASES.get(cleaned, cleaned)
    if cleaned in _CONDITION_SOURCES:
        heading, source_name, source_url = _CONDITION_SOURCES[cleaned]
        return ConditionReference(
            query=cleaned,
            heading=heading,
            source_name=source_name,
            source_url=source_url,
            exact_match=True,
            notice="This source explains a condition generally. It cannot confirm that you have it or rule out another cause.",
        )
    if not cleaned:
        return ConditionReference(
            query="",
            heading="Enter a condition name",
            source_name="",
            source_url="",
            exact_match=False,
            notice="Arthur will not guess a disease from symptoms. Enter a condition you want to learn about.",
        )
    return ConditionReference(
        query=cleaned,
        heading="Find a reviewed health topic",
        source_name="MedlinePlus Health Topics",
        source_url=f"https://medlineplus.gov/search/?query={quote_plus(cleaned)}",
        exact_match=False,
        notice="Arthur has not selected an exact condition article. Review the source results yourself; a matching name is not a diagnosis.",
    )


def _trusted_source(url: str) -> str | None:
    host = urlparse((url or "").strip()).hostname or ""
    host = host.lower().removeprefix("www.")
    if host == "medlineplus.gov":
        return "MedlinePlus"
    if host == "nhs.uk":
        return "NHS"
    if host == "who.int":
        return "World Health Organization"
    if host == "cdc.gov":
        return "CDC"
    return None


def summarise_article_excerpt(source_url: str, excerpt: str) -> ArticleReadingNote:
    """Create a local, source-preserving reading note from user-pasted text only."""
    source_name = _trusted_source(source_url)
    if not source_name:
        return ArticleReadingNote(
            "", "", "", "Use a direct public-health URL from MedlinePlus, NHS, WHO, or CDC before requesting a local reading note. Arthur does not fetch or trust unreviewed pages here.")
    cleaned = " ".join((excerpt or "").split())
    if len(cleaned) < 80:
        return ArticleReadingNote(
            source_url.strip(), source_name, "", "Paste at least a short paragraph from the page. Arthur will summarize only the text you provide and will not diagnose or recommend treatment.")
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    selected: list[str] = []
    used = 0
    for sentence in sentences:
        if not sentence:
            continue
        if used + len(sentence) > 620 and selected:
            break
        selected.append(sentence)
        used += len(sentence) + 1
        if len(selected) == 3:
            break
    return ArticleReadingNote(
        source_url.strip(),
        source_name,
        " ".join(selected),
        "Local reading note from text you pasted. Check the source page for context and discuss symptoms or treatment questions with a qualified clinician.",
    )
