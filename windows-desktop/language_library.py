"""Local language catalogue and query-preparation helpers for Arthur.

The catalogue is descriptive only.  Selecting a language never installs a speech
model, opens a microphone, translates text, or contacts a search provider.
"""

from __future__ import annotations

import csv
from io import StringIO
from dataclasses import dataclass
from typing import Iterable
import unicodedata


@dataclass(frozen=True)
class LanguageEntry:
    name: str
    code: str
    native_label: str
    script: str
    readiness: str
    aliases: tuple[str, ...] = ()
    community_review: str = "No community review is bundled"
    vitality_context: str = "No vitality label is bundled"
    colloquial_status: str = "No colloquial expressions are bundled"


PRIMARY_LOCAL = {"English", "Kinyarwanda", "French", "Kiswahili"}


def _entry(
    name: str,
    code: str,
    native: str,
    script: str = "Latin",
    *,
    aliases: tuple[str, ...] = (),
    community_review: str = "No community review is bundled",
    vitality_context: str = "No vitality label is bundled",
    colloquial_status: str = "No colloquial expressions are bundled",
) -> LanguageEntry:
    readiness = "local profile" if name in PRIMARY_LOCAL else "language pack or approved provider"
    return LanguageEntry(name, code, native, script, readiness, aliases, community_review, vitality_context, colloquial_status)


