import { useMemo, useState } from "react";
import { BadgeCheck, Check, Copy, ExternalLink, FileText, Globe2, Languages, Search, Star, Upload } from "lucide-react";
import { toast } from "sonner";
import {
  createPrivateColloquialDraft,
  filterLanguages,
  getSourceConfirmedExpressions,
  mergeImportedLanguageReferences,
  parseIso6393Table,
  prepareColloquialEntryReview,
  prepareMultilingualSearch,
  prepareSourceConfirmedExpression,
  type ColloquialEntryReview,
  type ExpressionEvidenceKind,
  type ImportedLanguageReference,
  type LanguageEntry,
  type PrivateColloquialDraft,
  type SourceConfirmedExpression,
} from "@/lib/languageLibrary";
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
  const [importedReferences, setImportedReferences] = useState<ImportedLanguageReference[]>([]);
  const [researchQuestion, setResearchQuestion] = useState("");
  const [prepared, setPrepared] = useState<ReturnType<typeof prepareMultilingualSearch> | null>(null);
  const [expression, setExpression] = useState("");
  const [meaning, setMeaning] = useState("");
  const [regionalContext, setRegionalContext] = useState("");
  const [sourceNote, setSourceNote] = useState("");
  const [sensitivityNote, setSensitivityNote] = useState("");
  const [useContext, setUseContext] = useState("");
  const [evidenceTitle, setEvidenceTitle] = useState("");
  const [evidenceUrl, setEvidenceUrl] = useState("");
  const [evidenceKind, setEvidenceKind] = useState<ExpressionEvidenceKind>("community-language-program");
  const [evidenceReviewed, setEvidenceReviewed] = useState(false);
  const [privateDrafts, setPrivateDrafts] = useState<PrivateColloquialDraft[]>([]);
  const [reviewPreview, setReviewPreview] = useState<ColloquialEntryReview | null>(null);
  const [sourceConfirmedPreview, setSourceConfirmedPreview] = useState<SourceConfirmedExpression | null>(null);

  const catalogue = useMemo(() => mergeImportedLanguageReferences(importedReferences), [importedReferences]);
  const matches = useMemo(() => filterLanguages(query, catalogue), [query, catalogue]);
  const sourceConfirmedRecords = useMemo(() => getSourceConfirmedExpressions(selected.name, catalogue), [selected.name, catalogue]);
  const selectedFavourite = favourites.includes(selected.name);

  const chooseLanguage = (entry: LanguageEntry) => {
    setSelected(entry);
    setActiveLanguage(entry.name);
    setPrepared(null);
    setSourceConfirmedPreview(null);
    toast.success(`${entry.name} selected`, {
      description: entry.readiness === "profile-ready"
        ? "Arthur can keep this as a local language preference."
        : "Choose an approved local pack or provider later if speech, translation, or research needs it.",
    });
  };

  const clearExpressionFields = () => {
    setExpression("");
    setMeaning("");
    setRegionalContext("");
    setSourceNote("");
    setSensitivityNote("");
    setUseContext("");
    setEvidenceTitle("");
    setEvidenceUrl("");
    setEvidenceReviewed(false);
    setReviewPreview(null);
    setSourceConfirmedPreview(null);
  };

  const toggleFavourite = () => {
    setFavourites((current) => selectedFavourite ? current.filter((name) => name !== selected.name) : [...current, selected.name]);
  };

  const prepare = () => setPrepared(prepareMultilingualSearch(researchQuestion, activeLanguage, catalogue));

  const savePrivateDraft = () => {
    try {
      const draft = createPrivateColloquialDraft(selected.name, expression, regionalContext, sourceNote, catalogue);
      setPrivateDrafts((current) => [...current, draft].slice(-40));
      clearExpressionFields();
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

  const previewReview = () => {
    try {
      setReviewPreview(prepareColloquialEntryReview(selected.name, expression, meaning, regionalContext, sourceNote, sensitivityNote, catalogue));
      toast.success("Review preview prepared locally", { description: "It remains unverified, unpublished, and unavailable to speech, translation, search, or replies." });
    } catch (error) {
      toast.error("Review preview needs context", { description: error instanceof Error ? error.message : "Complete every field before preparing a local review preview." });
    }
  };

  const previewSourceConfirmation = () => {
    try {
      setSourceConfirmedPreview(prepareSourceConfirmedExpression({
        language: selected.name,
        expression,
        meaning,
        regionalContext,
        useContext,
        sensitivityNote,
        evidenceKind,
        evidenceTitle,
        evidenceUrl,
        evidenceReviewed,
      }, catalogue));
      toast.success("Source-confirmed preview prepared locally", { description: "It records reviewer-attested evidence only. It is not community review, publishing permission, or approval for automatic use." });
    } catch (error) {
      toast.error("Source confirmation needs evidence", { description: error instanceof Error ? error.message : "Complete the expression, context, evidence, and reviewer attestation." });
    }
  };

  const importIdentifierTable = async (file: File | undefined) => {
    if (!file) return;
    try {
      const parsed = parseIso6393Table(await file.text());
      if (!parsed.length) throw new Error("No new ISO 639-3 identifiers were found in this table.");
      setImportedReferences(parsed);
      toast.success(`${parsed.length.toLocaleString()} identifiers staged locally`, { description: "The table was read in this browser only. It adds catalogue identifiers, not voice packs, translations, web searches, or slang." });
    } catch (error) {
      toast.error("Identifier table was not imported", { description: error instanceof Error ? error.message : "Choose a valid ISO 639-3 tab-separated table." });
    }
  };

  return (
    <section className="language-library" aria-label="Arthur language library">
      <header className="language-library-hero">
        <div>
          <span className="eyebrow">Language library / local catalogue</span>
          <h2>Choose the language before Arthur chooses a route.</h2>
          <p>This bundled catalogue helps you find language names, ISO codes, native labels, and writing systems. Selection is local: it never downloads a pack, turns on the microphone, translates your text, or begins a web search.</p>
        </div>
        <div className="language-library-seal"><Languages size={24} /><b>{catalogue.length.toLocaleString()}</b><span>catalogued<br />languages</span></div>
      </header>

      <section className="language-catalogue-import">
        <div>
          <span className="eyebrow">All-language coverage / local identifier table</span>
          <h3>Stage an official ISO 639-3 identifier table on this device.</h3>
          <p>Arthur has a bundled discovery set. Choose an official tab-separated table to add many known language identifiers for local selection and search. The file is read only in this browser session; it is not uploaded, stored, or treated as a language pack or slang source.</p>
        </div>
        <label className="outline-button"><Upload size={15} /> Choose ISO table<input type="file" accept=".tab,.tsv,text/tab-separated-values,text/plain" onChange={(event) => importIdentifierTable(event.target.files?.[0])} /></label>
        <div className="catalogue-import-summary"><b>{importedReferences.length.toLocaleString()}</b><span>additional identifiers staged locally</span></div>
      </section>

      <div className="language-library-grid">
        <section className="language-browser-panel">
          <div className="language-panel-heading"><div><span className="eyebrow">Discover</span><h3>Search the local library</h3></div><span>{matches.length} matches</span></div>
          <label className="language-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, ISO code, native label, or script" /></label>
          <div className="language-match-list" role="listbox" aria-label="Language matches">
            {matches.map((entry) => <button key={entry.code} className={`language-match ${selected.code === entry.code ? "selected" : ""}`} onClick={() => chooseLanguage(entry)} role="option" aria-selected={selected.code === entry.code}><span><b>{entry.name}</b><small>{entry.nativeLabel} · {entry.code.toUpperCase()}</small></span><em>{entry.readiness === "profile-ready" ? "profile ready" : "pack / provider"}</em></button>)}
          </div>
        </section>

        <section className="language-detail-panel">
          <div className="language-panel-heading"><div><span className="eyebrow">Selected language</span><h3>{selected.name}</h3></div><Globe2 size={20} /></div>
          <p className="language-native">{selected.nativeLabel}</p>
          <dl>
            <div><dt>ISO code</dt><dd>{selected.code.toUpperCase()}</dd></div>
            <div><dt>Writing system</dt><dd>{selected.script}</dd></div>
            <div><dt>Readiness</dt><dd>{selected.readiness === "profile-ready" ? "Local profile preference" : "Language pack or approved provider"}</dd></div>
            <div><dt>Community review</dt><dd>{selected.communityReview}</dd></div>
            <div><dt>Vitality context</dt><dd>{selected.vitalityContext}</dd></div>
            <div><dt>Colloquial content</dt><dd>{selected.colloquialStatus}</dd></div>
          </dl>
          <p className="language-boundary">{selected.readiness === "profile-ready" ? "Arthur can retain this as your current language preference. Actual speech and research still follow their own explicit permissions." : "This entry is available for selection and query preparation. Install a local pack or connect and approve a provider separately before Arthur attempts speech, translation, or research in it."}</p>
          <div className="language-actions"><button className="primary-button compact" onClick={() => chooseLanguage(selected)}><Check size={15} /> Use for conversation</button><button className="outline-button" onClick={toggleFavourite}><Star size={15} /> {selectedFavourite ? "Remove favourite" : "Add favourite"}</button></div>
          <div className="language-favourites"><span>Favourites</span>{favourites.map((name) => <button key={name} onClick={() => { const entry = filterLanguages("", catalogue).find((item) => item.name === name); if (entry) chooseLanguage(entry); }}>{name}</button>)}</div>
        </section>
      </div>

      <section className="community-language-review">
        <div className="language-panel-heading"><div><span className="eyebrow">Community context / source-governed drafts</span><h3>Do not make slang a stereotype.</h3></div><FileText size={20} /></div>
        <p>Arthur includes no fabricated expressions. Every language can hold a local draft only when its language, regional context, meaning, source or attribution, and sensitivity note are supplied. A review preview never becomes verified content, translation, speech, search, or a reply.</p>
        <div className="community-language-status"><span>Selected language</span><b>{selected.name}</b><span>Review state</span><b>{selected.communityReview}</b></div>

        {sourceConfirmedRecords.length > 0 && <div className="source-records" aria-label="Source-confirmed expressions">
          <div className="source-record-heading"><span className="eyebrow">Source-confirmed examples</span><span>Evidence retained · community review remains separate</span></div>
          {sourceConfirmedRecords.map((record) => <article key={`${record.language}-${record.expression}`} className="source-record">
            <div><BadgeCheck size={17} /><b>{record.reviewStatus}</b></div>
            <code>{record.expression} — {record.meaning}</code>
            <p><strong>Region / dialect:</strong> {record.regionalContext}<br /><strong>Use:</strong> {record.useContext}<br /><strong>Care:</strong> {record.sensitivityNote}</p>
            <a href={record.evidenceUrl} target="_blank" rel="noreferrer"><ExternalLink size={14} /> {record.evidenceTitle}</a>
          </article>)}
        </div>}

        <div className="colloquial-draft-grid">
          <label>Expression<input value={expression} onChange={(event) => setExpression(event.target.value.slice(0, 120))} maxLength={120} placeholder="Private draft only" /></label>
          <label>Meaning<input value={meaning} onChange={(event) => setMeaning(event.target.value.slice(0, 240))} maxLength={240} placeholder="Required for review" /></label>
          <label>Region / dialect context<input value={regionalContext} onChange={(event) => setRegionalContext(event.target.value.slice(0, 160))} maxLength={160} placeholder="Required; do not generalise" /></label>
          <label>Sensitivity / use note<input value={sensitivityNote} onChange={(event) => setSensitivityNote(event.target.value.slice(0, 180))} maxLength={180} placeholder="Required for review" /></label>
          <label className="colloquial-source">Source or community attribution<textarea value={sourceNote} onChange={(event) => setSourceNote(event.target.value.slice(0, 240))} maxLength={240} placeholder="Required; not sent anywhere" /></label>
        </div>
        <div className="language-actions"><button className="outline-button" onClick={previewReview}><FileText size={15} /> Prepare review preview</button><button className="outline-button" onClick={savePrivateDraft}><FileText size={15} /> Save private local draft</button><span>{privateDrafts.length} private draft{privateDrafts.length === 1 ? "" : "s"} · not community reviewed</span></div>
        {reviewPreview && <div className="prepared-language-query needs-input"><b>{reviewPreview.reviewStatus}</b><p>{reviewPreview.language} · {reviewPreview.regionalContext}</p><code>{reviewPreview.expression} — {reviewPreview.meaning}</code><p>Source: {reviewPreview.sourceNote}<br />Sensitivity: {reviewPreview.sensitivityNote}</p></div>}

        <div className="source-confirmation-form">
          <div className="source-record-heading"><span className="eyebrow">Reviewer-attested source confirmation</span><span>Still not community review or automatic-use approval</span></div>
          <div className="colloquial-draft-grid">
            <label>Use context<input value={useContext} onChange={(event) => setUseContext(event.target.value.slice(0, 180))} maxLength={180} placeholder="For example: greeting listed by source" /></label>
            <label>Evidence source type<select value={evidenceKind} onChange={(event) => setEvidenceKind(event.target.value as ExpressionEvidenceKind)}><option value="community-language-program">Community language programme</option><option value="government-cultural-resource">Government or cultural resource</option><option value="educational-or-archival-resource">Educational or archival resource</option></select></label>
            <label>Evidence title<input value={evidenceTitle} onChange={(event) => setEvidenceTitle(event.target.value.slice(0, 180))} maxLength={180} placeholder="Named publisher and resource" /></label>
            <label>HTTPS evidence URL<input value={evidenceUrl} onChange={(event) => setEvidenceUrl(event.target.value.slice(0, 500))} maxLength={500} placeholder="https://…" /></label>
          </div>
          <label className="evidence-attestation"><input type="checkbox" checked={evidenceReviewed} onChange={(event) => setEvidenceReviewed(event.target.checked)} /> I checked the named source, language or dialect, regional context, and intended use. I understand this cannot grant community-review status.</label>
          <div className="language-actions"><button className="primary-button compact" onClick={previewSourceConfirmation}><BadgeCheck size={15} /> Prepare source-confirmed preview</button></div>
          {sourceConfirmedPreview && <div className="prepared-language-query source-confirmed"><b>{sourceConfirmedPreview.reviewStatus}</b><p>{sourceConfirmedPreview.language} · {sourceConfirmedPreview.regionalContext}</p><code>{sourceConfirmedPreview.expression} — {sourceConfirmedPreview.meaning}</code><p><strong>Use:</strong> {sourceConfirmedPreview.useContext}<br /><strong>Evidence:</strong> {sourceConfirmedPreview.evidenceTitle}<br />{sourceConfirmedPreview.verificationNote}</p></div>}
        </div>
      </section>

      <section className="multilingual-search-review">
        <div className="language-panel-heading"><div><span className="eyebrow">Research preparation</span><h3>Keep the question in {activeLanguage}.</h3></div><Search size={20} /></div>
        <p>Arthur prepares the question exactly as you write it, then tells you if an approved research or language provider is needed. It never automatically submits, translates, or stores the question.</p>
        <textarea value={researchQuestion} onChange={(event) => { setResearchQuestion(event.target.value.slice(0, 500)); setPrepared(null); }} maxLength={500} placeholder={`Ask a question in ${activeLanguage}`} />
        <div className="language-actions"><button className="primary-button compact" onClick={prepare}><Search size={15} /> Prepare for review</button><span>{researchQuestion.length}/500</span></div>
        {prepared && <div className={`prepared-language-query ${prepared.ready ? "ready" : "needs-input"}`}><b>{prepared.ready ? `Prepared locally · ${prepared.language?.name} (${prepared.language?.code.toUpperCase()})` : "Not yet prepared"}</b>{prepared.ready && <code>{prepared.query}</code>}<p>{prepared.reason}</p>{prepared.ready && <button className="outline-button" onClick={copyPrepared}><Copy size={15} /> Copy prepared query</button>}</div>}
      </section>
    </section>
  );
}
