export type LanguageReadiness = "profile-ready" | "pack-or-provider";

export type LanguageEntry = {
  name: string;
  code: string;
  nativeLabel: string;
  script: string;
  readiness: LanguageReadiness;
  aliases: string[];
  communityReview: string;
  vitalityContext: string;
  colloquialStatus: string;
};

export type PrivateColloquialDraft = {
  language: string;
  expression: string;
  regionalContext: string;
  sourceNote: string;
  reviewStatus: "Private draft — not community reviewed";
};

export type ColloquialEntryReview = Omit<PrivateColloquialDraft, "reviewStatus"> & {
  meaning: string;
  sensitivityNote: string;
  reviewStatus: "Review preview only — not published or verified";
};

export type ExpressionEvidenceKind = "community-language-program" | "government-cultural-resource" | "educational-or-archival-resource";

export type SourceConfirmedExpression = {
  language: string;
  expression: string;
  meaning: string;
  regionalContext: string;
  useContext: string;
  sensitivityNote: string;
  evidenceKind: ExpressionEvidenceKind;
  evidenceTitle: string;
  evidenceUrl: string;
  verificationNote: string;
  reviewStatus: "Source-confirmed — not community-reviewed";
};

export type SourceConfirmationInput = Omit<SourceConfirmedExpression, "language" | "reviewStatus" | "verificationNote"> & {
  language: string;
  evidenceReviewed: boolean;
};

export type ImportedLanguageReference = Pick<LanguageEntry, "name" | "code" | "nativeLabel">;

const profileReady = new Set(["English", "Kinyarwanda", "French", "Kiswahili"]);

const rows = `English|en|English|Latin
Kinyarwanda|rw|Ikinyarwanda|Latin
French|fr|Français|Latin
Kiswahili|sw|Kiswahili|Latin
Afrikaans|af|Afrikaans|Latin
Ainu|ain|アイヌ・イタㇰ|Kana / Latin
Albanian|sq|Shqip|Latin
Amharic|am|አማርኛ|Ethiopic
Arabic|ar|العربية|Arabic
Armenian|hy|Հայերեն|Armenian
Azerbaijani|az|Azərbaycanca|Latin
Bambara|bm|Bamanankan|Latin
Basque|eu|Euskara|Latin
Belarusian|be|Беларуская|Cyrillic
Bengali|bn|বাংলা|Bengali
Blackfoot (Siksika / Pikanii)|bla|Blackfoot|Latin
Bosnian|bs|Bosanski|Latin
Bulgarian|bg|Български|Cyrillic
Burmese|my|မြန်မာ|Myanmar
Catalan|ca|Català|Latin
Cebuano|ceb|Cebuano|Latin
Chinese|zh|中文|Han
Croatian|hr|Hrvatski|Latin
Czech|cs|Čeština|Latin
Danish|da|Dansk|Latin
Diné Bizaad (Navajo)|nv|Diné Bizaad|Latin
Dutch|nl|Nederlands|Latin
Estonian|et|Eesti|Latin
Filipino|fil|Filipino|Latin
Finnish|fi|Suomi|Latin
Fula|ff|Fulfulde|Latin
Galician|gl|Galego|Latin
Georgian|ka|ქართული|Georgian
German|de|Deutsch|Latin
Greek|el|Ελληνικά|Greek
Gujarati|gu|ગુજરાતી|Gujarati
Haida (Northern dialect)|hai|Haida|Latin
Hausa|ha|Hausa|Latin
Hawaiian|haw|ʻŌlelo Hawaiʻi|Latin
Hebrew|he|עברית|Hebrew
Hindi|hi|हिन्दी|Devanagari
Hungarian|hu|Magyar|Latin
Icelandic|is|Íslenska|Latin
Igbo|ig|Igbo|Latin
Indonesian|id|Bahasa Indonesia|Latin
Inuktitut|iu|ᐃᓄᒃᑎᑐᑦ|Canadian Aboriginal Syllabics
Irish|ga|Gaeilge|Latin
Italian|it|Italiano|Latin
Japanese|ja|日本語|Kana / Han
Javanese|jv|Basa Jawa|Latin
Kannada|kn|ಕನ್ನಡ|Kannada
Kazakh|kk|Қазақ тілі|Cyrillic
Khmer|km|ខ្មែរ|Khmer
Korean|ko|한국어|Hangul
Kurdish|ku|Kurdî|Latin
Lao|lo|ລາວ|Lao
Latvian|lv|Latviešu|Latin
Lingala|ln|Lingála|Latin
Lithuanian|lt|Lietuvių|Latin
Malay|ms|Bahasa Melayu|Latin
Malayalam|ml|മലയാളം|Malayalam
Maltese|mt|Malti|Latin
Manx|gv|Gaelg|Latin
Maori|mi|Te Reo Māori|Latin
Marathi|mr|मराठी|Devanagari
Mongolian|mn|Монгол|Cyrillic
Nepali|ne|नेपाली|Devanagari
Norwegian|no|Norsk|Latin
Odia|or|ଓଡ଼ିଆ|Odia
Oneida|one|Oneida|Latin
Oromo|om|Afaan Oromoo|Latin
Pashto|ps|پښتو|Arabic
Persian|fa|فارسی|Arabic
Polish|pl|Polski|Latin
Portuguese|pt|Português|Latin
Punjabi|pa|ਪੰਜਾਬੀ|Gurmukhi
Quechua|qu|Runa Simi|Latin
Romanian|ro|Română|Latin
Russian|ru|Русский|Cyrillic
Samoan|sm|Gagana Samoa|Latin
Serbian|sr|Српски|Cyrillic / Latin
Shona|sn|ChiShona|Latin
Sindhi|sd|سنڌي|Arabic
Sinhala|si|සිංහල|Sinhala
Slovak|sk|Slovenčina|Latin
Slovenian|sl|Slovenščina|Latin
Somali|so|Soomaali|Latin
Spanish|es|Español|Latin
Sundanese|su|Basa Sunda|Latin
Swedish|sv|Svenska|Latin
Tajik|tg|Тоҷикӣ|Cyrillic
Tamil|ta|தமிழ்|Tamil
Telugu|te|తెలుగు|Telugu
Thai|th|ไทย|Thai
Tigrinya|ti|ትግርኛ|Ethiopic
Turkish|tr|Türkçe|Latin
Ukrainian|uk|Українська|Cyrillic
Urdu|ur|اردو|Arabic
Uzbek|uz|Oʻzbekcha|Latin
Vietnamese|vi|Tiếng Việt|Latin
Welsh|cy|Cymraeg|Latin
Wolof|wo|Wolof|Latin
Xhosa|xh|isiXhosa|Latin
Yoruba|yo|Yorùbá|Latin
Yuchi|yuc|Tsoyaha|Latin
Zulu|zu|isiZulu|Latin`;

