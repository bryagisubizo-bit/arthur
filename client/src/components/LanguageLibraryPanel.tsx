import { useMemo, useState } from "react";
import { Check, Copy, FileText, Globe2, Languages, Search, Star } from "lucide-react";
import { toast } from "sonner";
import { createPrivateColloquialDraft, filterLanguages, prepareMultilingualSearch, type LanguageEntry, type PrivateColloquialDraft } from "@/lib/languageLibrary";
import "./language-library.css";

type Props = {
  activeLanguage: string;
  setActiveLanguage: (language: string) => void;
};

const defaultFavourites = ["English", "Kinyarwanda", "French", "Kiswahili"];

export default function LanguageLibraryPanel({ activeLanguage, setActiveLanguage }: Props) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<LanguageEntry>(() => filterLanguages("").find((entry) => entry.name === activeLanguage) ?? filterLanguages("")[0]);
  const [favourites, setFavourites] = useState(defaultFavourites);
  const [researchQuestion, setResearchQuestion] = useState("");
  const [prepared, setPrepared] = useState<ReturnType<typeof prepareMultilingualSearch> | null>(null);
  const [expression, setExpression] = useState("");
  const [regionalContext, setRegionalContext] = useState("");
  const [sourceNote, setSourceNote] = useState("");
  const [privateDrafts, setPrivateDrafts] = useState<PrivateColloquialDraft[]>([]);
  const matches = useMemo(() => filterLanguages(query), [query]);
  const selectedFavourite = favourites.includes(selected.name);

  const chooseLanguage = (entry: LanguageEntry) => {
    setSelected(entry);
    setActiveLanguage(entry.name);
    setPrepared(null);
    toast.success(`${entry.name} selected`, { description: entry.readiness === "profile-ready" ? "Arthur can keep this as a local language preference." : "Choose an approved local pack or provider later if speech, translation, or research needs it." });
  };

  const toggleFavourite = () => {
    setFavourites((current) => selectedFavourite ? current.filter((name) => name !== selected.name) : [...current, selected.name]);
  };

  const prepare = () => setPrepared(prepareMultilingualSearch(researchQuestion, activeLanguage));

  const savePrivateDraft = () => {
    try {
      const draft = createPrivateColloquialDraft(selected.name, expression, regionalContext, sourceNote);
      setPrivateDrafts((current) => [...current, draft].slice(-40));
      setExpression(""); setRegionalContext(""); setSourceNote("");
      toast.success("Private local draft saved", { description: "It is not community reviewed and will not be used for speech, translation, search, or replies automatically." });
    } catch (error) {
      toast.error("Private draft needs context", { description: error instanceof Error ? error.message : "Add a language, expression, regional context, and source note." });
    }
  };

  const copyPrepared = async () => {
    if (!prepared?.ready) return;
    try {
      await navigator.clipboard.writeText(prepared.query);
      toast.success("Prepared query copied", { description: "Nothing has been sent to a search, translation, or speech provider." });
    } catch {
      toast.error("Copy was unavailable", { description: "Select the prepared text manually. Arthur has not sent it anywhere." });
    }
  };

  return <section className="language-library" aria-label="Arthur language library">
    <header className="language-library-hero"><div><span className="eyebrow">Language library / local catalogue</span><h2>Choose the language before Arthur chooses a route.</h2><p>This bundled catalogue helps you find language names, ISO codes, native labels, and writing systems. Selection is local: it never downloads a pack, turns on the microphone, translates your text, or begins a web search.</p></div><div className="language-library-seal"><Languages size={24} /><b>{filterLanguages("").length}</b><span>catalogued<br/>languages</span></div></header>

    <div className="language-library-grid">
      <section className="language-browser-panel"><div className="language-panel-heading"><div><span className="eyebrow">Discover</span><h3>Search the local library</h3></div><span>{matches.length} matches</span></div><label className="language-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, ISO code, native label, or script" /></label><div className="language-match-list" role="listbox" aria-label="Language matches">{matches.map((entry) => <button key={entry.code} className={`language-match ${selected.code === entry.code ? "selected" : ""}`} onClick={() => setSelected(entry)} role="option" aria-selected={selected.code === entry.code}><span><b>{entry.name}</b><small>{entry.nativeLabel} · {entry.code.toUpperCase()}</small></span><em>{entry.readiness === "profile-ready" ? "profile ready" : "pack / provider"}</em></button>)}</div></section>

      <section className="language-detail-panel"><div className="language-panel-heading"><div><span className="eyebrow">Selected language</span><h3>{selected.name}</h3></div><Globe2 size={20} /></div><p className="language-native">{selected.nativeLabel}</p><dl><div><dt>ISO code</dt><dd>{selected.code.toUpperCase()}</dd></div><div><dt>Writing system</dt><dd>{selected.script}</dd></div><div><dt>Readiness</dt><dd>{selected.readiness === "profile-ready" ? "Local profile preference" : "Language pack or approved provider"}</dd></div><div><dt>Community review</dt><dd>{selected.communityReview}</dd></div><div><dt>Vitality context</dt><dd>{selected.vitalityContext}</dd></div><div><dt>Colloquial content</dt><dd>{selected.colloquialStatus}</dd></div></dl><p className="language-boundary">{selected.readiness === "profile-ready" ? "Arthur can retain this as your current language preference. Actual speech and research still follow their own explicit permissions." : "This entry is available for selection and query preparation. Install a local pack or connect and approve a provider separately before Arthur attempts speech, translation, or research in it."}</p><div className="language-actions"><button className="primary-button compact" onClick={() => chooseLanguage(selected)}><Check size={15} /> Use for conversation</button><button className="outline-button" onClick={toggleFavourite}><Star size={15} /> {selectedFavourite ? "Remove favourite" : "Add favourite"}</button></div><div className="language-favourites"><span>Favourites</span>{favourites.map((name) => <button key={name} onClick={() => { const entry = filterLanguages("").find((item) => item.name === name); if (entry) chooseLanguage(entry); }}>{name}</button>)}</div></section>
    </div>

    <section className="community-language-review"><div className="language-panel-heading"><div><span className="eyebrow">Community context / private drafts</span><h3>Do not make slang a stereotype.</h3></div><FileText size={20} /></div><p>Arthur includes no fabricated expressions. If you hold a phrase with permission to record it, keep a private local draft with its regional context and source or community-review note. The draft is never treated as verified, translated, submitted, or used automatically.</p><div className="community-language-status"><span>Selected language</span><b>{selected.name}</b><span>Review state</span><b>{selected.communityReview}</b></div><div className="colloquial-draft-grid"><label>Expression<input value={expression} onChange={(event) => setExpression(event.target.value.slice(0, 120))} maxLength={120} placeholder="Private draft only" /></label><label>Region / context<input value={regionalContext} onChange={(event) => setRegionalContext(event.target.value.slice(0, 160))} maxLength={160} placeholder="Required" /></label><label className="colloquial-source">Source or community-review note<textarea value={sourceNote} onChange={(event) => setSourceNote(event.target.value.slice(0, 240))} maxLength={240} placeholder="Required; not sent anywhere" /></label></div><div className="language-actions"><button className="outline-button" onClick={savePrivateDraft}><FileText size={15} /> Save private local draft</button><span>{privateDrafts.length} private draft{privateDrafts.length === 1 ? "" : "s"} · not community reviewed</span></div></section>

    <section className="multilingual-search-review"><div className="language-panel-heading"><div><span className="eyebrow">Research preparation</span><h3>Keep the question in {activeLanguage}.</h3></div><Search size={20} /></div><p>Arthur prepares the question exactly as you write it, then tells you if an approved research or language provider is needed. It never automatically submits, translates, or stores the question.</p><textarea value={researchQuestion} onChange={(event) => { setResearchQuestion(event.target.value.slice(0, 500)); setPrepared(null); }} maxLength={500} placeholder={`Ask a question in ${activeLanguage}`} /><div className="language-actions"><button className="primary-button compact" onClick={prepare}><Search size={15} /> Prepare for review</button><span>{researchQuestion.length}/500</span></div>{prepared && <div className={`prepared-language-query ${prepared.ready ? "ready" : "needs-input"}`}><b>{prepared.ready ? `Prepared locally · ${prepared.language?.name} (${prepared.language?.code.toUpperCase()})` : "Not yet prepared"}</b>{prepared.ready && <code>{prepared.query}</code>}<p>{prepared.reason}</p>{prepared.ready && <button className="outline-button" onClick={copyPrepared}><Copy size={15} /> Copy prepared query</button>}</div>}</section>
  </section>;
}