LANGUAGE_CATALOGUE: tuple[LanguageEntry, ...] = (
    _entry("English", "en", "English"), _entry("Kinyarwanda", "rw", "Ikinyarwanda"),
    _entry("French", "fr", "Français"), _entry("Kiswahili", "sw", "Kiswahili"),
    _entry("Afrikaans", "af", "Afrikaans"), _entry("Ainu", "ain", "アイヌ・イタㇰ", "Kana / Latin", vitality_context="Community revitalisation context — authoritative community source required"), _entry("Albanian", "sq", "Shqip"),
    _entry("Amharic", "am", "አማርኛ", "Ethiopic"), _entry("Arabic", "ar", "العربية", "Arabic"),
    _entry("Armenian", "hy", "Հայերեն", "Armenian"), _entry("Azerbaijani", "az", "Azərbaycanca"),
    _entry("Bambara", "bm", "Bamanankan"), _entry("Basque", "eu", "Euskara"),
    _entry("Belarusian", "be", "Беларуская", "Cyrillic"), _entry("Bengali", "bn", "বাংলা", "Bengali"),
    _entry("Blackfoot (Siksika / Pikanii)", "bla", "Blackfoot", aliases=("Blackfoot", "Siksika", "Pikanii"), community_review="Regional source confirmation present — community review still required", vitality_context="Regional Indigenous-language source set — do not infer vitality or permission from this record", colloquial_status="A source-confirmed regional greeting example is available; no slang is bundled"),
    _entry("Bosnian", "bs", "Bosanski"), _entry("Bulgarian", "bg", "Български", "Cyrillic"),
    _entry("Burmese", "my", "မြန်မာ", "Myanmar"), _entry("Catalan", "ca", "Català"),
    _entry("Cebuano", "ceb", "Cebuano"), _entry("Chinese", "zh", "中文", "Han"),
    _entry("Croatian", "hr", "Hrvatski"), _entry("Czech", "cs", "Čeština"),
    _entry("Danish", "da", "Dansk"), _entry("Diné Bizaad (Navajo)", "nv", "Diné Bizaad", "Latin", aliases=("Navajo", "Dine Bizaad", "Diné Bizaad"), community_review="Navajo Nation / community review required", vitality_context="Community-governed language — do not infer vitality from technical readiness"), _entry("Dutch", "nl", "Nederlands"),
    _entry("Estonian", "et", "Eesti"), _entry("Filipino", "fil", "Filipino"),
    _entry("Finnish", "fi", "Suomi"), _entry("Fula", "ff", "Fulfulde"),
    _entry("Galician", "gl", "Galego"), _entry("Georgian", "ka", "ქართული", "Georgian"),
    _entry("German", "de", "Deutsch"), _entry("Greek", "el", "Ελληνικά", "Greek"),
    _entry("Gujarati", "gu", "ગુજરાતી", "Gujarati"), _entry("Haida (Northern dialect)", "hai", "Haida", aliases=("Haida", "Northern Haida"), community_review="Dialect-labelled source confirmation present — community review still required", vitality_context="Regional Indigenous-language source set — do not infer vitality or permission from this record", colloquial_status="A source-confirmed regional greeting example is available; no slang is bundled"), _entry("Hausa", "ha", "Hausa"), _entry("Hawaiian", "haw", "ʻŌlelo Hawaiʻi", "Latin", aliases=("Olelo Hawaii",), vitality_context="Community revitalisation context — authoritative community source required"),
    _entry("Hebrew", "he", "עברית", "Hebrew"), _entry("Hindi", "hi", "हिन्दी", "Devanagari"),
    _entry("Hungarian", "hu", "Magyar"), _entry("Icelandic", "is", "Íslenska"),
    _entry("Igbo", "ig", "Igbo"), _entry("Indonesian", "id", "Bahasa Indonesia"), _entry("Inuktitut", "iu", "ᐃᓄᒃᑎᑐᑦ", "Canadian Aboriginal Syllabics", community_review="Dialect-labelled source confirmation present — community review still required", vitality_context="Community vitality context varies by region — authoritative community source required", colloquial_status="A source-confirmed North Baffin example is available; no slang is bundled"),
    _entry("Irish", "ga", "Gaeilge"), _entry("Italian", "it", "Italiano"),
    _entry("Japanese", "ja", "日本語", "Kana / Han"), _entry("Javanese", "jv", "Basa Jawa"),
    _entry("Kannada", "kn", "ಕನ್ನಡ", "Kannada"), _entry("Kazakh", "kk", "Қазақ тілі", "Cyrillic"),
    _entry("Khmer", "km", "ខ្មែរ", "Khmer"), _entry("Korean", "ko", "한국어", "Hangul"),
    _entry("Kurdish", "ku", "Kurdî"), _entry("Lao", "lo", "ລາວ", "Lao"),
    _entry("Latvian", "lv", "Latviešu"), _entry("Lingala", "ln", "Lingála"),
    _entry("Lithuanian", "lt", "Lietuvių"), _entry("Luxembourgish", "lb", "Lëtzebuergesch"),
    _entry("Macedonian", "mk", "Македонски", "Cyrillic"), _entry("Malay", "ms", "Bahasa Melayu"),
    _entry("Malayalam", "ml", "മലയാളം", "Malayalam"), _entry("Maltese", "mt", "Malti"), _entry("Manx", "gv", "Gaelg", "Latin", community_review="Source confirmation present — community review still required", vitality_context="Community revitalisation context — authoritative community source required", colloquial_status="A source-confirmed learning expression is available; no slang is bundled"),
    _entry("Mandarin Chinese", "cmn", "普通话", "Han"), _entry("Maori", "mi", "Te Reo Māori"),
    _entry("Marathi", "mr", "मराठी", "Devanagari"), _entry("Mongolian", "mn", "Монгол", "Cyrillic"),
    _entry("Nepali", "ne", "नेपाली", "Devanagari"), _entry("Norwegian", "no", "Norsk"),
    _entry("Odia", "or", "ଓଡ଼ିଆ", "Odia"), _entry("Oneida", "one", "Oneida", community_review="Regional source confirmation present — community review still required", vitality_context="Regional Indigenous-language source set — do not infer vitality or permission from this record", colloquial_status="A source-confirmed regional greeting example is available; no slang is bundled"), _entry("Oromo", "om", "Afaan Oromoo"),
    _entry("Pashto", "ps", "پښتو", "Arabic"), _entry("Persian", "fa", "فارسی", "Arabic"),
    _entry("Polish", "pl", "Polski"), _entry("Portuguese", "pt", "Português"),
    _entry("Punjabi", "pa", "ਪੰਜਾਬੀ", "Gurmukhi"), _entry("Quechua", "qu", "Runa Simi"),
    _entry("Romanian", "ro", "Română"), _entry("Russian", "ru", "Русский", "Cyrillic"),
    _entry("Samoan", "sm", "Gagana Samoa"), _entry("Serbian", "sr", "Српски", "Cyrillic / Latin"),
    _entry("Shona", "sn", "ChiShona"), _entry("Sindhi", "sd", "سنڌي", "Arabic"),
    _entry("Sinhala", "si", "සිංහල", "Sinhala"), _entry("Slovak", "sk", "Slovenčina"),
    _entry("Slovenian", "sl", "Slovenščina"), _entry("Somali", "so", "Soomaali"),
    _entry("Spanish", "es", "Español"), _entry("Sundanese", "su", "Basa Sunda"),
    _entry("Swedish", "sv", "Svenska"), _entry("Tajik", "tg", "Тоҷикӣ", "Cyrillic"),
    _entry("Tamil", "ta", "தமிழ்", "Tamil"), _entry("Telugu", "te", "తెలుగు", "Telugu"),
    _entry("Thai", "th", "ไทย", "Thai"), _entry("Tigrinya", "ti", "ትግርኛ", "Ethiopic"),
    _entry("Turkish", "tr", "Türkçe"), _entry("Ukrainian", "uk", "Українська", "Cyrillic"),
    _entry("Urdu", "ur", "اردو", "Arabic"), _entry("Uzbek", "uz", "Oʻzbekcha"),
    _entry("Vietnamese", "vi", "Tiếng Việt"), _entry("Welsh", "cy", "Cymraeg"),
    _entry("Wolof", "wo", "Wolof"), _entry("Xhosa", "xh", "isiXhosa"),
    _entry("Yoruba", "yo", "Yorùbá"), _entry("Yuchi", "yuc", "Tsoyaha", "Latin", vitality_context="Community revitalisation context — authoritative community source required"), _entry("Zulu", "zu", "isiZulu"),
)