const languageMetadata: Record<string, Pick<LanguageEntry, "aliases" | "communityReview" | "vitalityContext" | "colloquialStatus">> = {
  "Diné Bizaad (Navajo)": {
    aliases: ["Navajo", "Dine Bizaad", "Diné Bizaad"],
    communityReview: "Navajo Nation / community review required",
    vitalityContext: "Community-governed language — do not infer vitality from technical readiness",
    colloquialStatus: "No colloquial expressions are bundled",
  },
  Ainu: { aliases: [], communityReview: "Authoritative community source required", vitalityContext: "Community revitalisation context — authoritative community source required", colloquialStatus: "No colloquial expressions are bundled" },
  Hawaiian: { aliases: ["Olelo Hawaii"], communityReview: "Authoritative community source required", vitalityContext: "Community revitalisation context — authoritative community source required", colloquialStatus: "No colloquial expressions are bundled" },
  "Blackfoot (Siksika / Pikanii)": { aliases: ["Blackfoot", "Siksika", "Pikanii"], communityReview: "Regional source confirmation present — community review still required", vitalityContext: "Regional Indigenous-language source set — do not infer vitality or permission from this record", colloquialStatus: "A source-confirmed regional greeting example is available; no slang is bundled" },
  "Haida (Northern dialect)": { aliases: ["Haida", "Northern Haida"], communityReview: "Dialect-labelled source confirmation present — community review still required", vitalityContext: "Regional Indigenous-language source set — do not infer vitality or permission from this record", colloquialStatus: "A source-confirmed regional greeting example is available; no slang is bundled" },
  Inuktitut: { aliases: [], communityReview: "Dialect-labelled source confirmation present — community review still required", vitalityContext: "Community vitality context varies by region — authoritative community source required", colloquialStatus: "A source-confirmed North Baffin example is available; no slang is bundled" },
  Manx: { aliases: [], communityReview: "Source confirmation present — community review still required", vitalityContext: "Community revitalisation context — authoritative community source required", colloquialStatus: "A source-confirmed learning expression is available; no slang is bundled" },
  Oneida: { aliases: [], communityReview: "Regional source confirmation present — community review still required", vitalityContext: "Regional Indigenous-language source set — do not infer vitality or permission from this record", colloquialStatus: "A source-confirmed regional greeting example is available; no slang is bundled" },
  Yuchi: { aliases: [], communityReview: "Authoritative community source required", vitalityContext: "Community revitalisation context — authoritative community source required", colloquialStatus: "No colloquial expressions are bundled" },
};

