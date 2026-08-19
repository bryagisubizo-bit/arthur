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
  Inuktitut: { aliases: [], communityReview: "Authoritative community source required", vitalityContext: "Community vitality context varies by region — authoritative community source required", colloquialStatus: "No colloquial expressions are bundled" },
  Manx: { aliases: [], communityReview: "Authoritative community source required", vitalityContext: "Community revitalisation context — authoritative community source required", colloquialStatus: "No colloquial expressions are bundled" },
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

export function filterLanguages(query = ""): LanguageEntry[] {
  const needle = normalise(query);
  return !needle ? languageLibrary : languageLibrary.filter((entry) => normalise(`${entry.name} ${entry.code} ${entry.nativeLabel} ${entry.script} ${entry.aliases.join(" ")}`).includes(needle));
}

export function findLanguage(value: string): LanguageEntry | undefined {
  const needle = normalise(value);
  return languageLibrary.find((entry) => [entry.name, entry.code, entry.nativeLabel, ...entry.aliases].some((candidate) => normalise(candidate) === needle));
}

export function languageFromPreferenceRequest(request: string): LanguageEntry | undefined {
  const normalisedRequest = normalise(request);
  if (!/(speak|talk|reply|parle|vuga|ongea|sema)/.test(normalisedRequest)) return undefined;
  return languageLibrary.find((entry) => [entry.name, entry.nativeLabel, ...entry.aliases].some((candidate) => normalisedRequest.includes(normalise(candidate))));
}

export function prepareMultilingualSearch(query: string, selectedLanguage: string) {
  const language = findLanguage(selectedLanguage);
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

export function createPrivateColloquialDraft(languageName: string, expression: string, regionalContext: string, sourceNote: string): PrivateColloquialDraft {
  const language = findLanguage(languageName);
  const cleanExpression = expression.trim().slice(0, 120);
  const cleanContext = regionalContext.trim().slice(0, 160);
  const cleanSource = sourceNote.trim().slice(0, 240);
  if (!language) throw new Error("Choose a language from the local library first.");
  if (!cleanExpression || !cleanContext || !cleanSource) throw new Error("Add the expression, regional context, and source or community-review note.");
  return { language: language.name, expression: cleanExpression, regionalContext: cleanContext, sourceNote: cleanSource, reviewStatus: "Private draft — not community reviewed" };
}
