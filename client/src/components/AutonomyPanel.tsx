import { useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, CircleDotDashed, Eye, KeyRound, Mic, Palette, PauseCircle, Play, Radio, RotateCcw, ShieldCheck, Sparkles, Volume2, WandSparkles, XCircle } from "lucide-react";
import { toast } from "sonner";
import { assessNaturalLanguage, type IntentAssessment } from "@/lib/naturalLanguageIntent";
import { policyDescription, recommendProviderStep, type ProviderDecisionPolicy, type RouteStep } from "@/lib/providerOrchestration";
import type { SelfCustomizationProposal } from "@/lib/selfCustomization";
import { approveSelfCustomization, prepareSelfCustomization, rejectSelfCustomization, reviseSelfCustomization, type SelfCustomizationLifecycleState } from "@/lib/selfCustomizationLifecycle";

export type BackgroundPolicy = {
  enabled: boolean;
  localListening: boolean;
  actionExecution: boolean;
  spokenReply: boolean;
  visualResult: "ask" | "always" | "spoken-first";
};

export type AppearancePreferences = {
  typeScale: "standard" | "large" | "extra";
  density: "relaxed" | "compact";
  motion: "calm" | "reduced";
};

type Props = {
  policy: BackgroundPolicy;
  setPolicy: (next: BackgroundPolicy) => void;
  appearance: AppearancePreferences;
  setAppearance: (next: AppearancePreferences) => void;
  setColourMode: (next: "cobalt" | "tide" | "amber") => void;
  openPermissions: () => void;
  openApiVault: (category?: string) => void;
};

const orchestrationPlans: Record<"research" | "voice" | "change", RouteStep[]> = {
  research: [
    { label: "OpenAI / intent planning", category: "AI, reasoning & embeddings", role: "Primary", quality: 4, cost: 2 },
    { label: "SerpAPI / approved sources", category: "Search, news & research", role: "Support", quality: 4, cost: 2 },
    { label: "Anthropic / optional second-pass synthesis", category: "AI, reasoning & embeddings", role: "Fallback", quality: 5, cost: 3 },
  ],
  voice: [
    { label: "openWakeWord / local wake event", category: "Windows & local desktop", role: "Primary", quality: 4, cost: 1 },
    { label: "OpenAI Audio / transcription and spoken reply", category: "Speech, translation & language", role: "Support", quality: 5, cost: 3 },
    { label: "Windows audio adapter / approved playback", category: "Windows & local desktop", role: "Fallback", quality: 3, cost: 1 },
  ],
  change: [
    { label: "Local preference layer / reversible appearance changes", category: "Windows & local desktop", role: "Primary", quality: 4, cost: 1 },
    { label: "Lovable OAuth MCP / app-change proposal", category: "App building, code & deployment", role: "Support", quality: 4, cost: 2 },
    { label: "Manus project workspace / test and rollback review", category: "App building, code & deployment", role: "Fallback", quality: 5, cost: 2 },
  ],
};

const categoryAvailability = {
  "AI, reasoning & embeddings": true,
  "Search, news & research": false,
  "Speech, translation & language": false,
  "Windows & local desktop": true,
  "App building, code & deployment": false,
} as const;

function proposalStatus(state: SelfCustomizationLifecycleState, proposal?: SelfCustomizationProposal) {
  if (state === "approved") return "Approval recorded. No provider has been contacted and no code has been changed.";
  if (state === "rejected") return "Proposal rejected. Arthur keeps the current behaviour and settings.";
  if (state === "clarification") return "Arthur requires a clearer outcome before it can prepare a proposal.";
  if (state === "prepared") return proposal?.approvalAllowed ? "Proposal ready for your explicit review and approval." : "Proposal is informative only; it cannot be approved.";
  return "Arthur will show the outcome, scope, tests, resources, and rollback point before it asks for approval.";
}

