/**
 * Orbital Command Atelier: clipped operational cards, explicit consent labels, and no implied remote control.
 */
import { useEffect, useRef, useState, type CSSProperties } from "react";
import { prepareSymptomGuidance, type SymptomGuidance } from "@/lib/symptomSupport";
import {
  AppWindow,
  Camera,
  CheckCircle2,
  CircleAlert,
  Clock3,
  FileSearch,
  Gauge,
  Hand,
  HeartPulse,
  History,
  Mic,
  MonitorCog,
  MousePointer2,
  MoveHorizontal,
  Power,
  RefreshCw,
  Route,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TimerReset,
  Trash2,
  Volume2,
  Webhook,
  Wifi,
  Workflow,
} from "lucide-react";
import { toast } from "sonner";

type RouteMode = {
  name: string;
  detail: string;
  status: string;
  tone: "live" | "reviewed" | "dependent" | "guarded";
  icon: typeof Route;
};

const routeModes: RouteMode[] = [
  { name: "Conversation", detail: "Interpret the request, language, and preferred response mode.", status: "Profile-led", tone: "live", icon: Sparkles },
  { name: "PC control", detail: "Use only reviewed Windows or WSL action templates.", status: "Desktop adapter", tone: "reviewed", icon: MonitorCog },
  { name: "Files & screen", detail: "Ask for a selected file or explicit screen-analysis consent.", status: "Consent gate", tone: "guarded", icon: FileSearch },
  { name: "Web research", detail: "Use an approved provider and return a spoken summary.", status: "Provider-dependent", tone: "dependent", icon: Search },
  { name: "Vision", detail: "Keep camera and identity checks separately authorised.", status: "Provider-dependent", tone: "dependent", icon: Camera },
  { name: "Automations", detail: "Run named, visible routines with a defined trigger and owner.", status: "Registry-controlled", tone: "reviewed", icon: Workflow },
  { name: "Sensitive actions", detail: "Pause for confirmation before any consequential change.", status: "Always confirm", tone: "guarded", icon: ShieldAlert },
];

const diagnostics = [
  ["AI connection", "Developer provider required", "dependent", Sparkles],
  ["Microphone input", "Desktop device adapter required", "dependent", Mic],
  ["Speaker output", "Desktop device adapter required", "dependent", Volume2],
  ["Internet path", "Available to reviewed research tools", "ready", Wifi],
  ["Profile vault", "Protected desktop credential store", "ready", ShieldCheck],
  ["Plugin registry", "Only declared permissions may load", "ready", Webhook],
  ["Smart-home bridge", "Detect and request Home Assistant consent", "dependent", Gauge],
] as const;

type Automation = { id: number; name: string; trigger: string; owner: string; scope: string; lastRun: string; enabled: boolean };

const initialAutomations: Automation[] = [
  { id: 1, name: "Workday brief", trigger: "Weekdays · 08:30", owner: "Profile owner", scope: "Calendar read + spoken brief", lastRun: "Not yet run", enabled: true },
  { id: 2, name: "Workstation guard", trigger: "Local threshold", owner: "Profile owner", scope: "Read-only telemetry", lastRun: "Preview only", enabled: true },
  { id: 3, name: "Focus-room lights", trigger: "Manual invocation", owner: "Profile owner", scope: "Home Assistant · ask first", lastRun: "Not connected", enabled: false },
];

const initialHistory = [
  ["09:41", "Workstation health", "Prepared a read-only health request", "Preview"],
  ["09:36", "Research request", "Held for provider and source approval", "Awaiting consent"],
  ["09:19", "Wake-word setting", "Listening remains locally controlled", "Local only"],
];

const smartHomeProviders = ["Home Assistant", "Philips Hue", "SmartThings", "Tuya", "MQTT adapter", "Other local hub"];