def parse_iso6393_table(table_text: str, *, max_entries: int = 8000) -> list[LanguageEntry]:
    """Parse a user-selected ISO 639-3 tab-separated table locally.

    The official source table is neither bundled nor uploaded.  Imported rows only
    identify a language code and reference name; they do not claim language-pack,
    vitality, community-review, or colloquial-content coverage.
    """
    reader = csv.DictReader(StringIO(str(table_text)), delimiter="\t")
    if not reader.fieldnames or not {"Id", "Ref_Name"}.issubset(set(reader.fieldnames)):
        raise ValueError("Choose a tab-separated ISO 639-3 table containing Id and Ref_Name columns.")
    known_codes = {_normalise(entry.code) for entry in LANGUAGE_CATALOGUE}
    imported: list[LanguageEntry] = []
    for row in reader:
        code = str(row.get("Id", "")).strip().lower()
        name = str(row.get("Ref_Name", "")).strip()
        if len(code) != 3 or not code.isalpha() or not name or code in known_codes:
            continue
        known_codes.add(code)
        imported.append(LanguageEntry(
            name=name,
            code=code,
            native_label=name,
            script="Unspecified in imported identifier table",
            readiness="language pack or approved provider",
            community_review="No community review is bundled — identifier table only",
            vitality_context="No vitality label is bundled — consult an authoritative community source",
            colloquial_status="No colloquial expressions are bundled",
        ))
        if len(imported) >= max_entries:
            break
    return imported