const defaultMetadata: Pick<LanguageEntry, "aliases" | "communityReview" | "vitalityContext" | "colloquialStatus"> = {
  aliases: [],
  communityReview: "No community review is bundled",
  vitalityContext: "No vitality label is bundled",
  colloquialStatus: "No colloquial expressions are bundled",
};

export const languageLibrary: LanguageEntry[] = rows.split("\n").map((row) => {
  const [name, code, nativeLabel, script] = row.split("|");
  return { name, code, nativeLabel, script, readiness: profileReady.has(name) ? "profile-ready" : "pack-or-provider", ...(languageMetadata[name] ?? defaultMetadata) };
});

const normalise = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase().trim();

export const sourceConfirmedExpressions: SourceConfirmedExpression[] = [
  {
    language: "Manx",
    expression: "Aigh vie",
    meaning: "Good luck",
    regionalContext: "Isle of Man; Learn Manx learner resource",
    useContext: "Beginner-learning encouragement expression",
    sensitivityNote: "Use the linked learning source for context. This does not establish universal or colloquial usage.",
    evidenceKind: "community-language-program",
    evidenceTitle: "Learn Manx — 1000 Words",
    evidenceUrl: "https://www.learnmanx.com/learning/1000words/",
    verificationNote: "Source checked against a named Isle of Man learning resource; no community-wide endorsement is implied.",
    reviewStatus: "Source-confirmed — not community-reviewed",
  },
  {
    language: "Blackfoot (Siksika / Pikanii)",
    expression: "Oki, tsanitapi?",
    meaning: "Hello! How are you?",
    regionalContext: "Canada; language label shown as Blackfoot (Siksika / Pikanii) by the source",
    useContext: "Greeting listed by the source",
    sensitivityNote: "Keep the source's language label attached; do not generalise this wording across all Blackfoot communities.",
    evidenceKind: "government-cultural-resource",
    evidenceTitle: "Government of Canada — How to say hello in Indigenous languages",
    evidenceUrl: "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
    verificationNote: "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
    reviewStatus: "Source-confirmed — not community-reviewed",
  },
  {
    language: "Haida (Northern dialect)",
    expression: "Jáa, gasánuu dáng G̱íidang?",
    meaning: "Hello! How are you?",
    regionalContext: "Canada; Northern dialect label retained exactly from the source",
    useContext: "Greeting listed by the source",
    sensitivityNote: "Dialect label is required. Do not substitute this expression for other Haida dialects or claim a universal greeting.",
    evidenceKind: "government-cultural-resource",
    evidenceTitle: "Government of Canada — How to say hello in Indigenous languages",
    evidenceUrl: "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
    verificationNote: "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
    reviewStatus: "Source-confirmed — not community-reviewed",
  },
  {
    language: "Inuktitut",
    expression: "Aingai! Qanuippit",
    meaning: "Hello! How are you?",
    regionalContext: "Canada; North Baffin, Roman Orthography label retained from the source",
    useContext: "Greeting listed by the source",
    sensitivityNote: "The North Baffin and writing-system label is integral; do not treat this as a replacement for other Inuktitut regional varieties.",
    evidenceKind: "government-cultural-resource",
    evidenceTitle: "Government of Canada — How to say hello in Indigenous languages",
    evidenceUrl: "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
    verificationNote: "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
    reviewStatus: "Source-confirmed — not community-reviewed",
  },
  {
    language: "Oneida",
    expression: "shekoli ohniyotuháti?",
    meaning: "Hello! How are you?",
    regionalContext: "Canada; Oneida language label retained from the source",
    useContext: "Greeting listed by the source",
    sensitivityNote: "Use only with the linked source and do not infer that a government listing replaces review by Oneida language authorities.",
    evidenceKind: "government-cultural-resource",
    evidenceTitle: "Government of Canada — How to say hello in Indigenous languages",
    evidenceUrl: "https://www.canada.ca/en/canadian-heritage/campaigns/canada-day/say-hello.html",
    verificationNote: "Source checked against a named government cultural resource; no community-wide endorsement is implied.",
    reviewStatus: "Source-confirmed — not community-reviewed",
  },
];

