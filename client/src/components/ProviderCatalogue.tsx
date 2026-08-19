import { Activity, CircleAlert, Database, Filter, LoaderCircle, Search, ShieldAlert, SlidersHorizontal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { apiCatalogue, catalogueCounts, providerPlaceholderKey, type CatalogueCategory } from "@/lib/apiCatalogue";

type FilterMode = "all" | "developer" | "account" | "local" | "review";
type TestState = "idle" | "testing" | "needs-resource" | "review";

function matchesFilter(category: CatalogueCategory, filter: FilterMode) {
  if (filter === "all") return true;
  if (filter === "review") return Boolean(category.reviewRequired);
  if (filter === "developer") return category.owner === "Developer";
  if (filter === "account") return category.owner === "User account";
  return category.owner === "Local desktop";
}

type ProviderCatalogueProps = {
  openIntegration: () => void;
  focusCategory?: string | null;
  clearFocus?: () => void;
};

export default function ProviderCatalogue({ openIntegration, focusCategory, clearFocus }: ProviderCatalogueProps) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterMode>("all");
  const [tests, setTests] = useState<Record<string, TestState>>({});
  const visible = useMemo(() => {
    const query = search.trim().toLowerCase();
    return apiCatalogue.filter((category) => matchesFilter(category, filter) && (!query || [category.name, category.function, category.auth, category.owner, ...category.providers].join(" ").toLowerCase().includes(query)));
  }, [filter, search]);
  const standardVisible = visible.filter((category) => !category.reviewRequired);
  const reviewVisible = visible.filter((category) => category.reviewRequired);
  useEffect(() => {
    if (!focusCategory) return;
    setFilter("all");
    setSearch(focusCategory);
    window.requestAnimationFrame(() => document.getElementById("provider-catalogue")?.scrollIntoView({ behavior: "smooth", block: "start" }));
  }, [focusCategory]);
  const testCategory = (category: CatalogueCategory) => {
    setTests((current) => ({ ...current, [category.id]: "testing" }));
    window.setTimeout(() => {
      const next: TestState = category.reviewRequired ? "review" : "needs-resource";
      setTests((current) => ({ ...current, [category.id]: next }));
      toast(next === "review" ? "Approval review is required" : "No approved resource is connected", { description: `${category.name}: this preview did not send credentials or contact any provider.` });
    }, 520);
  };

  const renderCard = (category: CatalogueCategory, reviewSurface = false) => {
    const state = tests[category.id] ?? "idle";
    return <article className={`catalogue-card ${category.reviewRequired ? "review-required" : ""} ${reviewSurface ? "review-surface-card" : ""}`} key={category.id} id={`api-category-${category.id}`}><div className="catalogue-card-top"><span className="catalogue-number">{String(apiCatalogue.indexOf(category) + 1).padStart(2, "0")}</span>{category.reviewRequired && <span className="review-badge"><ShieldAlert size={12} />Review</span>}</div><h3>{category.name}</h3><p>{category.function}</p><dl><div><dt>Owner</dt><dd>{category.owner}</dd></div><div><dt>Auth</dt><dd>{category.auth}</dd></div><div><dt>Resource</dt><dd>{state === "testing" ? "Checking safely" : state === "review" ? "Review before setup" : state === "needs-resource" ? "No resource connected" : "Placeholder only"}</dd></div></dl><details><summary><Filter size={13} /> View {category.providers.length} placeholders</summary><div className="provider-tag-list">{category.providers.map((provider) => <span key={providerPlaceholderKey(category.id, provider)}>{provider}</span>)}</div></details><div className="catalogue-card-actions"><button className="text-button" onClick={openIntegration}>{category.reviewRequired ? "Review setup" : "Add resource"}</button><button className="test-button" onClick={() => testCategory(category)} disabled={state === "testing"}>{state === "testing" && <LoaderCircle size={12} className="spin" />}{state === "testing" ? "Testing safely…" : "Test room"}</button></div></article>;
  };
  return <section className="provider-catalogue" id="provider-catalogue">
    <header className="catalogue-heading">
      <div><span className="eyebrow">Provider placeholder catalogue / function classified</span><h2>Every room has a declared boundary.</h2><p>{catalogueCounts.categories} function categories and {catalogueCounts.providers} provider placeholders are registered for review. Registration is not connection: Arthur stops when the required room has no approved resource.</p></div>
      <div className="catalogue-readout"><Database size={20} /><span><b>{catalogueCounts.providers}</b> provider placeholders</span><small>{catalogueCounts.reviewRequired} review-required rooms</small></div>
    </header>
    <div className="catalogue-controls"><label className="catalogue-search"><Search size={17} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search provider, category, or function" aria-label="Search API placeholders" /></label><div className="catalogue-filters" aria-label="Filter API placeholder catalogue"><SlidersHorizontal size={16} />{(["all", "developer", "account", "local", "review"] as FilterMode[]).map((item) => <button key={item} className={filter === item ? "active" : ""} onClick={() => setFilter(item)}>{item === "all" ? "All rooms" : item === "developer" ? "Developer" : item === "account" ? "User account" : item === "local" ? "Desktop" : "Review required"}</button>)}</div></div>
    <div className="catalogue-routing-note"><CircleAlert size={17} /><p><b>Routing rule:</b> Arthur first identifies the function. If its room is unconfigured, it reports “No resource of information” and opens the approved setup path. It does not substitute a random provider, contact an API, or run raw commands.</p><button className="outline-button" onClick={openIntegration}>Add approved API</button></div>
    {focusCategory && <div className="catalogue-focus" role="status"><CircleAlert size={17} /><div><b>Required by your command: {focusCategory}</b><span>This catalogue is focused on the declared category. Add and test an approved provider before preparing the request again.</span></div><button className="text-button" onClick={clearFocus}>Clear focus</button></div>}
    <div className="catalogue-grid">{standardVisible.map((category) => renderCard(category))}</div>
    {reviewVisible.length > 0 && <section className="review-boundary" aria-labelledby="review-boundary-heading"><header><span className="eyebrow"><ShieldAlert size={14} /> Review-required / excluded from automatic routing</span><h3 id="review-boundary-heading">Sensitive capability rooms remain behind a human review boundary.</h3><p>Arthur will not auto-select, test against a live service, or execute work through these rooms. A responsible developer must approve the provider, scope, and permission before any connection can be enabled.</p></header><div className="review-boundary-grid">{reviewVisible.map((category) => renderCard(category, true))}</div></section>}
    {visible.length === 0 && <div className="catalogue-empty"><Activity size={18} /><p>No placeholder matches that search. Add a custom approved integration only after reviewing its function and permissions.</p></div>}
  </section>;
}