def serialise_imported_catalogue(entries: Iterable[LanguageEntry]) -> list[dict[str, str]]:
    """Persist only locally selected identifier rows, never the source file itself."""
    return [{"name": entry.name, "code": entry.code, "native_label": entry.native_label} for entry in entries]


def restore_imported_catalogue(records: Iterable[dict[str, str]]) -> list[LanguageEntry]:
    restored: list[LanguageEntry] = []
    existing_codes = {_normalise(entry.code) for entry in LANGUAGE_CATALOGUE}
    for record in records:
        code = str(record.get("code", "")).strip().lower()
        name = str(record.get("name", "")).strip()
        native_label = str(record.get("native_label", name)).strip() or name
        if len(code) != 3 or not code.isalpha() or not name or code in existing_codes:
            continue
        existing_codes.add(code)
        restored.append(LanguageEntry(
            name=name,
            code=code,
            native_label=native_label,
            script="Unspecified in imported identifier table",
            readiness="language pack or approved provider",
            community_review="No community review is bundled — identifier table only",
            vitality_context="No vitality label is bundled — consult an authoritative community source",
            colloquial_status="No colloquial expressions are bundled",
        ))
    return restored


def merged_catalogue(imported_entries: Iterable[LanguageEntry] = ()) -> tuple[LanguageEntry, ...]:
    """Return bundled entries plus locally imported identifiers without duplicates."""
    merged = list(LANGUAGE_CATALOGUE)
    known_codes = {_normalise(entry.code) for entry in merged}
    for entry in imported_entries:
        if _normalise(entry.code) not in known_codes:
            known_codes.add(_normalise(entry.code))
            merged.append(entry)
    return tuple(merged)


def _normalise(value: str) -> str:
    folded = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return " ".join(folded.casefold().split())


def _catalogue(entries: Iterable[LanguageEntry] | None = None) -> tuple[LanguageEntry, ...]:
    return tuple(entries) if entries is not None else LANGUAGE_CATALOGUE


def search_languages(query: str = "", entries: Iterable[LanguageEntry] | None = None) -> list[LanguageEntry]:
    """Return a deterministic local catalogue match; no network request is made."""
    needle = _normalise(query)
    catalogue = _catalogue(entries)
    if not needle:
        return list(catalogue)
    return [entry for entry in catalogue if needle in _normalise(f"{entry.name} {entry.code} {entry.native_label} {entry.script} {' '.join(entry.aliases)}")]


def find_language(value: str, entries: Iterable[LanguageEntry] | None = None) -> LanguageEntry | None:
    needle = _normalise(value)
    for entry in _catalogue(entries):
        if needle in {_normalise(entry.name), _normalise(entry.code), _normalise(entry.native_label), *(_normalise(alias) for alias in entry.aliases)}:
            return entry
    return None


def normalise_favourites(values: Iterable[str], entries: Iterable[LanguageEntry] | None = None) -> list[str]:
    """Keep unique known catalogue names in catalogue order, with the primary languages first."""
    requested = {_normalise(value) for value in values}
    return [entry.name for entry in _catalogue(entries) if _normalise(entry.name) in requested]


def prepare_search_query(query: str, language_name: str, entries: Iterable[LanguageEntry] | None = None) -> dict[str, str | bool]:
    """Prepare a reviewable query without translating it or making an external request."""
    entry = find_language(language_name, entries)
    clean_query = str(query).strip()[:500]
    if not clean_query:
        return {"ready": False, "query": "", "language": language_name, "reason": "Enter a search question first."}
    if entry is None:
        return {"ready": False, "query": clean_query, "language": language_name, "reason": "Choose a language from the local library before preparing research."}
    if entry.name in PRIMARY_LOCAL:
        reason = "Prepared locally in the selected language. A separate approved research provider is still required to retrieve information."
    else:
        reason = "The query remains unchanged. Configure an approved translation, speech, or research provider if this language needs processing beyond the local profile."
    return {"ready": True, "query": clean_query, "language": entry.name, "code": entry.code, "reason": reason}


