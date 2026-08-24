import { CheckCircle2, CircleAlert, LoaderCircle, Sparkles, TerminalSquare } from "lucide-react";
import { useState } from "react";
import { previewProviderOutcome } from "@/lib/providerPreviewState";

type PreviewState = "not-connected" | "testing" | "key-required" | "desktop-test-required" | "desktop-setup-ready" | "local-setup-required";

type Props = {
  label: string;
  provider: string;
  detail: string;
  fieldName: string;
  openWakeWordSetup: () => void;
};

const presentation: Record<PreviewState, { badge: string; tone: "gray" | "amber" | "blue" | "green"; detail: string }> = {
  "not-connected": { badge: "Not connected", tone: "gray", detail: "No provider credential is configured in this preview." },
  testing: { badge: "Checking preview", tone: "blue", detail: "Arthur is checking the browser-preview form only; it is not sending a request." },
  "key-required": { badge: "Key required", tone: "amber", detail: "Enter a development key in the installed Windows app, then save and approve a live test there." },
  "desktop-test-required": { badge: "Desktop test required", tone: "amber", detail: "A value was entered only in this preview. The preview cannot save or test it; use the installed Windows API Vault." },
  "desktop-setup-ready": { badge: "Desktop setup ready", tone: "amber", detail: "This preview has not saved a secret. Continue in the installed Windows API Vault to store it in the OS credential manager." },
  "local-setup-required": { badge: "Local setup required", tone: "amber", detail: "This local adapter requires a separately approved installation and readiness check on the Windows PC." },
};

function PreviewStatusPill({ tone, children }: { tone: "gray" | "amber" | "blue" | "green"; children: React.ReactNode }) {
  return <span className={`status-pill ${tone}`}><span className="status-dot" />{children}</span>;
}

export default function ProviderPreviewCard({ label, provider, detail, fieldName, openWakeWordSetup }: Props) {
  const [draft, setDraft] = useState("");
  const [state, setState] = useState<PreviewState>(provider === "openWakeWord" ? "local-setup-required" : "not-connected");
  const visible = presentation[state];
  const testPreview = () => {
    if (provider === "openWakeWord") {
      setState("local-setup-required");
      openWakeWordSetup();
      return;
    }
    setState("testing");
    window.setTimeout(() => setState(previewProviderOutcome(provider, Boolean(draft.trim()), "test")), 360);
  };
  const savePreview = () => setState(previewProviderOutcome(provider, Boolean(draft.trim()), "save"));

  return <article className="provider-card" data-provider-state={state}>
    <div className="provider-heading"><span className="provider-icon"><Sparkles size={16} /></span><div><h3>{label}</h3><p>{detail}</p></div><PreviewStatusPill tone={visible.tone}>{visible.badge}</PreviewStatusPill></div>
    <label>Provider<select defaultValue={provider}><option>{provider}</option><option>Custom provider</option><option>Disabled</option></select></label>
    {provider === "Supabase" ? <><label>Project URL<input type="url" name="supabase-url" placeholder="https://your-project.supabase.co" /></label><label>Publishable key<input type="password" name="supabase-publishable-key" value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="sb_publishable_..." /></label></> : provider === "openWakeWord" ? <div className="wakeword-card-note"><PreviewStatusPill tone="amber">Local install required</PreviewStatusPill><p>The desktop app requests approval before opening Command Prompt or enabling tray listening.</p><button className="outline-button" onClick={openWakeWordSetup}><TerminalSquare size={15} /> Review setup</button></div> : <label>Developer key<input type="password" name={fieldName} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Enter only in the installed Windows app" /></label>}
    <p className="connection-result preview-provider-result" role="status" aria-live="polite">{state === "testing" ? <LoaderCircle size={12} className="spin" /> : state === "not-connected" ? <CircleAlert size={12} /> : <CheckCircle2 size={12} />}<span>{visible.detail}</span></p>
    <div className="provider-actions"><button className="outline-button" disabled={state === "testing"} onClick={testPreview}>{state === "testing" ? "Checking preview…" : provider === "openWakeWord" ? "Review local setup" : "Check preview setup"}</button><button className="text-button" onClick={savePreview}>Review desktop setup</button></div>
  </article>;
}
