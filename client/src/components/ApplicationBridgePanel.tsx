import { useState } from "react";
import { AppWindow, Ban, ClipboardCheck, ShieldCheck, StopCircle } from "lucide-react";
import { toast } from "sonner";
import { applicationBridgeStatus, bridgeActionState, createApplicationScope, prepareApplicationNavigation, type ApplicationBridgeScope } from "@/lib/applicationBridge";

/** Browser preview only: Windows application inspection remains an opt-in desktop capability. */
export default function ApplicationBridgePanel({ privacyLocked }: { privacyLocked: boolean }) {
  const [title, setTitle] = useState("");
  const [scope, setScope] = useState<ApplicationBridgeScope | null>(null);
  const [planStatus, setPlanStatus] = useState("No navigation plan has been prepared.");

  const reviewScope = () => {
    const next = createApplicationScope(title, false);
    if (!next) {
      toast("Enter one visible desktop application title.");
      return;
    }
    setScope(next);
    setPlanStatus("Scope recorded locally; no application was enumerated or inspected.");
  };

  const approveScope = () => {
    if (!scope) return;
    if (privacyLocked) {
      toast("Turn off Privacy Lock only after reviewing the exact desktop app scope.");
      return;
    }
    setScope({ ...scope, approved: true });
    setPlanStatus(`Approved review scope for “${scope.title}”. Controls and content remain unread.`);
  };

  const preparePlan = () => {
    const result = prepareApplicationNavigation(scope, "Review the visible interface and propose the next navigation step");
    setPlanStatus(result.detail);
  };

  const clearBridge = () => {
    setScope(null);
    setTitle("");
    setPlanStatus("Emergency stop applied: no inspection, action queue, or background bridge remains active.");
  };

  return <section className="tools-panel application-bridge-panel" aria-label="Consent-gated Windows application bridge">
    <div className="section-heading"><div><span className="eyebrow">Windows app bridge / review only</span><h3>Browse one approved interface, never the whole desktop.</h3></div><AppWindow size={19} /></div>
    <p className="tools-intro">Arthur’s installed Windows prototype can later use an optional accessibility adapter for one named app. This browser preview cannot read, capture, enumerate, or control desktop software.</p>
    <div className="application-bridge-grid">
      <label>Visible desktop app title<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Example: Untitled - Notepad" maxLength={120} /></label>
      <button className="outline-button" onClick={reviewScope}>Prepare local scope</button>
      <button className="outline-button" disabled={!scope || privacyLocked} onClick={approveScope}>Approve this app only</button>
      <button className="outline-button" disabled={!scope?.approved} onClick={preparePlan}>Prepare navigation plan</button>
      <button className="text-button danger-text" onClick={clearBridge}><StopCircle size={15} /> Emergency stop & clear</button>
    </div>
    <div className="application-bridge-status"><ShieldCheck size={17} /><p>{applicationBridgeStatus(scope)}</p></div>
    <div className="application-bridge-status"><ClipboardCheck size={17} /><p>{planStatus}</p></div>
    <div className="application-bridge-boundary"><Ban size={16} /><p>Blocked by design: password fields, security prompts, background apps, screenshots, automatic clicks, typing, clipboard access, files, messages, and cloud sharing. {scope?.approved ? bridgeActionState(scope, "click").detail : "Per-app approval is required before any later Windows review."}</p></div>
  </section>;
}