const evidenceKinds = new Set<ExpressionEvidenceKind>(["community-language-program", "government-cultural-resource", "educational-or-archival-resource"]);

export function mergeImportedLanguageReferences(references: ImportedLanguageReference[]): LanguageEntry[] {
  const knownCodes = new Set(languageLibrary.map((entry) => normalise(entry.code)));
  const imported = references.flatMap((reference) => {
    const code = reference.code.trim().toLowerCase();
    const name = reference.name.trim();
    const nativeLabel = reference.nativeLabel.trim() || name;
    if (!/^[a-z]{3}$/.test(code) || !name || knownCodes.has(normalise(code))) return [];
    knownCodes.add(normalise(code));
    return [{
      name,
      code,
      nativeLabel,
      script: "Unspecified in imported identifier table",
      readiness: "pack-or-provider" as const,
      aliases: [],
      communityReview: "No community review is bundled — identifier table only",
      vitalityContext: "No vitality label is bundled — consult an authoritative community source",
      colloquialStatus: "No colloquial expressions are bundled",
    }];
  });
  return [...languageLibrary, ...imported];
}

export function parseIso6393Table(tableText: string, maxEntries = 8000): ImportedLanguageReference[] {
  const lines = tableText.replace(/^\uFEFF/, "").split(/\r?\n/).filter(Boolean);
  const header = lines.shift()?.split("\t") ?? [];
  const idIndex = header.indexOf("Id");
  const nameIndex = header.indexOf("Ref_Name");
  if (idIndex < 0 || nameIndex < 0) throw new Error("Choose a tab-separated ISO 639-3 table containing Id and Ref_Name columns.");
  const knownCodes = new Set(languageLibrary.map((entry) => normalise(entry.code)));
  const results: ImportedLanguageReference[] = [];
  for (const line of lines) {
    const cells = line.split("\t");
    const code = (cells[idIndex] ?? "").trim().toLowerCase();
    const name = (cells[nameIndex] ?? "").trim();
    if (!/^[a-z]{3}$/.test(code) || !name || knownCodes.has(normalise(code))) continue;
    knownCodes.add(normalise(code));
    results.push({ name, code, nativeLabel: name });
    if (results.length >= maxEntries) break;
  }
  return results;
}

export function filterLanguages(query = "", catalogue: LanguageEntry[] = languageLibrary): LanguageEntry[] {
  const needle = normalise(query);
  return !needle ? catalogue : catalogue.filter((entry) => normalise(`${entry.name} ${entry.code} ${entry.nativeLabel} ${entry.script} ${entry.aliases.join(" ")}`).includes(needle));
}

export function findLanguage(value: string, catalogue: LanguageEntry[] = languageLibrary): LanguageEntry | undefined {
  const needle = normalise(value);
  return catalogue.find((entry) => [entry.name, entry.code, entry.nativeLabel, ...entry.aliases].some((candidate) => normalise(candidate) === needle));
}

export function languageFromPreferenceRequest(request: string): LanguageEntry | undefined {
  const normalisedRequest = normalise(request);
  if (!/(speak|talk|reply|parle|vuga|ongea|sema)/.test(normalisedRequest)) return undefined;
  return languageLibrary.find((entry) => [entry.name, entry.nativeLabel, ...entry.aliases].some((candidate) => normalisedRequest.includes(normalise(candidate))));
}

