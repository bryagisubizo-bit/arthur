import { useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, CircleDotDashed, Eye, KeyRound, Mic, Palette, PauseCircle, Play, Radio, RotateCcw, ShieldCheck, Sparkles, Volume2, WandSparkles } from "lucide-react";
import { toast } from "sonner";
import { assessNaturalLanguage, type IntentAssessment } from "@/lib/naturalLanguageIntent";
import { policyDescription, recommendProviderStep, type ProviderDecisionPolicy, type RouteStep } from "@/lib/providerOrchestration";

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

export default function AutonomyPanel({ policy, setPolicy, appearance, setAppearance, openPermissions, openApiVault }: Props) {
  const [request, setRequest] = useState("Could you make it quieter when I am in a meeting?");
  const [assessment, setAssessment] = useState<IntentAssessment>(() => assessNaturalLanguage(request));
  const [goal, setGoal] = useState<keyof typeof orchestrationPlans>("research");
  const [decisionPolicy, setDecisionPolicy] = useState<ProviderDecisionPolicy>("balanced");
  const [availability, setAvailability] = useState<Record<keyof typeof categoryAvailability, boolean>>(categoryAvailability);
  const [changeRequest, setChangeRequest] = useState("Use a calmer compact writing style when I ask for a focused workspace.");
  const [proposalState, setProposalState] = useState<"idle" | "prepared" | "approved">("idle");
  const routeRequest = () => {
    const next = assessNaturalLanguage(request);
    setAssessment(next);
    toast(next.kind === "clarification" ? "Arthur requires a clarification." : `${next.label} classified.`, { description: next.summary });
  };
  const selectedPlan = orchestrationPlans[goal];
  const recommendation = useMemo(() => recommendProviderStep(selectedPlan, decisionPolicy, availability), [decisionPolicy, selectedPlan, availability]);
  const unavailableStep = selectedPlan.find((step) => !availability[step.category as keyof typeof availability]);
  const updatePolicy = (key: keyof Omit<BackgroundPolicy, "visualResult">) => {
    if (key === "localListening" && !policy.enabled) return toast.error("Accept background readiness before enabling local wake listening.");
    setPolicy({ ...policy, [key]: !policy[key] });
  };
  const pauseAll = () => {
    setPolicy({ ...policy, enabled: false, localListening: false, actionExecution: false });
    toast("All background readiness, listening, and action execution are paused.");
  };
  const proposal = {
    route: "Manus project workspace → Lovable OAuth MCP",
    category: "App building, code & deployment",
    diff: ["Autonomy workspace settings", "presentation tokens and layout", "preference state and tests"],
    tests: ["TypeScript check", "intent routing tests", "responsive preview review"],
    rollback: "Restore the checkpoint captured immediately before the approved change.",
  };

  return <section className="autonomy-layout">
    <header className="autonomy-hero">
      <div><span className="eyebrow">Consent-first operating model</span><h2>Understands your meaning. Waits for your permission.</h2><p>Arthur accepts natural speech and alternate phrasing, but it separates understanding from action. Background readiness, listening, action execution, and visual outputs are choices you can change at any time.</p></div>
      <div className="autonomy-orbit" aria-hidden="true"><span /><span /><div><Radio size={25} /><b>OPT-IN</b></div></div>
    </header>

    <div className="autonomy-grid">
      <section className="autonomy-panel consent-panel"><div className="section-heading"><div><span className="eyebrow">Background consent</span><h3>Choose how Arthur waits</h3></div><ShieldCheck size={19} /></div>
        <label className="autonomy-row"><span><b>Background readiness</b><small>Allow the installed Windows app to stay available in the system tray after its window closes.</small></span><button className={`switch ${policy.enabled ? "on" : ""}`} aria-pressed={policy.enabled} onClick={() => updatePolicy("enabled")}><span /></button></label>
        <label className="autonomy-row"><span><b>Local wake listening</b><small>Only operates when background readiness is accepted. Pause or stop remains available at all times.</small></span><button className={`switch ${policy.localListening ? "on" : ""}`} aria-pressed={policy.localListening} onClick={() => updatePolicy("localListening")}><span /></button></label>
        <label className="autonomy-row"><span><b>Action execution after spoken consent</b><small>Arthur may perform only a reviewed, permitted action after it repeats the plan and receives an explicit “yes.” Consequential actions remain separately confirmed.</small></span><button className={`switch ${policy.actionExecution ? "on" : ""}`} aria-pressed={policy.actionExecution} onClick={() => updatePolicy("actionExecution")}><span /></button></label>
        <label className="autonomy-row"><span><b>Spoken responses</b><small>Use voice replies when the configured speech provider and local speaker path are available.</small></span><button className={`switch ${policy.spokenReply ? "on" : ""}`} aria-pressed={policy.spokenReply} onClick={() => updatePolicy("spokenReply")}><span /></button></label>
        <div className="visual-choice"><Eye size={17} /><div><b>Visual results</b><small>For a chart, image, file, or screen result:</small></div><select value={policy.visualResult} onChange={(event) => setPolicy({ ...policy, visualResult: event.target.value as BackgroundPolicy["visualResult"] })}><option value="ask">Ask before showing</option><option value="always">Show when useful</option><option value="spoken-first">Speak first, then ask</option></select></div>
        <button className="pause-all-button" onClick={pauseAll}><PauseCircle size={16} /> Pause all background activity</button>
        <div className="consent-foot"><CheckCircle2 size={17} /><span>{policy.enabled ? policy.actionExecution ? "Background readiness and reviewed action execution are accepted. Arthur still confirms consequential actions." : "Background readiness is accepted, but Arthur will only prepare—not execute—actions." : "Background operation is off. Arthur remains available only while the foreground app is active."}</span></div>
      </section>

      <section className="autonomy-panel intent-panel"><div className="section-heading"><div><span className="eyebrow">Natural language intake</span><h3>No fixed spoken command list</h3></div><Mic size={19} /></div>
        <p className="muted-copy">Try alternate wording. This safe starter maps intent to a reviewed category; an unfamiliar request asks for clarification rather than generating a shell command.</p>
        <div className="intent-entry"><input value={request} onChange={(event) => setRequest(event.target.value)} onKeyDown={(event) => event.key === "Enter" && routeRequest()} placeholder="For example: Could you make it quieter?" /><button className="primary-button compact" onClick={routeRequest}>Interpret <Sparkles size={15} /></button></div>
        <div className={`intent-result ${assessment.kind}`}><span className="intent-icon">{assessment.kind === "clarification" ? <CircleDotDashed size={18} /> : assessment.consequence === "proposal" ? <WandSparkles size={18} /> : <CheckCircle2 size={18} />}</span><div><span className="eyebrow">{assessment.label}</span><b>{assessment.requiredRoom}</b><p>{assessment.summary}</p>{assessment.alternatePhrasing.length > 0 && <small>Also understood: {assessment.alternatePhrasing.join(" · ")}</small>}</div>{assessment.vaultCategory ? <button className="outline-button" onClick={() => openApiVault(assessment.vaultCategory)}>View category <KeyRound size={14} /></button> : <span className="local-result-state">{assessment.kind === "appearance" ? "Applies locally after review" : "Clarify before routing"}</span>}</div>
      </section>
    </div>

    <section className="orchestration-panel"><div className="section-heading"><div><span className="eyebrow">Provider orchestra</span><h3>Coordinate approved rooms; do not guess connections.</h3></div><Volume2 size={19} /></div><p>Arthur chooses from declared rooms by availability and the decision policy. A missing primary room is reported and opened in the vault; it is not silently substituted.</p>
      <div className="orchestration-controls"><label>Goal<select value={goal} onChange={(event) => setGoal(event.target.value as keyof typeof orchestrationPlans)}><option value="research">Research and spoken brief</option><option value="voice">Voice interaction</option><option value="change">Reviewable app change</option></select></label><label>Cost / quality preference<select value={decisionPolicy} onChange={(event) => setDecisionPolicy(event.target.value as ProviderDecisionPolicy)}><option value="balanced">Balanced quality and cost</option><option value="quality">Prefer highest verified quality</option><option value="cost">Prefer lowest approved cost</option></select></label><button className="outline-button" onClick={() => unavailableStep ? openApiVault(unavailableStep.category) : openApiVault()}><KeyRound size={15} /> {unavailableStep ? "Open missing room" : "Inspect rooms"}</button></div>
      <div className="policy-readout" role="status"><CheckCircle2 size={15} /><span><b>Active preference:</b> {policyDescription[decisionPolicy]} <strong>{recommendation ? `Recommendation only: ${recommendation.label}.` : "No approved available room can be recommended."}</strong> The declared primary → support → fallback chain below does not change automatically.</span></div>
      <div className="availability-strip">{(Object.keys(availability) as Array<keyof typeof availability>).map((category) => <button key={category} className={availability[category] ? "available" : "unavailable"} aria-pressed={availability[category]} onClick={() => setAvailability({ ...availability, [category]: !availability[category] })}><span />{category}</button>)}</div>
      <div className="chain-label"><span className="eyebrow">Declared execution chain</span><small>Stable order; any alternative recommendation requires review and confirmation.</small></div>
      <ol className="provider-chain">{selectedPlan.map((step, index) => <li key={`${step.label}-${index}`} className={availability[step.category as keyof typeof availability] ? "" : "route-unavailable"}><span>{String(index + 1).padStart(2, "0")}</span><b>{step.label}</b><small>{availability[step.category as keyof typeof availability] ? `${step.role} route · quality ${step.quality}/5 · cost ${step.cost}/5` : `Unavailable · add or test ${step.category}`}</small></li>)}</ol>
      <div className={`orchestration-foot ${unavailableStep ? "needs-resource" : ""}`}><AlertTriangle size={17} /><span>{unavailableStep ? `${unavailableStep.category} is unavailable for this route. Arthur will stop at the resource gate until it is added and tested.` : "All demonstrated rooms are marked available in this preview. Live calls still require developer credentials and the applicable user approval."}</span></div>
    </section>

    <div className="autonomy-grid lower-grid">
      <section className="autonomy-panel evolution-panel"><div className="section-heading"><div><span className="eyebrow">Reviewable evolution</span><h3>Ask Arthur to change itself—safely</h3></div><WandSparkles size={19} /></div><p className="muted-copy">Arthur can only prepare a scoped proposal for a connected development room. It never edits, publishes, or contacts a provider automatically.</p><textarea value={changeRequest} onChange={(event) => { setChangeRequest(event.target.value); setProposalState("idle"); }} aria-label="Requested Arthur change" />
        <div className="evolution-actions"><button className="outline-button" onClick={() => { setProposalState("prepared"); toast("Change proposal prepared.", { description: "No provider was contacted and no code was changed." }); }}>Prepare review <Play size={15} /></button><button className="primary-button" disabled={proposalState !== "prepared"} onClick={() => { setProposalState("approved"); toast("Staged proposal approved.", { description: "A connected development workspace must now show this scope, tests, and rollback checkpoint before implementation." }); }}>Approve staged proposal <ShieldCheck size={15} /></button></div>
        <div className={`proposal-state ${proposalState}`}><b>{proposalState === "idle" ? "No proposal is active." : proposalState === "prepared" ? "Proposal ready for your review." : "Approval recorded; implementation remains separately reviewed."}</b><span>{proposalState === "idle" ? "Arthur will create a scoped plan, provider route, affected screens, tests, and rollback point." : `Request: ${changeRequest}`}</span></div>
        {proposalState !== "idle" && <div className="proposal-detail"><div><span className="eyebrow">Proposed route</span><b>{proposal.route}</b><button className="text-button" onClick={() => openApiVault(proposal.category)}>Inspect required room</button></div><div><span className="eyebrow">Planned diff</span><ul>{proposal.diff.map((item) => <li key={item}>{item}</li>)}</ul></div><div><span className="eyebrow">Required checks</span><ul>{proposal.tests.map((item) => <li key={item}>{item}</li>)}</ul></div><div><span className="eyebrow">Rollback</span><p>{proposal.rollback}</p></div></div>}
      </section>

      <section className="autonomy-panel appearance-panel"><div className="section-heading"><div><span className="eyebrow">Personal format controls</span><h3>Change the way Arthur presents itself</h3></div><Palette size={19} /></div><p className="muted-copy">These local preview settings are reversible. You may also ask for these changes by voice; Arthur will show the affected setting before it applies it.</p>
        <div className="appearance-control"><b>Type scale</b><div>{(["standard", "large", "extra"] as const).map((value) => <button key={value} className={appearance.typeScale === value ? "selected" : ""} onClick={() => setAppearance({ ...appearance, typeScale: value })}>{value === "extra" ? "Extra large" : value}</button>)}</div></div>
        <div className="appearance-control"><b>Information density</b><div>{(["relaxed", "compact"] as const).map((value) => <button key={value} className={appearance.density === value ? "selected" : ""} onClick={() => setAppearance({ ...appearance, density: value })}>{value}</button>)}</div></div>
        <div className="appearance-control"><b>Motion</b><div>{(["calm", "reduced"] as const).map((value) => <button key={value} className={appearance.motion === value ? "selected" : ""} onClick={() => setAppearance({ ...appearance, motion: value })}>{value}</button>)}</div></div>
        <button className="outline-button reset-appearance" onClick={() => setAppearance({ typeScale: "standard", density: "relaxed", motion: "calm" })}><RotateCcw size={15} /> Restore default presentation</button>
      </section>
    </div>
    <button className="permissions-link" onClick={openPermissions}><ShieldCheck size={16} /> Review the permissions that govern each action class</button>
  </section>;
}