export default function AutonomyPanel({ policy, setPolicy, appearance, setAppearance, setColourMode, openPermissions, openApiVault }: Props) {
  const [request, setRequest] = useState("Could you make it quieter when I am in a meeting?");
  const [assessment, setAssessment] = useState<IntentAssessment>(() => assessNaturalLanguage(request));
  const [goal, setGoal] = useState<keyof typeof orchestrationPlans>("research");
  const [decisionPolicy, setDecisionPolicy] = useState<ProviderDecisionPolicy>("balanced");
  const [availability, setAvailability] = useState<Record<keyof typeof categoryAvailability, boolean>>(categoryAvailability);
  const [changeRequest, setChangeRequest] = useState("Use larger compact writing when I ask for a focused workspace.");
  const [proposal, setProposal] = useState<SelfCustomizationProposal>();
  const [proposalState, setProposalState] = useState<SelfCustomizationLifecycleState>("idle");

  const selectedPlan = orchestrationPlans[goal];
  const recommendation = useMemo(() => recommendProviderStep(selectedPlan, decisionPolicy, availability), [decisionPolicy, selectedPlan, availability]);
  const unavailableStep = selectedPlan.find((step) => !availability[step.category as keyof typeof availability]);

  const routeRequest = () => {
    const next = assessNaturalLanguage(request);
    setAssessment(next);
    toast(next.kind === "clarification" ? "Arthur requires a clarification." : `${next.label} classified.`, { description: next.summary });
  };

  const updatePolicy = (key: keyof Omit<BackgroundPolicy, "visualResult">) => {
    if (key === "localListening" && !policy.enabled) {
      toast.error("Accept background readiness before enabling local wake listening.");
      return;
    }
    setPolicy({ ...policy, [key]: !policy[key] });
  };

  const pauseAll = () => {
    setPolicy({ ...policy, enabled: false, localListening: false, actionExecution: false });
    toast("All background readiness, listening, and action execution are paused.");
  };

  const prepareProposal = () => {
    const next = prepareSelfCustomization(changeRequest);
    setProposal(next.proposal);
    setProposalState(next.state);
    const needsClarification = next.state === "clarification";
    toast(needsClarification ? "Arthur needs a little more detail." : "Self-customisation proposal prepared.", {
      description: needsClarification ? next.proposal?.summary : "No provider was contacted, no setting was changed, and no code was edited.",
    });
  };

  const approveProposal = () => {
    const next = approveSelfCustomization({ state: proposalState, proposal });
    if (next.state !== "approved" || !next.proposal) return;
    if (next.appliedPreferencePatch) {
      const { colour, ...appearancePatch } = next.appliedPreferencePatch;
      if (colour) setColourMode(colour);
      if (Object.keys(appearancePatch).length > 0) setAppearance({ ...appearance, ...appearancePatch });
    }
    setProposal(next.proposal);
    setProposalState(next.state);
    toast("Proposal approval recorded.", {
      description: next.appliedPreferencePatch
        ? "Only the reviewed local presentation preference was applied."
        : "A separately authorized development workflow must still review the implementation, tests, and rollback checkpoint.",
    });
  };

  const rejectProposal = () => {
    const next = rejectSelfCustomization({ state: proposalState, proposal });
    if (next.state !== "rejected" || !next.proposal) return;
    setProposal(next.proposal);
    setProposalState(next.state);
    toast("Proposal rejected.", { description: "No preferences, providers, or code were changed." });
  };

  const reviseProposal = () => {
    const next = reviseSelfCustomization();
    setProposal(next.proposal);
    setProposalState(next.state);
    toast("Proposal returned for revision.", { description: "Edit the request and prepare a new review; nothing has been changed." });
  };

  return (
    <section className="autonomy-layout">
      <header className="autonomy-hero">
        <div>
          <span className="eyebrow">Consent-first operating model</span>
          <h2>Understands your meaning. Waits for your permission.</h2>
          <p>Arthur accepts natural speech and alternate phrasing, but it separates understanding from action. Background readiness, listening, action execution, visual outputs, and self-customisation are choices you can change at any time.</p>
        </div>
        <div className="autonomy-orbit" aria-hidden="true"><span /><span /><div><Radio size={25} /><b>OPT-IN</b></div></div>
      </header>

      <div className="autonomy-grid">
        <section className="autonomy-panel consent-panel">
          <div className="section-heading"><div><span className="eyebrow">Background consent</span><h3>Choose how Arthur waits</h3></div><ShieldCheck size={19} /></div>
          <label className="autonomy-row"><span><b>Background readiness</b><small>Allow the installed Windows app to stay available in the system tray after its window closes.</small></span><button className={`switch ${policy.enabled ? "on" : ""}`} aria-pressed={policy.enabled} onClick={() => updatePolicy("enabled")}><span /></button></label>
          <label className="autonomy-row"><span><b>Local wake listening</b><small>Only operates when background readiness is accepted. Pause or stop remains available at all times.</small></span><button className={`switch ${policy.localListening ? "on" : ""}`} aria-pressed={policy.localListening} onClick={() => updatePolicy("localListening")}><span /></button></label>
          <label className="autonomy-row"><span><b>Action execution after spoken consent</b><small>Arthur may perform only a reviewed, permitted action after it repeats the plan and receives an explicit “yes.” Consequential actions remain separately confirmed.</small></span><button className={`switch ${policy.actionExecution ? "on" : ""}`} aria-pressed={policy.actionExecution} onClick={() => updatePolicy("actionExecution")}><span /></button></label>
          <label className="autonomy-row"><span><b>Spoken responses</b><small>Use voice replies when the configured speech provider and local speaker path are available.</small></span><button className={`switch ${policy.spokenReply ? "on" : ""}`} aria-pressed={policy.spokenReply} onClick={() => updatePolicy("spokenReply")}><span /></button></label>
          <div className="visual-choice"><Eye size={17} /><div><b>Visual results</b><small>For a chart, image, file, or screen result:</small></div><select value={policy.visualResult} onChange={(event) => setPolicy({ ...policy, visualResult: event.target.value as BackgroundPolicy["visualResult"] })}><option value="ask">Ask before showing</option><option value="always">Show when useful</option><option value="spoken-first">Speak first, then ask</option></select></div>
          <button className="pause-all-button" onClick={pauseAll}><PauseCircle size={16} /> Pause all background activity</button>
          <div className="consent-foot"><CheckCircle2 size={17} /><span>{policy.enabled ? policy.actionExecution ? "Background readiness and reviewed action execution are accepted. Arthur still confirms consequential actions." : "Background readiness is accepted, but Arthur will only prepare—not execute—actions." : "Background operation is off. Arthur remains available only while the foreground app is active."}</span></div>
        </section>

        <section className="autonomy-panel intent-panel">
          <div className="section-heading"><div><span className="eyebrow">Natural language intake</span><h3>No fixed spoken command list</h3></div><Mic size={19} /></div>
          <p className="muted-copy">Try alternate wording. This safe starter maps intent to a reviewed category; an unfamiliar request asks for clarification rather than generating a shell command.</p>
          <div className="intent-entry"><input value={request} onChange={(event) => setRequest(event.target.value)} onKeyDown={(event) => event.key === "Enter" && routeRequest()} placeholder="For example: Could you make it quieter?" /><button className="primary-button compact" onClick={routeRequest}>Interpret <Sparkles size={15} /></button></div>
          <div className={`intent-result ${assessment.kind}`}><span className="intent-icon">{assessment.kind === "clarification" ? <CircleDotDashed size={18} /> : assessment.consequence === "proposal" ? <WandSparkles size={18} /> : <CheckCircle2 size={18} />}</span><div><span className="eyebrow">{assessment.label}</span><b>{assessment.requiredRoom}</b><p>{assessment.summary}</p>{assessment.alternatePhrasing.length > 0 && <small>Also understood: {assessment.alternatePhrasing.join(" · ")}</small>}</div>{assessment.vaultCategory ? <button className="outline-button" onClick={() => openApiVault(assessment.vaultCategory)}>View category <KeyRound size={14} /></button> : <span className="local-result-state">{assessment.kind === "appearance" ? "Applies locally after review" : "Clarify before routing"}</span>}</div>
        </section>
      </div>

      <section className="orchestration-panel">
        <div className="section-heading"><div><span className="eyebrow">Provider orchestra</span><h3>Coordinate approved rooms; do not guess connections.</h3></div><Volume2 size={19} /></div>
        <p>Arthur chooses from declared rooms by availability and the decision policy. A missing primary room is reported and opened in the vault; it is not silently substituted.</p>
        <div className="orchestration-controls"><label>Goal<select value={goal} onChange={(event) => setGoal(event.target.value as keyof typeof orchestrationPlans)}><option value="research">Research and spoken brief</option><option value="voice">Voice interaction</option><option value="change">Reviewable app change</option></select></label><label>Cost / quality preference<select value={decisionPolicy} onChange={(event) => setDecisionPolicy(event.target.value as ProviderDecisionPolicy)}><option value="balanced">Balanced quality and cost</option><option value="quality">Prefer highest verified quality</option><option value="cost">Prefer lowest approved cost</option></select></label><button className="outline-button" onClick={() => unavailableStep ? openApiVault(unavailableStep.category) : openApiVault()}><KeyRound size={15} /> {unavailableStep ? "Open missing room" : "Inspect rooms"}</button></div>
        <div className="policy-readout" role="status"><CheckCircle2 size={15} /><span><b>Active preference:</b> {policyDescription[decisionPolicy]} <strong>{recommendation ? `Recommendation only: ${recommendation.label}.` : "No approved available room can be recommended."}</strong> The declared primary → support → fallback chain below does not change automatically.</span></div>
        <div className="availability-strip">{(Object.keys(availability) as Array<keyof typeof availability>).map((category) => <button key={category} className={availability[category] ? "available" : "unavailable"} aria-pressed={availability[category]} onClick={() => setAvailability({ ...availability, [category]: !availability[category] })}><span />{category}</button>)}</div>
        <div className="chain-label"><span className="eyebrow">Declared execution chain</span><small>Stable order; any alternative recommendation requires review and confirmation.</small></div>
        <ol className="provider-chain">{selectedPlan.map((step, index) => <li key={`${step.label}-${index}`} className={availability[step.category as keyof typeof availability] ? "" : "route-unavailable"}><span>{String(index + 1).padStart(2, "0")}</span><b>{step.label}</b><small>{availability[step.category as keyof typeof availability] ? `${step.role} route · quality ${step.quality}/5 · cost ${step.cost}/5` : `Unavailable · add or test ${step.category}`}</small></li>)}</ol>
        <div className={`orchestration-foot ${unavailableStep ? "needs-resource" : ""}`}><AlertTriangle size={17} /><span>{unavailableStep ? `${unavailableStep.category} is unavailable for this route. Arthur will stop at the resource gate until it is added and tested.` : "All demonstrated rooms are marked available in this preview. Live calls still require developer credentials and the applicable user approval."}</span></div>
      </section>

      <div className="autonomy-grid lower-grid">
        <section className="autonomy-panel evolution-panel">
          <div className="section-heading"><div><span className="eyebrow">Review-first self-customisation</span><h3>Describe a change in your own words</h3></div><WandSparkles size={19} /></div>
          <p className="muted-copy">Arthur classifies your request as a presentation, demeanor, voice, provider, or capability change. It creates a concrete proposal, and applies nothing until you approve. Approved local requests can update only workspace colour, type scale, density, or motion. Approval never publishes code or contacts Manus, Lovable, or another provider by itself.</p>
          <textarea value={changeRequest} onChange={(event) => { setChangeRequest(event.target.value); setProposalState("idle"); }} aria-label="Requested Arthur customisation" placeholder="For example: Arthur, make the writing larger and compact when I am concentrating." />
          <div className="evolution-actions"><button className="outline-button" onClick={prepareProposal}>Prepare review <Play size={15} /></button><button className="primary-button" disabled={proposalState !== "prepared" || !proposal?.approvalAllowed} onClick={approveProposal}>Approve scoped proposal <ShieldCheck size={15} /></button><button className="outline-button" disabled={proposalState !== "prepared"} onClick={reviseProposal}>Revise request <RotateCcw size={15} /></button><button className="outline-button" disabled={proposalState !== "prepared"} onClick={rejectProposal}>Reject <XCircle size={15} /></button></div>
          <div className={`proposal-state ${proposalState}`} aria-live="polite"><b>{proposal ? proposal.label : "No proposal is active."}</b><span>{proposalStatus(proposalState, proposal)}</span></div>
          {proposal && proposalState !== "idle" && <div className="proposal-detail">
            <div><span className="eyebrow">Requested outcome</span><p>{proposal.requestedOutcome}</p></div>
            <div><span className="eyebrow">Affected areas</span><ul>{proposal.affectedAreas.map((item) => <li key={item}>{item}</li>)}</ul></div>
            <div><span className="eyebrow">Review and validation</span><ul>{proposal.reviewSteps.map((item) => <li key={item}>{item}</li>)}</ul></div>
            <div><span className="eyebrow">Resources and recovery</span>{proposal.requiredRoom && <b>{proposal.requiredRoom}</b>}{proposal.vaultCategory && <button className="text-button" onClick={() => openApiVault(proposal.vaultCategory)}>Inspect required room</button>}<p>{proposal.rollback}</p></div>
          </div>}
        </section>

        <section className="autonomy-panel appearance-panel">
          <div className="section-heading"><div><span className="eyebrow">Personal format controls</span><h3>Change the way Arthur presents itself</h3></div><Palette size={19} /></div>
          <p className="muted-copy">These local preview settings are reversible. You may also ask for these changes by voice; Arthur will show the affected setting before it applies it.</p>
          <div className="appearance-control"><b>Type scale</b><div>{(["standard", "large", "extra"] as const).map((value) => <button key={value} className={appearance.typeScale === value ? "selected" : ""} onClick={() => setAppearance({ ...appearance, typeScale: value })}>{value === "extra" ? "Extra large" : value}</button>)}</div></div>
          <div className="appearance-control"><b>Information density</b><div>{(["relaxed", "compact"] as const).map((value) => <button key={value} className={appearance.density === value ? "selected" : ""} onClick={() => setAppearance({ ...appearance, density: value })}>{value}</button>)}</div></div>
          <div className="appearance-control"><b>Motion</b><div>{(["calm", "reduced"] as const).map((value) => <button key={value} className={appearance.motion === value ? "selected" : ""} onClick={() => setAppearance({ ...appearance, motion: value })}>{value}</button>)}</div></div>
          <button className="outline-button reset-appearance" onClick={() => setAppearance({ typeScale: "standard", density: "relaxed", motion: "calm" })}><RotateCcw size={15} /> Restore default presentation</button>
        </section>
      </div>
      <button className="permissions-link" onClick={openPermissions}><ShieldCheck size={16} /> Review the permissions that govern each action class</button>
    </section>
  );
}