def create_colloquial_draft(
    language_name: str,
    expression: str,
    regional_context: str,
    source_note: str,
    entries: Iterable[LanguageEntry] | None = None,
) -> dict[str, str]:
    """Validate a private local draft; this neither verifies nor distributes an expression."""
    entry = find_language(language_name, entries)
    clean_expression = str(expression).strip()[:120]
    clean_context = str(regional_context).strip()[:160]
    clean_source = str(source_note).strip()[:240]
    if entry is None:
        raise ValueError("Choose a language from Arthur's local library first.")
    if not clean_expression or not clean_context or not clean_source:
        raise ValueError("Add the expression, regional context, and source or community-review note.")
    return {
        "language": entry.name,
        "expression": clean_expression,
        "regional_context": clean_context,
        "source_note": clean_source,
        "review_status": "Private draft — not community reviewed",
    }


def prepare_colloquial_entry_review(
    language_name: str,
    expression: str,
    meaning: str,
    regional_context: str,
    source_note: str,
    sensitivity_note: str,
    entries: Iterable[LanguageEntry] | None = None,
) -> dict[str, str]:
    """Create an unpublishable review preview for a source-backed colloquial entry.

    It remains local, unverified, and unavailable to voice, translation, search, or
    language-model routing until a separate human/community review process exists.
    """
    draft = create_colloquial_draft(language_name, expression, regional_context, source_note, entries)
    clean_meaning = str(meaning).strip()[:240]
    clean_sensitivity = str(sensitivity_note).strip()[:180]
    if not clean_meaning or not clean_sensitivity:
        raise ValueError("Add a plain-language meaning and sensitivity/context note for review.")
    return {
        **draft,
        "meaning": clean_meaning,
        "sensitivity_note": clean_sensitivity,
        "review_status": "Review preview only — not published or verified",
    }


SOURCE_CONFIRMED_EXPRESSIONS: tuple[dict[str, str], ...] = (
    {
        "language": "Manx",
        "expression": "Aigh vie",
        "meaning": "Good luck",
        "regional_context": "Isle of Man; Learn Manx learner resource",
        "use_context": "Beginner-learning encouragement expression",
        "sensitivity_note": "Use the linked learning source for context. This does not establish universal or colloquial usage.",
        "evidence_kind": "community-language-program",
        "evidence_title": "Learn Manx — 1000 Words",
        "evidence_url": "https://www.learnmanx.com/learning/1000words/",
        "verification_note": "Source checked against a named Isle of Man learning resource; no community-wide endorsement is implied.",
        "review_status": "Source-confirmed — not community-reviewed",
    },
    {
        "language": "Blackfoot (Siksika / Pikanii)",
        "expression": "Oki, tsanitapi?",
        "meaning": "Hello! How are you?",
        "regional_context": "Canada; language label shown as Blackfoot (Siksika / Pikanii) by the source",
        "use_context": "Greeting listed by the source",
        "sensitivity_note": "Keep the source's language label attached; do not generalise this wording across all Blackfoot communities.",
        "evidence_kind": "government-cultural-resource",
        "evidence_title": "Government of Canada — How to say hello in Indigenous languages",
        "evidence_url": "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
        "verification_note": "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
        "review_status": "Source-confirmed — not community-reviewed",
    },
    {
        "language": "Haida (Northern dialect)",
        "expression": "Jáa, gasánuu dáng G̱íidang?",
        "meaning": "Hello! How are you?",
        "regional_context": "Canada; Northern dialect label retained exactly from the source",
        "use_context": "Greeting listed by the source",
        "sensitivity_note": "Dialect label is required. Do not substitute this expression for other Haida dialects or claim a universal greeting.",
        "evidence_kind": "government-cultural-resource",
        "evidence_title": "Government of Canada — How to say hello in Indigenous languages",
        "evidence_url": "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
        "verification_note": "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
        "review_status": "Source-confirmed — not community-reviewed",
    },
    {
        "language": "Inuktitut",
        "expression": "Aingai! Qanuippit",
        "meaning": "Hello! How are you?",
        "regional_context": "Canada; North Baffin, Roman Orthography label retained from the source",
        "use_context": "Greeting listed by the source",
        "sensitivity_note": "The North Baffin and writing-system label is integral; do not treat this as a replacement for other Inuktitut regional varieties.",
        "evidence_kind": "government-cultural-resource",
        "evidence_title": "Government of Canada — How to say hello in Indigenous languages",
        "evidence_url": "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
        "verification_note": "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
        "review_status": "Source-confirmed — not community-reviewed",
    },
    {
        "language": "Oneida",
        "expression": "shekoli ohniyotuháti?",
        "meaning": "Hello! How are you?",
        "regional_context": "Canada; Oneida language label retained from the source",
        "use_context": "Greeting listed by the source",
        "sensitivity_note": "Use only with the linked source and do not infer that a government listing replaces review by Oneida language authorities.",
        "evidence_kind": "government-cultural-resource",
        "evidence_title": "Government of Canada — How to say hello in Indigenous languages",
        "evidence_url": "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
        "verification_note": "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
        "review_status": "Source-confirmed — not community-reviewed",
    },
)