export default function ToolsPanel({ focusSpatial = false }: { focusSpatial?: boolean }) {
  const [activeRoute, setActiveRoute] = useState("Conversation");
  const [privacyMode, setPrivacyMode] = useState(false);
  const [automations, setAutomations] = useState(initialAutomations);
  const [history, setHistory] = useState(initialHistory);
  const [smartHomeProvider, setSmartHomeProvider] = useState("Home Assistant");
  const [discoveryReviewEnabled, setDiscoveryReviewEnabled] = useState(false);
  const [spatialCards, setSpatialCards] = useState(["Research field", "System diagnostics", "Private note", "Voice signal", "Smart-home review"]);
  const [selectedSpatialCard, setSelectedSpatialCard] = useState("Research field");
  const [lastDiscardedCard, setLastDiscardedCard] = useState<{ label: string; index: number } | null>(null);
  const [spatialZoom, setSpatialZoom] = useState(100);
  const [gestureConsent, setGestureConsent] = useState(false);
  const [spatialPasswordReady, setSpatialPasswordReady] = useState(false);
  const [spatialFaceReady, setSpatialFaceReady] = useState(false);
  const [spatialUnlocked, setSpatialUnlocked] = useState(false);
  const [spatialAccessMethod, setSpatialAccessMethod] = useState<"" | "password" | "windows_hello" | "local_camera_face">("");
  const [faceCameraTestStatus, setFaceCameraTestStatus] = useState<"idle" | "passed">("idle");
  const [faceAudioCue, setFaceAudioCue] = useState(false);
  const [faceFailures, setFaceFailures] = useState(0);
  const [faceCooldownSeconds, setFaceCooldownSeconds] = useState(0);
  const [symptomText, setSymptomText] = useState("");
  const [symptomGuidance, setSymptomGuidance] = useState<SymptomGuidance | null>(null);
  const dragCard = useRef<string | null>(null);
  const touchOrigin = useRef<{ x: number; y: number } | null>(null);
  const spatialWorkspaceRef = useRef<HTMLElement | null>(null);
  const active = routeModes.find((item) => item.name === activeRoute) ?? routeModes[0];

  useEffect(() => {
    if (!faceCooldownSeconds) return;
    const timer = window.setInterval(() => setFaceCooldownSeconds((seconds) => Math.max(0, seconds - 1)), 1000);
    return () => window.clearInterval(timer);
  }, [faceCooldownSeconds]);

  useEffect(() => {
    if (!focusSpatial) return;
    const frame = window.requestAnimationFrame(() => {
      spatialWorkspaceRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [focusSpatial]);

  const previewFaceFailure = () => {
    if (faceCooldownSeconds) return;
    const nextAttempts = faceFailures + 1;
    setFaceFailures(nextAttempts);
    if (nextAttempts >= 3) {
      setFaceCooldownSeconds(60);
      toast.error("Preview face access is temporarily locked.", { description: "The installed app uses the same short local cooldown after repeated completed non-matches. It retains no failed frame." });
      return;
    }
    toast("Preview non-match recorded.", { description: `Attempt ${nextAttempts} of 3. The installed app stores only a short local counter, never a failed camera frame.` });
  };

  const moveSelection = (direction: number) => {
    if (!spatialCards.length) return;
    const index = Math.max(0, spatialCards.indexOf(selectedSpatialCard));
    const next = spatialCards[(index + direction + spatialCards.length) % spatialCards.length];
    setSelectedSpatialCard(next);
  };

  const discardSelectedSpatialCard = () => {
    const index = spatialCards.indexOf(selectedSpatialCard);
    if (index < 0) return toast.error("Select an Arthur workspace card first.");
    const label = spatialCards[index];
    setLastDiscardedCard({ label, index });
    const remaining = spatialCards.filter((item) => item !== label);
    setSpatialCards(remaining);
    setSelectedSpatialCard(remaining[Math.min(index, Math.max(remaining.length - 1, 0))] ?? "");
    toast("Card removed from the current preview layout.", { description: "It was not deleted and can be restored with Undo discard." });
  };

  const restoreDiscardedSpatialCard = () => {
    if (!lastDiscardedCard) return;
    setSpatialCards((current) => [...current.slice(0, lastDiscardedCard.index), lastDiscardedCard.label, ...current.slice(lastDiscardedCard.index)]);
    setSelectedSpatialCard(lastDiscardedCard.label);
    setLastDiscardedCard(null);
    toast("Workspace card restored.");
  };

  const reorderSpatialCard = (target: string) => {
    const source = dragCard.current;
    if (!source || source === target) return;
    setSpatialCards((current) => {
      const from = current.indexOf(source);
      const to = current.indexOf(target);
      const next = [...current];
      next.splice(from, 1);
      next.splice(to, 0, source);
      return next;
    });
    dragCard.current = null;
  };

  const toggleAutomation = (id: number) => {
    setAutomations((current) => current.map((item) => item.id === id ? { ...item, enabled: !item.enabled } : item));
    toast("Automation registry updated.", { description: "The browser preview changes display state only." });
  };

  const togglePrivacy = () => {
    setPrivacyMode((current) => !current);
    toast(privacyMode ? "Privacy lock released in preview." : "Privacy lock engaged in preview.", { description: privacyMode ? "Configured capabilities remain individually reviewable." : "Microphone, camera, cloud tools, memory, web access, and screen analysis are marked unavailable." });
  };

  return (
    <section className="tools-layout">
      {!focusSpatial && <>
      <header className="tools-hero">
        <div>
          <span className="eyebrow">Tool-routing workspace / inspected intent</span>
          <h2>Every request has a visible route.</h2>
          <p>Arthur classifies the work before it acts: conversation, approved desktop tooling, selected files, research, vision, an owned automation, or a confirmation gate.</p>
        </div>
        <div className="routing-seal"><Route size={26} /><span>ROUTE<br />BEFORE ACT</span></div>
      </header>

      <section className="route-console" aria-label="Arthur tool-routing console">
        <div className="route-lanes">
          {routeModes.map((item, index) => {
            const Icon = item.icon;
            return <button key={item.name} className={`route-lane ${activeRoute === item.name ? "active" : ""}`} onClick={() => setActiveRoute(item.name)} aria-pressed={activeRoute === item.name}><span className="route-index">0{index + 1}</span><Icon size={16} /><span>{item.name}</span><i className={`route-pulse ${item.tone}`} /></button>;
          })}
        </div>
        <article className={`route-inspector ${active.tone}`}>
          <span className="eyebrow">Selected path / {active.status}</span>
          <h3>{active.name}</h3>
          <p>{active.detail}</p>
          <div><ShieldCheck size={17} /><span>{active.tone === "guarded" ? "Arthur asks first; no exception is inferred from natural language." : active.tone === "dependent" ? "The capability stays unavailable until its approved provider is configured." : "Arthur records the proposed scope before the desktop app acts."}</span></div>
        </article>
      </section>

      <section className={`privacy-lock ${privacyMode ? "locked" : ""}`}>
        <div className="privacy-lock-icon"><ShieldAlert size={23} /></div>
        <div><span className="eyebrow">One-switch privacy lock</span><h3>{privacyMode ? "Private mode is holding all sensitive channels." : "A single stop for sensitive channels."}</h3><p>{privacyMode ? "Microphone, camera, cloud AI, web research, learning memory, and screen analysis are unavailable until you release the lock." : "Use the lock before a private meeting, screen-share, or sensitive task. It does not delete your settings."}</p></div>
        <button aria-pressed={privacyMode} className={`switch privacy-switch ${privacyMode ? "on" : ""}`} onClick={togglePrivacy}><span /></button>
      </section>

      <div className="tools-pair">
        <section className="tools-panel app-control-panel">
          <div className="section-heading"><div><span className="eyebrow">Application management</span><h3>Explicit Windows adapter</h3></div><AppWindow size={19} /></div>
          <p className="tools-intro">Arthur may propose launch, focus, close, restart, and scroll actions only through a reviewed Windows adapter. None of these controls run from this preview.</p>
          <div className="app-control-list">
            {[["Launch approved app", AppWindow], ["Focus current window", MousePointer2], ["Restart approved app", RefreshCw], ["Close application", Power]].map(([label, Icon]) => {
              const ActionIcon = Icon as typeof AppWindow;
              return <button key={label as string} className="app-control-row" onClick={() => toast(`${label} is a desktop-only placeholder.`, { description: "The installed app would identify the target and ask for confirmation where needed." })}><span><ActionIcon size={17} /></span><b>{label as string}</b><small>Requires reviewed target</small></button>;
            })}
          </div>
        </section>

        <section className="tools-panel diagnostics-panel">
          <div className="section-heading"><div><span className="eyebrow">Self-diagnostics</span><h3>Readiness, not surveillance</h3></div><TimerReset size={19} /></div>
          <p className="tools-intro">This dashboard describes what the desktop app should check. It does not access hardware, networks, or provider accounts in a browser.</p>
          <div className="diagnostic-list">{diagnostics.map(([label, detail, state, Icon]) => <div className="diagnostic-row" key={label}><span className={`diagnostic-icon ${state}`}><Icon size={15} /></span><div><b>{label}</b><small>{detail}</small></div>{state === "ready" ? <CheckCircle2 size={17} className="diagnostic-check" /> : <CircleAlert size={17} className="diagnostic-wait" />}</div>)}</div>
          <button className="outline-button full" onClick={() => toast("Preview diagnostic completed.", { description: "Live checks belong to the installed desktop assistant after permissions are granted." })}>Run preview check <TimerReset size={15} /></button>
        </section>
      </div>

      <section className="tools-panel smart-home-review">
        <div className="section-heading"><div><span className="eyebrow">Smart-home / review before connection</span><h3>Choose a hub, then approve its declared scope.</h3></div><Gauge size={19} /></div>
        <p className="tools-intro">This preview does not scan a local network, contact a hub, enumerate devices, or control anything. The desktop app can only use an explicitly configured hub API after its endpoint, developer credential, and one selected action have been reviewed.</p>
        <div className="smart-home-options" role="group" aria-label="Smart-home provider choice">
          {smartHomeProviders.map((provider) => <button key={provider} className={smartHomeProvider === provider ? "active" : ""} onClick={() => setSmartHomeProvider(provider)} aria-pressed={smartHomeProvider === provider}>{provider}</button>)}
        </div>
        <label className="review-choice"><input type="checkbox" checked={discoveryReviewEnabled} onChange={(event) => setDiscoveryReviewEnabled(event.target.checked)} /> Permit a later review of this hub’s own authorised-device list. It does not begin discovery.</label>
        <div className="smart-home-actions"><button className="outline-button" onClick={() => toast("Connection proposal prepared.", { description: `${smartHomeProvider} remains disconnected. Add its endpoint and developer-owned credential in the API Vault, then review the device scope in the installed desktop app.` })}>Prepare connection proposal <Route size={15} /></button><button className="outline-button" onClick={() => toast(discoveryReviewEnabled ? "Authorised-device review is eligible after configuration." : "Enable the separate review option first.", { description: "Arthur never performs network scans or automatic device discovery." })}>Review discovery boundary <ShieldCheck size={15} /></button></div>
      </section>

      <section className="tools-panel personalisation-review">
        <div className="section-heading"><div><span className="eyebrow">Personalisation / own data only</span><h3>Samples are chosen, local, and revocable.</h3></div><Camera size={19} /></div>
        <p className="tools-intro">Arthur will not collect every camera or microphone detail. A user can deliberately select a local photo or a short own-voice sample in the desktop app, set a retention period, and review a separate request before a configured developer-owned provider receives anything.</p>
        <div className="smart-home-actions"><button className="outline-button" onClick={() => toast("Camera-style proposal requires an explicit local file choice.", { description: "The preview never opens a camera or accesses images." })}>Review camera-style boundary <Camera size={15} /></button><button className="outline-button" onClick={() => toast("Own-voice proposal requires fresh consent and an imported local sample.", { description: "Arthur cannot clone another person’s voice and never uploads a sample from this preview." })}>Review own-voice boundary <Mic size={15} /></button></div>
      </section>
      </>}

      <section ref={spatialWorkspaceRef} className="tools-panel spatial-workspace-review">
        <div className="section-heading"><div><span className="eyebrow">Touch & spatial workspace / Arthur only</span><h3>Arrange the field with direct touch.</h3></div><Hand size={19} /></div>
        <p className="tools-intro">On a touch screen, swipe this card field left or right to choose an Arthur card, drag cards to change their order, and pinch or use the controls to adjust the in-app canvas scale. These inputs never control another Windows application or move the system pointer.</p>
        <div className={`spatial-room-access ${spatialUnlocked ? "unlocked" : "locked"}`}>
          <div><span className="eyebrow">Protected room / preview only</span><h4>{spatialUnlocked ? "Unlocked for this preview session" : "Locked until local access is verified"}</h4><p>Choose exactly one installed-app access method: a salted local password verifier, OS-managed Windows Hello, or experimental local-camera face access. The camera method requires deliberate enrolment and a recovery secret, displays a camera-active preview, stores no raw image or video, and keeps only an encrypted local model. It is not equivalent to Windows Hello.</p></div>
          <div className="spatial-room-actions">
            <button className="outline-button" onClick={() => { setSpatialAccessMethod("password"); setSpatialPasswordReady(true); setSpatialFaceReady(false); setSpatialUnlocked(false); setGestureConsent(false); toast("Password-only access is represented in this preview.", { description: "In the installed app, you choose and confirm a 10+ character password; its plaintext is never saved in Arthur’s configuration." }); }}>Use password only</button>
            <button className="outline-button" onClick={() => { setSpatialAccessMethod("windows_hello"); setSpatialPasswordReady(false); setSpatialFaceReady(false); setSpatialUnlocked(false); setGestureConsent(false); toast("Windows Hello-only access is represented in this preview.", { description: "The installed app asks Windows to verify enrolled face or PIN. Arthur requests no room password and never opens a camera for this check." }); }}>Use Windows Hello only</button>
            <button className="outline-button" onClick={() => { setSpatialAccessMethod("local_camera_face"); setSpatialPasswordReady(false); setSpatialFaceReady(true); setSpatialUnlocked(false); setGestureConsent(false); toast("Local camera face-access is represented in this preview.", { description: "The installed app requires explicit camera consent, enrolment, an encrypted local model, and a recovery secret. This browser preview never opens a camera." }); }}>Use local camera face access</button>
            <button className="primary-button compact" onClick={() => { const isReady = spatialAccessMethod === "password" ? spatialPasswordReady : spatialAccessMethod === "local_camera_face" ? spatialFaceReady : spatialAccessMethod === "windows_hello"; if (!isReady) { toast.error("Choose and complete one room access method first.", { description: "Select password-only, Windows Hello-only, or local-camera face access. Arthur never silently enables a biometric check." }); return; } if (spatialAccessMethod === "local_camera_face" && faceCooldownSeconds) { toast.error("Local face access is temporarily locked in this preview.", { description: `Wait about ${faceCooldownSeconds} seconds or use the recovery-secret reset path. No frame was retained.` }); return; } setSpatialUnlocked(true); toast("Protected Spatial room unlocked in preview.", { description: spatialAccessMethod === "windows_hello" ? "The Windows app requires OS-managed Windows Hello; this browser preview does neither." : spatialAccessMethod === "local_camera_face" ? "The Windows app runs an explicit visible local camera check; this browser preview does not access a camera." : "The Windows app requires the local room password; this browser preview does not retain one." }); }}>{spatialUnlocked ? "Room unlocked" : "Unlock room"}</button>
            <button className="text-button" disabled={!spatialUnlocked} onClick={() => { setSpatialUnlocked(false); setGestureConsent(false); toast("Preview Spatial room locked."); }}>Lock room</button>
          </div>
          <div className="spatial-install-line"><b>Optional installation is always manual.</b><code>pip install -r requirements-gesture-optional.txt</code><button className="text-button" onClick={() => { void navigator.clipboard?.writeText("pip install -r requirements-gesture-optional.txt"); toast("Optional gesture command copied.", { description: "Arthur never installs packages automatically. Review it, then run it yourself in the Arthur source folder." }); }}>Copy gesture command</button><code>pip install -r requirements-face-access-optional.txt</code><button className="text-button" onClick={() => { void navigator.clipboard?.writeText("pip install -r requirements-face-access-optional.txt"); toast("Optional local face-access command copied.", { description: "Review and run it yourself only if you want experimental on-device camera face access. Arthur will then ask for separate enrolment consent." }); }}>Copy face-access command</button></div>
          <div className="face-safeguard-panel" aria-label="Local camera face-access safeguards preview">
            <div><span className="eyebrow">Camera safeguards / Windows prototype</span><h4>Test the camera deliberately. Pause repeated non-matches.</h4><p>{faceCameraTestStatus === "passed" ? "Readiness test represented: the installed app shows a camera-active preview, confirms frames are available, and immediately discards them." : "Run the local camera readiness test before enrolment if you want to confirm Windows permission, the shutter, and the selected camera. This browser preview never opens a camera."}</p></div>
            <div className="face-safeguard-actions"><button className="outline-button" onClick={() => { setFaceCameraTestStatus("passed"); toast("Camera readiness test represented in preview.", { description: "On Windows, it opens only after your confirmation, shows a camera-active preview, and stores no image, video, model, or failed frame." }); }}>Preview camera readiness</button><button className={`outline-button ${faceAudioCue ? "active" : ""}`} aria-pressed={faceAudioCue} onClick={() => { setFaceAudioCue((enabled) => !enabled); toast(faceAudioCue ? "Preview accessibility cue muted." : "Preview accessibility cue enabled.", { description: "The installed app uses only a local system tone for camera activation and verification outcomes. It does not speak or reveal biometric details." }); }}><Volume2 size={15} /> {faceAudioCue ? "Cue enabled" : "Enable audio cue"}</button><button className="outline-button" disabled={Boolean(faceCooldownSeconds)} onClick={previewFaceFailure}>Preview failed face check</button></div>
            <div className={`face-lockout-state ${faceCooldownSeconds ? "locked" : ""}`} role="status"><TimerReset size={16} /><span>{faceCooldownSeconds ? `Temporary local lockout: try again in about ${faceCooldownSeconds} seconds, or use the recovery secret to erase and reset local face access.` : faceFailures ? `${faceFailures} preview non-match${faceFailures === 1 ? "" : "es"} recorded. A 60-second local cooldown begins after 3 completed non-matches.` : "No recent preview non-matches. The Windows app retains no failed frame; it uses only a short local counter/timer if needed."}</span><button className="text-button" onClick={() => { setFaceFailures(0); setFaceCooldownSeconds(0); toast("Preview recovery-reset path represented.", { description: "The installed app requires the recovery secret before erasing the encrypted local model and clearing its cooldown." }); }}>Preview recovery reset</button></div>
          </div>
        </div>
        <div className="spatial-canvas" aria-disabled={!spatialUnlocked} style={{ "--spatial-scale": spatialZoom / 100 } as CSSProperties} onTouchStart={(event) => { if (!spatialUnlocked) return; const touch = event.touches[0]; touchOrigin.current = touch ? { x: touch.clientX, y: touch.clientY } : null; }} onTouchEnd={(event) => { if (!spatialUnlocked) return; const origin = touchOrigin.current; const touch = event.changedTouches[0]; if (origin && touch && Math.abs(touch.clientX - origin.x) > 56) { moveSelection(touch.clientX > origin.x ? -1 : 1); toast("Touch swipe selected a neighbouring Arthur workspace card."); } touchOrigin.current = null; }} onWheel={(event) => { if (spatialUnlocked && event.ctrlKey) { event.preventDefault(); setSpatialZoom((current) => Math.min(150, Math.max(70, current + (event.deltaY < 0 ? 5 : -5)))); } }}>
          <div className="spatial-canvas-meta"><span><MoveHorizontal size={15} /> {selectedSpatialCard || "No card selected"}</span><span>{spatialZoom}% canvas</span></div>
          <div className="spatial-card-strip" aria-label="Touch-reorderable Arthur workspace cards">{spatialCards.map((card) => <button key={card} disabled={!spatialUnlocked} draggable={spatialUnlocked} onDragStart={() => { dragCard.current = card; }} onDragOver={(event) => { if (spatialUnlocked) event.preventDefault(); }} onDrop={() => reorderSpatialCard(card)} onClick={() => setSelectedSpatialCard(card)} className={`spatial-card ${selectedSpatialCard === card ? "active" : ""}`} aria-pressed={selectedSpatialCard === card}><span>{String(spatialCards.indexOf(card) + 1).padStart(2, "0")}</span><b>{card}</b></button>)}</div>
        </div>
        <div className="spatial-controls"><button className="outline-button" disabled={!spatialUnlocked} onClick={() => moveSelection(-1)}>Previous card</button><button className="outline-button" disabled={!spatialUnlocked} onClick={() => moveSelection(1)}>Next card</button><label>Zoom<input disabled={!spatialUnlocked} type="range" min="70" max="150" value={spatialZoom} onChange={(event) => setSpatialZoom(Number(event.target.value))} /></label><button className="outline-button" disabled={!spatialUnlocked || !selectedSpatialCard} onClick={discardSelectedSpatialCard}><Trash2 size={15} /> Discard selected</button><button className="text-button" disabled={!spatialUnlocked || !lastDiscardedCard} onClick={restoreDiscardedSpatialCard}>Undo discard</button></div>
        <div className="gesture-consent-callout"><Hand size={18} /><div><b>Camera-based air gestures are optional and off.</b><p>Enable only in the Windows prototype after manually installing the optional requirements, selecting a local camera, unlocking this room, and accepting the visible local-only camera indicator. The preview neither opens a camera nor reads video.</p></div><label className="review-choice"><input disabled={!spatialUnlocked} type="checkbox" checked={gestureConsent} onChange={(event) => setGestureConsent(event.target.checked)} /> I want to review local air-gesture consent.</label><button className="outline-button" disabled={!spatialUnlocked} onClick={() => toast(gestureConsent ? "Desktop consent proposal prepared." : "Confirm the separate consent acknowledgement first.", { description: gestureConsent ? "The installed prototype processes transient local hand landmarks only; it does not retain video or biometric templates." : "A camera never opens from this preview." })}>Prepare consent review</button></div>
      </section>

      {!focusSpatial && <>
      <section className="tools-panel symptom-support-review">
        <div className="section-heading"><div><span className="eyebrow">Health support / guidance, not diagnosis</span><h3>Prepare clear information for appropriate care.</h3></div><HeartPulse size={19} /></div>
        <p className="tools-intro">Arthur cannot diagnose a disease or replace a clinician. It can provide cautious information and encourage urgent care when a description contains potential warning signs. Your text is not saved in this preview.</p>
        <div className="symptom-emergency-note"><CircleAlert size={17} /><span>If there is severe chest pain, trouble breathing, stroke-like symptoms, severe allergic reaction, loss of consciousness, severe bleeding, or immediate danger, contact local emergency services now.</span></div>
        <label className="symptom-entry">How are you feeling?<textarea value={symptomText} onChange={(event) => setSymptomText(event.target.value)} placeholder="Describe symptoms, when they began, and whether they are worsening. Arthur will not label a disease." /></label>
        <div className="smart-home-actions"><button className="primary-button compact" onClick={() => setSymptomGuidance(prepareSymptomGuidance(symptomText))}>Prepare cautious guidance</button><button className="outline-button" onClick={() => { setSymptomText(""); setSymptomGuidance(null); }}>Clear private text</button></div>
        {symptomGuidance && <div className={`symptom-guidance ${symptomGuidance.urgency.replace(/\s+/g, "-")}`} role="status"><span className="eyebrow">{symptomGuidance.urgency}</span><h4>{symptomGuidance.heading}</h4><p>{symptomGuidance.summary}</p><b>Next step: {symptomGuidance.nextStep}</b></div>}
      </section>

      <section className="automation-register">
        <div className="automation-heading"><div><span className="eyebrow">Automation registry / owned and auditable</span><h3>Named routines, never invisible rules.</h3><p>Each automation shows who owns it, when it may run, its limited scope, and whether it is currently paused.</p></div><button className="outline-button" onClick={() => { setAutomations((current) => current.map((item) => ({ ...item, enabled: false }))); toast("All preview automations paused."); }}><Power size={15} /> Pause all</button></div>
        <div className="automation-list">{automations.map((item) => <article className={`automation-row ${item.enabled ? "enabled" : "paused"}`} key={item.id}><span className="automation-mark"><Clock3 size={18} /></span><div className="automation-name"><b>{item.name}</b><small>Last state · {item.lastRun}</small></div><div><span>Trigger</span><b>{item.trigger}</b></div><div><span>Owner</span><b>{item.owner}</b></div><div><span>Scope</span><b>{item.scope}</b></div><button className={`automation-toggle ${item.enabled ? "on" : ""}`} onClick={() => toggleAutomation(item.id)}>{item.enabled ? "Active" : "Paused"}</button></article>)}</div>
      </section>

      <section className="activity-register">
        <div className="section-heading"><div><span className="eyebrow">Command history / local audit shape</span><h3>What Arthur understood, prepared, and deferred.</h3></div><button className="text-button" onClick={() => { setHistory([]); toast("Preview history cleared.", { description: "The production app should keep audit entries local and user-controlled." }); }}>Clear preview history</button></div>
        {history.length ? <div className="history-list">{history.map(([time, request, result, state]) => <article className="history-row" key={`${time}-${request}`}><span>{time}</span><div><b>{request}</b><small>{result}</small></div><em>{state}</em></article>)}</div> : <div className="history-empty"><History size={20} /><span>There are no preview history entries. New actions should always be visible before they are carried out.</span></div>}
      </section>
      </>}
    </section>
  );
}
