export type LanguageReadiness = "profile-ready" | "pack-or-provider";

export type LanguageEntry = {
  name: string;
  code: string;
  nativeLabel: string;
  script: string;
  readiness: LanguageReadiness;
};

const profileReady = new Set(["English", "Kinyarwanda", "French", "Kiswahili"]);

const rows = `English|en|English|Latin
Kinyarwanda|rw|Ikinyarwanda|Latin
French|fr|Français|Latin
Kiswahili|sw|Kiswahili|Latin
Afrikaans|af|Afrikaans|Latin
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
Hebrew|he|עברית|Hebrew
Hindi|hi|हिन्दी|Devanagari
Hungarian|hu|Magyar|Latin
Icelandic|is|Íslenska|Latin
Igbo|ig|Igbo|Latin
Indonesian|id|Bahasa Indonesia|Latin
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
Zulu|zu|isiZulu|Latin`;

export const languageLibrary: LanguageEntry[] = rows.split("\n").map((row) => {
  const [name, code, nativeLabel, script] = row.split("|");
  return { name, code, nativeLabel, script, readiness: profileReady.has(name) ? "profile-ready" : "pack-or-provider" };
});

const normalise = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase().trim();

export function filterLanguages(query = ""): LanguageEntry[] {
  const needle = normalise(query);
  return !needle ? languageLibrary : languageLibrary.filter((entry) => normalise(`${entry.name} ${entry.code} ${entry.nativeLabel} ${entry.script}`).includes(needle));
}

export function findLanguage(value: string): LanguageEntry | undefined {
  const needle = normalise(value);
  return languageLibrary.find((entry) => [entry.name, entry.code, entry.nativeLabel].some((candidate) => normalise(candidate) === needle));
}

export function languageFromPreferenceRequest(request: string): LanguageEntry | undefined {
  const normalisedRequest = normalise(request);
  if (!/(speak|talk|reply|parle|vuga|ongea|sema)/.test(normalisedRequest)) return undefined;
  return languageLibrary.find((entry) => normalisedRequest.includes(normalise(entry.name)) || normalisedRequest.includes(normalise(entry.nativeLabel)));
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