_EVIDENCE_KINDS = {"community-language-program", "government-cultural-resource", "educational-or-archival-resource"}


def source_confirmed_expressions(language_name: str, entries: Iterable[LanguageEntry] | None = None) -> list[dict[str, str]]:
    """Return bundled source-confirmed records for one selected catalogue language.

    These records remain unavailable to automatic speech, translation, response,
    provider routing, or publishing.  The status is intentionally not a substitute
    for community review.
    """
    entry = find_language(language_name, entries)
    if entry is None:
        return []
    return [dict(record) for record in SOURCE_CONFIRMED_EXPRESSIONS if record["language"] == entry.name]


def prepare_source_confirmed_expression(
    language_name: str,
    expression: str,
    meaning: str,
    regional_context: str,
    use_context: str,
    sensitivity_note: str,
    evidence_kind: str,
    evidence_title: str,
    evidence_url: str,
    evidence_reviewed: bool,
    entries: Iterable[LanguageEntry] | None = None,
) -> dict[str, str]:
    """Validate a reviewer-attested source-confirmation record.

    This retains evidence metadata locally; it does not contact the evidence URL,
    publish the expression, or grant community-reviewed status.
    """
    review = prepare_colloquial_entry_review(
        language_name, expression, meaning, regional_context, evidence_title, sensitivity_note, entries
    )
    clean_use_context = str(use_context).strip()[:180]
    clean_title = str(evidence_title).strip()[:180]
    clean_url = str(evidence_url).strip()[:500]
    if not clean_use_context or not clean_title:
        raise ValueError("Add the expression's use context and a named evidence source.")
    if evidence_kind not in _EVIDENCE_KINDS:
        raise ValueError("Choose a recognised community, government, educational, or archival source type.")
    if not clean_url.startswith("https://"):
        raise ValueError("Add a valid HTTPS evidence URL before source confirmation.")
    if not evidence_reviewed:
        raise ValueError("Confirm that a reviewer checked the source, region or dialect, and use context before source confirmation.")
    return {
        "language": review["language"],
        "expression": review["expression"],
        "meaning": review["meaning"],
        "regional_context": review["regional_context"],
        "use_context": clean_use_context,
        "sensitivity_note": review["sensitivity_note"],
        "evidence_kind": evidence_kind,
        "evidence_title": clean_title,
        "evidence_url": clean_url,
        "verification_note": "Reviewer-attested source confirmation only; this is not community review, publication permission, or automatic-use approval.",
        "review_status": "Source-confirmed — not community-reviewed",
    }
