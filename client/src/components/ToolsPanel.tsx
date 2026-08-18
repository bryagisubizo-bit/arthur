/**
 * Orbital Command Atelier: clipped operational cards, explicit consent labels, and no implied remote control.
 */
import { useState } from "react";
import {
  AppWindow,
  Camera,
  CheckCircle2,
  CircleAlert,
  Clock3,
  FileSearch,
  Gauge,
  History,
  Mic,
  MonitorCog,
  MousePointer2,
  Power,
  RefreshCw,
  Route,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  TimerReset,
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

export default function ToolsPanel() {
  const [activeRoute, setActiveRoute] = useState("Conversation");
  const [privacyMode, setPrivacyMode] = useState(false);
  const [automations, setAutomations] = useState(initialAutomations);
  const [history, setHistory] = useState(initialHistory);
  const active = routeModes.find((item) => item.name === activeRoute) ?? routeModes[0];

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

      <section className="automation-register">
        <div className="automation-heading"><div><span className="eyebrow">Automation registry / owned and auditable</span><h3>Named routines, never invisible rules.</h3><p>Each automation shows who owns it, when it may run, its limited scope, and whether it is currently paused.</p></div><button className="outline-button" onClick={() => { setAutomations((current) => current.map((item) => ({ ...item, enabled: false }))); toast("All preview automations paused."); }}><Power size={15} /> Pause all</button></div>
        <div className="automation-list">{automations.map((item) => <article className={`automation-row ${item.enabled ? "enabled" : "paused"}`} key={item.id}><span className="automation-mark"><Clock3 size={18} /></span><div className="automation-name"><b>{item.name}</b><small>Last state · {item.lastRun}</small></div><div><span>Trigger</span><b>{item.trigger}</b></div><div><span>Owner</span><b>{item.owner}</b></div><div><span>Scope</span><b>{item.scope}</b></div><button className={`automation-toggle ${item.enabled ? "on" : ""}`} onClick={() => toggleAutomation(item.id)}>{item.enabled ? "Active" : "Paused"}</button></article>)}</div>
      </section>

      <section className="activity-register">
        <div className="section-heading"><div><span className="eyebrow">Command history / local audit shape</span><h3>What Arthur understood, prepared, and deferred.</h3></div><button className="text-button" onClick={() => { setHistory([]); toast("Preview history cleared.", { description: "The production app should keep audit entries local and user-controlled." }); }}>Clear preview history</button></div>
        {history.length ? <div className="history-list">{history.map(([time, request, result, state]) => <article className="history-row" key={`${time}-${request}`}><span>{time}</span><div><b>{request}</b><small>{result}</small></div><em>{state}</em></article>)}</div> : <div className="history-empty"><History size={20} /><span>There are no preview history entries. New actions should always be visible before they are carried out.</span></div>}
      </section>
    </section>
  );
}