export function prepareMultilingualSearch(query: string, selectedLanguage: string, catalogue: LanguageEntry[] = languageLibrary) {
  const language = findLanguage(selectedLanguage, catalogue);
  const cleanQuery = query.trim().slice(0, 500);
  if (!cleanQuery) return { ready: false, query: "", reason: "Enter a question before preparing research." };
  if (!language) return { ready: false, query: cleanQuery, reason: "Select a language from Arthur’s local library first." };
  return {
    ready: true,
    query: cleanQuery,
    language,
    reason: language.readiness === "profile-ready"
      ? "The question is prepared unchanged in the selected language. A separate approved research provider is still required to retrieve information."
      : "The question remains unchanged. Configure an approved local language pack or provider before speech, translation, or research in this language can be performed.",
  };
}

export function createPrivateColloquialDraft(languageName: string, expression: string, regionalContext: string, sourceNote: string, catalogue: LanguageEntry[] = languageLibrary): PrivateColloquialDraft {
  const language = findLanguage(languageName, catalogue);
  const cleanExpression = expression.trim().slice(0, 120);
  const cleanContext = regionalContext.trim().slice(0, 160);
  const cleanSource = sourceNote.trim().slice(0, 240);
  if (!language) throw new Error("Choose a language from the local library first.");
  if (!cleanExpression || !cleanContext || !cleanSource) throw new Error("Add the expression, regional context, and source or community-review note.");
  return { language: language.name, expression: cleanExpression, regionalContext: cleanContext, sourceNote: cleanSource, reviewStatus: "Private draft — not community reviewed" };
}

export function prepareColloquialEntryReview(
  languageName: string,
  expression: string,
  meaning: string,
  regionalContext: string,
  sourceNote: string,
  sensitivityNote: string,
  catalogue: LanguageEntry[] = languageLibrary,
): ColloquialEntryReview {
  const draft = createPrivateColloquialDraft(languageName, expression, regionalContext, sourceNote, catalogue);
  const cleanMeaning = meaning.trim().slice(0, 240);
  const cleanSensitivity = sensitivityNote.trim().slice(0, 180);
  if (!cleanMeaning || !cleanSensitivity) throw new Error("Add a plain-language meaning and sensitivity/context note for review.");
  return { ...draft, meaning: cleanMeaning, sensitivityNote: cleanSensitivity, reviewStatus: "Review preview only — not published or verified" };
}

export function getSourceConfirmedExpressions(languageName: string, catalogue: LanguageEntry[] = languageLibrary): SourceConfirmedExpression[] {
  const language = findLanguage(languageName, catalogue);
  return language ? sourceConfirmedExpressions.filter((record) => record.language === language.name) : [];
}

export function prepareSourceConfirmedExpression(input: SourceConfirmationInput, catalogue: LanguageEntry[] = languageLibrary): SourceConfirmedExpression {
  const review = prepareColloquialEntryReview(
    input.language,
    input.expression,
    input.meaning,
    input.regionalContext,
    input.evidenceTitle,
    input.sensitivityNote,
    catalogue,
  );
  const useContext = input.useContext.trim().slice(0, 180);
  const evidenceTitle = input.evidenceTitle.trim().slice(0, 180);
  const evidenceUrl = input.evidenceUrl.trim().slice(0, 500);
  if (!useContext || !evidenceTitle) throw new Error("Add the expression's use context and a named evidence source.");
  if (!evidenceKinds.has(input.evidenceKind)) throw new Error("Choose a recognised community, government, educational, or archival source type.");
  try {
    const url = new URL(evidenceUrl);
    if (url.protocol !== "https:") throw new Error("Use an HTTPS evidence URL.");
  } catch {
    throw new Error("Add a valid HTTPS evidence URL before source confirmation.");
  }
  if (!input.evidenceReviewed) throw new Error("Confirm that a reviewer checked the source, region or dialect, and use context before source confirmation.");
  return {
    language: review.language,
    expression: review.expression,
    meaning: review.meaning,
    regionalContext: review.regionalContext,
    useContext,
    sensitivityNote: review.sensitivityNote,
    evidenceKind: input.evidenceKind,
    evidenceTitle,
    evidenceUrl,
    verificationNote: "Reviewer-attested source confirmation only; this is not community review, publication permission, or automatic-use approval.",
    reviewStatus: "Source-confirmed — not community-reviewed",
  };
}
