/**
 * Orbital Command Atelier: asymmetric command canvas, cobalt instrumentation, and explicit consent states.
 */
import { useMemo, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  AudioLines,
  BellRing,
  Bot,
  ChevronRight,
  CircleGauge,
  CircleHelp,
  Command,
  Crosshair,
  Cpu,
  Database,
  Fingerprint,
  FolderCog,
  Globe2,
  KeyRound,
  Languages,
  LockKeyhole,
  Mic,
  MonitorCog,
  Music2,
  Network,
  Play,
  Plus,
  Power,
  Radar,
  Search,
  Settings2,
  ShieldCheck,
  Sparkles,
  TerminalSquare,
  UploadCloud,
  UserRound,
  Volume2,
  Waves,
  X,
} from "lucide-react";
import { toast } from "sonner";

type Section = "command" | "voice" | "persona" | "api" | "permissions" | "updates";
type ProviderCard = [string, string, string, string];
type CommandPlanPreview = { intent: string; summary: string; command: string; risk: "low" | "medium" | "blocked"; confirmation: boolean; allowed: boolean; reason?: string };

const heroImage = "/manus-storage/arthur-hero-atmosphere_eca500cb.png";
const analyticsImage = "/manus-storage/arthur-analytics-orbit_3b540420.png";
const voiceImage = "/manus-storage/arthur-voice-signal_cd52a5c8.png";
const markImage = "/manus-storage/arthur-mark_c216fbf0.png";

const providerCards: ProviderCard[] = [
  ["Main intelligence", "OpenAI", "Conversation, planning & tool selection", "openai-key"],
  ["Secondary reasoning", "Anthropic", "Long-form analysis & research checks", "anthropic-key"],
  ["Voice pipeline", "OpenAI Audio", "Speech-to-text and spoken response", "voice-key"],
  ["Wake word", "openWakeWord", "Local ‘Arthur’ listening trigger", "wake-key"],
  ["Web research", "SerpAPI", "Private summaries without opening a browser", "search-key"],
  ["Identity vision", "Luxand", "Optional local profile verification", "vision-key"],
  ["Accounts", "Supabase", "Browser registration and profile sync", "account-key"],
  ["Music", "Piped-compatible", "User-authorised music discovery and playback", "music-key"],
];

const nav = [
  ["command", Command, "Command desk"],
  ["voice", AudioLines, "Voice studio"],
  ["persona", Bot, "Conduct & memory"],
  ["api", KeyRound, "API vault"],
  ["permissions", ShieldCheck, "Permissions"],
  ["updates", UploadCloud, "Updates"],
] as const;

function planCommandPreview(request: string): CommandPlanPreview {
  const input = request.trim().toLowerCase();
  const blocked = ["hack", "breach", "exploit", "keylogger", "steal password", "dump credentials", "disable antivirus", "disable firewall", "reverse shell", "scan network", "scan public", "ransomware", "phishing"];
  if (!input) return { intent: "empty", summary: "Arthur needs a specific approved computer task.", command: "—", risk: "blocked", confirmation: false, allowed: false, reason: "No request supplied." };
  if (blocked.some((term) => input.includes(term))) return { intent: "blocked request", summary: "Arthur will not prepare intrusion, evasion, credential, or attack activity.", command: "—", risk: "blocked", confirmation: false, allowed: false, reason: "Unauthorized or harmful system access is not available." };
  const isLinux = /\b(kali|linux|wsl)\b/.test(input);
  const templates: Array<[string[], Omit<CommandPlanPreview, "risk" | "confirmation" | "allowed">]> = isLinux
    ? [
        [["system status", "system information"], { intent: "local WSL diagnostics", summary: "Inspect the configured local WSL/Linux system.", command: "wsl.exe -d <approved-distro> -- uname -a" }],
        [["disk space", "storage status"], { intent: "local WSL storage", summary: "Inspect storage in the configured local WSL/Linux system.", command: "wsl.exe -d <approved-distro> -- df -h" }],
        [["memory", "ram"], { intent: "local WSL memory", summary: "Inspect memory use in the configured local WSL/Linux system.", command: "wsl.exe -d <approved-distro> -- free -h" }],
        [["network status", "ip address"], { intent: "local WSL network", summary: "Inspect local WSL/Linux network addresses.", command: "wsl.exe -d <approved-distro> -- ip addr" }],
        [["list processes", "running apps"], { intent: "local WSL processes", summary: "List local WSL/Linux processes.", command: "wsl.exe -d <approved-distro> -- ps aux" }],
      ]
    : [
        [["system status", "computer status", "system information"], { intent: "windows system information", summary: "Collect Windows system information.", command: "systeminfo" }],
        [["who am i", "current user"], { intent: "current Windows user", summary: "Show the signed-in Windows account.", command: "whoami" }],
        [["ip address", "network address", "network status"], { intent: "Windows network information", summary: "Show local network adapter configuration.", command: "ipconfig" }],
        [["list processes", "running apps", "running applications", "what is running"], { intent: "Windows process information", summary: "List running Windows processes.", command: "tasklist" }],
        [["disk space", "storage status", "drive space"], { intent: "Windows storage information", summary: "Show available Windows file-system space.", command: "powershell.exe -NoProfile -Command Get-PSDrive -PSProvider FileSystem" }],
        [["check internet", "test internet", "internet connection"], { intent: "internet check", summary: "Perform one basic connectivity check.", command: "ping -n 1 1.1.1.1" }],
      ];
  if (["lock computer", "lock pc", "lock my computer"].some((term) => input.includes(term))) return { intent: "lock workstation", summary: "Lock this Windows session. Arthur requires your explicit approval before taking this action.", command: "rundll32.exe user32.dll,LockWorkStation", risk: "medium", confirmation: true, allowed: true };
  for (const [phrases, template] of templates) if (phrases.some((term) => input.includes(term))) return { ...template, risk: "low", confirmation: false, allowed: true };
  return { intent: "unreviewed request", summary: "Arthur has no reviewed command template for that request.", command: "—", risk: "blocked", confirmation: false, allowed: false, reason: "Add and test an explicit template in the developer command registry; raw generated shell text is never run." };
}

function StatusPill({ tone = "blue", children }: { tone?: "blue" | "green" | "amber" | "gray"; children: React.ReactNode }) {
  return <span className={`status-pill ${tone}`}><span className="status-dot" />{children}</span>;
}

function Metric({ label, value, unit, icon: Icon, delta }: { label: string; value: string; unit: string; icon: typeof Cpu; delta: string }) {
  return (
    <article className="metric-card">
      <div className="metric-top"><span className="metric-icon"><Icon size={17} /></span><span>{label}</span><span className="metric-delta">{delta}</span></div>
      <div className="metric-value">{value}<small>{unit}</small></div>
      <div className="metric-track"><span style={{ width: `${Math.min(Number(value) || 48, 92)}%` }} /></div>
    </article>
  );
}

function SetupModal({ close, save }: { close: () => void; save: (name: string, title: string, language: string) => void }) {
  const [name, setName] = useState("Aline");
  const [title, setTitle] = useState("Madam");
  const [language, setLanguage] = useState("Kinyarwanda");
  const [pronunciation, setPronunciation] = useState("Ah-lee-neh");
  const [step, setStep] = useState(1);
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Arthur first-run setup">
      <div className="setup-modal">
        <button className="icon-button close-modal" onClick={close} aria-label="Close setup"><X size={18} /></button>
        <div className="eyebrow">Arthur / First-run authorization</div>
        <h2>Let us make this feel personal.</h2>
        <p className="muted-copy">Arthur keeps these preferences within your profile. You remain in charge of what it remembers and what it may control.</p>
        <div className="setup-steps"><span className={step >= 1 ? "active" : ""}>01 Identity</span><span className={step >= 2 ? "active" : ""}>02 Voice</span><span className={step >= 3 ? "active" : ""}>03 Consent</span></div>
        {step === 1 && <div className="setup-fields"><label>What should Arthur call you?<input value={name} onChange={(e) => setName(e.target.value)} /></label><label>Preferred title<select value={title} onChange={(e) => setTitle(e.target.value)}><option>Madam</option><option>Sir</option><option>Captain</option><option>Friend</option></select></label></div>}
        {step === 2 && <div className="setup-fields"><label>Native language<select value={language} onChange={(e) => setLanguage(e.target.value)}><option>Kinyarwanda</option><option>English</option><option>French</option><option>Kiswahili</option></select></label><label>How do I pronounce your name?<input value={pronunciation} onChange={(e) => setPronunciation(e.target.value)} /></label><div className="language-strip"><Languages size={17} /><span>Arthur will switch naturally across Kinyarwanda, English, French, and Kiswahili when you do.</span></div></div>}
        {step === 3 && <div className="consent-box"><ShieldCheck size={24} /><div><strong>Explicit control is enabled.</strong><p>Arthur may suggest actions, but it will ask before sending, purchasing, deleting, installing, or making administrator changes.</p></div></div>}
        <div className="modal-actions"><button className="text-button" onClick={() => setStep(Math.max(1, step - 1))}>{step === 1 ? "" : "Back"}</button>{step < 3 ? <button className="primary-button" onClick={() => setStep(step + 1)}>Continue <ChevronRight size={17} /></button> : <button className="primary-button" onClick={() => save(name, title, language)}>Authorize Arthur <ShieldCheck size={17} /></button>}</div>
      </div>
    </div>
  );
}

function IntegrationModal({ close, save }: { close: () => void; save: (card: ProviderCard) => void }) {
  const [name, setName] = useState("");
  const [baseUrl, setBaseUrl] = useState("");
  const [auth, setAuth] = useState("API key");
  const addIntegration = () => {
    if (!name.trim() || !baseUrl.startsWith("https://")) return toast.error("Enter an integration name and an HTTPS base URL.");
    save([`Custom · ${name.trim()}`, name.trim(), `${auth} placeholder • ${baseUrl}`, `${name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-key`]);
    toast.success(`${name.trim()} was added as an unverified placeholder.`, { description: "This preview does not save or contact the API." });
    close();
  };
  return <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Add custom Arthur integration"><div className="setup-modal integration-modal"><button className="icon-button close-modal" onClick={close} aria-label="Close integration setup"><X size={18} /></button><div className="eyebrow">Developer API vault / add integration</div><h2>Describe the connection first.</h2><p className="muted-copy">Arthur will only use a new provider after a developer enters its approved configuration and enables the capability.</p><div className="setup-fields"><label>Integration name<input value={name} onChange={(event) => setName(event.target.value)} placeholder="For example, Calendar service" /></label><label>HTTPS base URL<input value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} placeholder="https://api.example.com" /></label><label>Authentication type<select value={auth} onChange={(event) => setAuth(event.target.value)}><option>API key</option><option>OAuth 2.0</option><option>Bearer token</option><option>Local network token</option></select></label><div className="consent-box"><KeyRound size={22} /><div><strong>Secrets remain local to the administrator.</strong><p>The real desktop app stores the credential in protected credential storage; this preview keeps it empty.</p></div></div></div><div className="modal-actions"><button className="text-button" onClick={close}>Cancel</button><button className="primary-button" onClick={addIntegration}>Add unverified provider <Plus size={16} /></button></div></div></div>;
}

function WakeWordModal({ close }: { close: () => void }) {
  const [approved, setApproved] = useState(false);
  const [trayListening, setTrayListening] = useState(true);
  const requestInstall = () => {
    if (!approved) return toast.error("Confirm the installation consent first.");
    toast.success("Approval recorded for the desktop installer.", { description: "This browser preview never opens Command Prompt or runs a command." });
  };
  return <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="openWakeWord setup"><div className="setup-modal wakeword-modal"><button className="icon-button close-modal" onClick={close} aria-label="Close wake word setup"><X size={18} /></button><div className="eyebrow">Local wake word / consent gate</div><h2>Install listening only with approval.</h2><p className="muted-copy">Arthur should ask before the Windows desktop app opens Command Prompt and installs the optional local listener.</p><div className="command-preview"><TerminalSquare size={18} /><code>pip install openwakeword</code></div><label className="check-row wakeword-consent"><input type="checkbox" checked={approved} onChange={(event) => setApproved(event.target.checked)} /><span><b>I approve this optional installation.</b><small>The desktop installer may open Command Prompt and run the shown command only after this box is selected.</small></span></label><label className="check-row tray-toggle"><input type="checkbox" checked={trayListening} onChange={(event) => setTrayListening(event.target.checked)} /><span><b>Keep listening when the main window is closed.</b><small>Closing Arthur hides it to the Windows system tray. Choosing “Exit Arthur,” pausing listening, signing out, or shutting down stops the listener.</small></span></label><div className="wakeword-note"><Activity size={20} /><p><b>Accuracy is calibrated, not guaranteed.</b> Arthur should provide a five-call microphone check, noise-level indicator, sensitivity control, and a visible listening state before background listening is enabled.</p></div><div className="modal-actions"><button className="text-button" onClick={close}>Not now</button><button className="primary-button" onClick={requestInstall}>Approve installation <ShieldCheck size={16} /></button></div></div></div>;
}

function ApiGuideModal({ close }: { close: () => void }) {
  const providers = [
    ["OpenAI", "Conversation, research, and voice", "Create a project key in the OpenAI API-key dashboard.", "https://platform.openai.com/api-keys"],
    ["Anthropic", "Optional reasoning checks", "Create a key in Claude Console Account Settings.", "https://platform.claude.com/settings/keys"],
    ["Supabase", "Browser accounts and profile sync", "Copy the Project URL and Publishable Key from the project Connect dialog.", "https://supabase.com/dashboard/project/_?showConnect=true"],
    ["Home Assistant", "Optional authorized smart-home control", "An authorized home owner creates a Long-Lived Access Token in User Profile → Security.", "https://my.home-assistant.io/redirect/profile_security"],
  ];
  return <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Arthur developer API acquisition guide"><div className="setup-modal api-guide-modal"><button className="icon-button close-modal" onClick={close} aria-label="Close API guide"><X size={18} /></button><div className="eyebrow">Developer API vault / acquisition guide</div><h2>Obtain keys from the provider, then keep them contained.</h2><p className="muted-copy">Use regenerated developer credentials only. Arthur’s production architecture keeps provider secrets on a protected backend; browser and desktop clients never receive server-only credentials.</p><div className="api-guide-list">{providers.map(([provider, purpose, instruction, href]) => <article className="api-guide-row" key={provider}><span className="provider-icon"><KeyRound size={16} /></span><div><b>{provider}</b><small>{purpose}</small><p>{instruction}</p></div><a className="outline-button" href={href} target="_blank" rel="noreferrer">Open provider <ArrowUpRight size={14} /></a></article>)}</div><div className="safety-note"><ShieldCheck size={20} /><p><b>Never enter:</b> a PostgreSQL connection string, database password, Supabase Secret/Service Role key, or any server credential in a distributed desktop app.</p></div><div className="modal-actions"><button className="primary-button" onClick={close}>Understood <ShieldCheck size={16} /></button></div></div></div>;
}

function PersonaPanel({ demeanor, learning, toggleDemeanor, toggleLearning, openPermissions }: { demeanor: { polite: boolean; wit: boolean; candor: boolean; calm: boolean }; learning: { routines: boolean; phrasing: boolean; schedule: boolean }; toggleDemeanor: (key: "polite" | "wit" | "candor" | "calm") => void; toggleLearning: (key: "routines" | "phrasing" | "schedule") => void; openPermissions: () => void }) {
  const demeanorRows = [
    ["polite", "Formal regard", "Uses your selected title and a refined, respectful register."],
    ["wit", "Dry British wit", "Offers restrained, situational humour—never at the user’s expense."],
    ["candor", "Radical candour", "States risks, conflicts, and productivity bottlenecks plainly."],
    ["calm", "Calm under pressure", "Keeps a measured voice during alerts, heavy load, or urgent tasks."],
  ] as const;
  const learningRows = [
    ["routines", "Routine signals", "Learns opted-in focus hours and common workspaces."],
    ["phrasing", "Language & sayings", "Retains approved phrasing, pronunciation notes, and cultural preferences."],
    ["schedule", "Schedule anticipation", "May prepare reminders from authorised calendar data."],
  ] as const;
  return <section className="persona-layout"><header className="persona-hero"><div><span className="eyebrow">Arthur conduct protocol</span><h2>Level voice. Clear judgement. Your terms.</h2><p>Arthur can be formal, composed, candid, and dryly funny without becoming hostile, manipulative, or presumptuous.</p></div><div className="persona-seal"><span className="orbit-seal"><Bot size={23} /></span><span>GUARDED<br/>LOYALTY</span></div></header><div className="persona-grid"><section className="persona-panel"><div className="section-heading"><div><span className="eyebrow">Demeanor matrix</span><h3>How Arthur speaks</h3></div><Settings2 size={18} /></div>{demeanorRows.map(([id, label, detail]) => <article className="protocol-row" key={id}><span className="protocol-icon"><Bot size={17} /></span><div><b>{label}</b><small>{detail}</small></div><button aria-pressed={demeanor[id]} className={`switch ${demeanor[id] ? "on" : ""}`} onClick={() => toggleDemeanor(id)}><span /></button></article>)}</section><section className="persona-panel learning-panel"><div className="section-heading"><div><span className="eyebrow">Learning ledger</span><h3>Adaptive by permission</h3></div><Fingerprint size={18} /></div>{learningRows.map(([id, label, detail]) => <article className="protocol-row" key={id}><span className="protocol-icon"><FolderCog size={17} /></span><div><b>{label}</b><small>{detail}</small></div><button aria-pressed={learning[id]} className={`switch ${learning[id] ? "on" : ""}`} onClick={() => toggleLearning(id)}><span /></button></article>)}<div className="ledger-rule"><ShieldCheck size={18} /><span>Every learned item remains reviewable, editable, exportable, and erasable by its owner.</span></div></section></div><section className="holo-workspace"><div className="holo-copy"><span className="eyebrow">Holographic data workspace</span><h2>Organise evidence, not mysteries.</h2><p>Arthur may cross-reference documents, approved research, calendar context, and local telemetry to prepare a spoken brief. It does not silently upload private files or access systems you have not authorized.</p><div className="holo-actions"><button className="primary-button" onClick={() => toast("Arthur would ask you to select approved sources before creating a research workspace.")}>Prepare research lens <Search size={16} /></button><button className="outline-button" onClick={openPermissions}>Inspect consent scope <ShieldCheck size={16} /></button></div></div><div className="holo-stage" aria-label="Illustrative holographic data workspace"><div className="holo-plane plane-one" /><div className="holo-plane plane-two" /><div className="holo-core"><Crosshair aria-hidden="true" size={28} /><b>AUTHORISE</b><small>scope / sources / output</small></div><div className="holo-readout readout-one">FILES / SELECTED</div><div className="holo-readout readout-two">SOURCES / VERIFIED</div><div className="holo-readout readout-three">OUTPUT / SPOKEN</div></div></section><section className="protective-grid"><article><StatusPill tone="amber">Attention</StatusPill><b>Calendar collision</b><p>Arthur can identify a conflict and propose options. It never moves meetings without approval.</p></article><article><StatusPill tone="green">Healthy</StatusPill><b>Workstation guard</b><p>Arthur can watch authorised system signals, explain bottlenecks, and ask before changing performance settings.</p></article><article><StatusPill tone="blue">Private by default</StatusPill><b>Research boundary</b><p>Arthur can summarize approved information sources but refuses unauthorized access and security bypass requests.</p></article></section></section>;
}

export default function Home() {
  const [section, setSection] = useState<Section>("command");
  const [setupOpen, setSetupOpen] = useState(false);
  const [listening, setListening] = useState(false);
  const [name, setName] = useState("Aline");
  const [title, setTitle] = useState("Madam");
  const [language, setLanguage] = useState("Kinyarwanda");
  const [command, setCommand] = useState("");
  const [visualPrompt, setVisualPrompt] = useState(true);
  const [permissions, setPermissions] = useState({ automation: true, health: true, research: true, smartHome: false });
  const [customIntegrations, setCustomIntegrations] = useState<ProviderCard[]>([]);
  const [integrationOpen, setIntegrationOpen] = useState(false);
  const [wakeWordOpen, setWakeWordOpen] = useState(false);
  const [apiGuideOpen, setApiGuideOpen] = useState(false);
  const [demeanor, setDemeanor] = useState({ polite: true, wit: true, candor: true, calm: true });
  const [learning, setLearning] = useState({ routines: true, phrasing: true, schedule: false });
  const [commandPlan, setCommandPlan] = useState<CommandPlanPreview | null>(null);
  const [automationPaused, setAutomationPaused] = useState(false);
  const greeting = useMemo(() => `At your signal, ${title}.`, [title]);

  const runCommand = () => {
    if (!command.trim()) return toast.error("Give Arthur something to prepare first.");
    const plan = planCommandPreview(command);
    setCommandPlan(plan);
    if (plan.allowed) toast.success("Arthur prepared a reviewed local command plan.", { description: "This browser preview never executes a command or contacts a provider." });
    else toast.error("Arthur declined that command request.", { description: plan.reason });
  };
  const saveProfile = (nextName: string, nextTitle: string, nextLanguage: string) => {
    setName(nextName); setTitle(nextTitle); setLanguage(nextLanguage); setSetupOpen(false);
    toast.success(`Profile prepared for ${nextName}.`, { description: "Preferences are preview-only in this browser." });
  };

  return (
    <main className="arthur-app">
      <aside className="instrument-rail">
        <div className="brand-lockup"><img src={markImage} alt="Arthur orbital mark" /><div><strong>ARTHUR</strong><span>desktop intelligence</span></div></div>
        <nav aria-label="Arthur sections">
          {nav.map(([id, Icon, label]) => <button key={id} className={`nav-item ${section === id ? "active" : ""}`} onClick={() => setSection(id)}><Icon size={19} /><span>{label}</span></button>)}
        </nav>
        <div className="rail-bottom"><div className="rail-profile"><span className="profile-avatar">{name.slice(0, 1).toUpperCase()}</span><div><b>{name}</b><small>{language}</small></div><ChevronRight size={16} /></div><button className="nav-item ghost" onClick={() => toast("Preview system notes", { description: "The production desktop app keeps diagnostics local unless you explicitly choose to share them." })}><CircleHelp size={18} /><span>System notes</span></button></div>
      </aside>

      <section className={`command-canvas ${section === "persona" ? "persona-active" : ""}`}>
        {section === "persona" && <PersonaPanel demeanor={demeanor} learning={learning} toggleDemeanor={(key) => setDemeanor((current) => ({ ...current, [key]: !current[key] }))} toggleLearning={(key) => setLearning((current) => ({ ...current, [key]: !current[key] }))} openPermissions={() => setSection("permissions")} />}
        {section === "api" && <button className="api-guide-fab" onClick={() => setApiGuideOpen(true)}><KeyRound size={15} /> Where do I get keys?</button>}
        <header className="topbar"><div><div className="eyebrow">Local workstation / windows 11</div><h1>{section === "command" ? "Command desk" : section === "voice" ? "Voice studio" : section === "persona" ? "Conduct & memory" : section === "api" ? "Developer API vault" : section === "permissions" ? "Permission register" : "Update control"}</h1></div><div className="top-actions"><StatusPill tone="green">Verified / stable</StatusPill><button className="outline-button" onClick={() => setSetupOpen(true)}><UserRound size={16} /> Personal protocol</button></div></header>

        {section === "command" && <>
          <section className="hero-command" style={{ backgroundImage: `linear-gradient(90deg, rgba(5, 11, 24, .95) 18%, rgba(5,11,24,.42) 72%, rgba(5,11,24,.86)), url(${heroImage})` }}>
            <div className="hero-copy"><div className="eyebrow light">Arthur is standing by</div><h2>{greeting}</h2><p>Voice-first assistance, carefully governed. Ask in {language}, English, French, or Kiswahili.</p><div className="hero-meta"><StatusPill>Wake word ready</StatusPill><span><LockKeyhole size={14} /> Spoken replies by default</span></div></div>
            <div className={`listening-orb ${listening ? "listening" : ""}`}><span className="orbit orbit-a" /><span className="orbit orbit-b" /><span className="orb-core"><Mic size={27} /></span><span className="orb-label">{listening ? "LISTENING" : "ARTHUR"}</span></div>
          </section>
          <section className="command-entry"><div className="command-prefix"><TerminalSquare size={18} /> <span>Speak or type a request</span></div><input value={command} onChange={(e) => setCommand(e.target.value)} onKeyDown={(e) => e.key === "Enter" && runCommand()} placeholder="For example: check my disk space, or show Kali WSL memory…" /><button className="voice-button" onClick={() => setListening(!listening)} aria-label="Toggle listening"><Mic size={18} /></button><button className="primary-button compact" onClick={runCommand}>Prepare <ArrowUpRight size={16} /></button></section>
          {commandPlan && <section className={`command-plan ${commandPlan.risk}`} aria-live="polite"><div className="plan-emblem"><TerminalSquare size={20} /></div><div className="plan-copy"><span className="eyebrow">Reviewed command plan / {commandPlan.risk}</span><h3>{commandPlan.summary}</h3><code>{commandPlan.command}</code>{commandPlan.reason && <p>{commandPlan.reason}</p>}</div><div className="plan-actions">{commandPlan.confirmation ? <StatusPill tone="amber">Approval required</StatusPill> : commandPlan.allowed ? <StatusPill tone="green">Read-only diagnostic</StatusPill> : <StatusPill tone="amber">Not available</StatusPill>}<button className="outline-button" onClick={() => toast(commandPlan.allowed ? "The production app would show this exact command and follow its permission policy." : "Arthur will retain no raw command text in its audit record.")}>{commandPlan.allowed ? "Inspect policy" : "Why blocked?"}</button></div></section>}
          <section className="command-governance"><div><span className="eyebrow">Automation governor</span><p>Arthur translates words into a small command allowlist. It never passes generated text directly to a shell.</p></div><button className={`outline-button ${automationPaused ? "pause-active" : ""}`} onClick={() => { setAutomationPaused((current) => !current); toast(automationPaused ? "Automation governor re-armed." : "Automation governor paused; new command plans remain visible but cannot proceed."); }}><Power size={16} /> {automationPaused ? "Resume approved tools" : "Pause all automation"}</button></section>
          <section className="quick-grid"><button onClick={() => setCommand("Summarize my calendar and alert me to conflicts")}> <BellRing size={17} /> Prepare day brief</button><button onClick={() => setCommand("Check workstation health and explain any bottleneck")}> <CircleGauge size={17} /> Prepare health readout</button><button onClick={() => setCommand("Research the latest information and give me a spoken summary")}> <Search size={17} /> Prepare private research</button><button onClick={() => setSection("permissions")}> <ShieldCheck size={17} /> Inspect permissions</button></section>
          <section className="command-lower"><div className="conversation-card"><div className="section-heading"><div><span className="eyebrow">Recent exchange</span><h3>Short, honest, and audible.</h3></div><button className="text-button" onClick={() => toast("Transcript remains local in the desktop version.")}>Inspect local transcript</button></div><div className="exchange"><span className="exchange-mark">A</span><div><p className="exchange-time">NOW / Arthur</p><p>“Your system is running comfortably. I can prepare the research you asked for, then I’ll wait for your approval before I show anything on screen.”</p><div className="exchange-actions"><button onClick={() => toast("In the desktop app, Arthur would repeat this through your selected voice.")}> <Volume2 size={14} /> Speak again</button><button onClick={() => toast("Visual panels appear only after you confirm.")}> <MonitorCog size={14} /> Request visual panel</button></div></div></div></div>
            <div className="analytics-card" style={{ backgroundImage: `linear-gradient(145deg, rgba(8, 17, 37, .72), rgba(8,17,37,.96)), url(${analyticsImage})` }}><div className="section-heading"><div><span className="eyebrow">Live workstation</span><h3>Quiet telemetry</h3></div><Activity size={19} /></div><div className="mini-chart"><svg viewBox="0 0 280 84" aria-label="Illustrative system telemetry"><path d="M0 61 C18 57, 25 32, 44 44 S70 64, 89 33 S120 49, 141 36 S170 53, 189 24 S227 45, 280 20" fill="none" stroke="url(#chartGradient)" strokeWidth="3" /><path d="M0 61 C18 57, 25 32, 44 44 S70 64, 89 33 S120 49, 141 36 S170 53, 189 24 S227 45, 280 20 L280 84 L0 84Z" fill="url(#fillGradient)" opacity=".5" /><defs><linearGradient id="chartGradient" x1="0" x2="1"><stop stopColor="#55d9ff"/><stop offset="1" stopColor="#2f6bff"/></linearGradient><linearGradient id="fillGradient" x1="0" x2="0" y2="1"><stop stopColor="#2f6bff" stopOpacity=".45"/><stop offset="1" stopColor="#2f6bff" stopOpacity="0"/></linearGradient></defs></svg></div><div className="analytics-foot"><span><b>42%</b> balanced load</span><span>next scan 02:14</span></div></div></section>
          <section className="metrics-row"><Metric label="CPU load" value="42" unit="%" icon={Cpu} delta="steady" /><Metric label="Memory" value="61" unit="%" icon={Database} delta="+3.2" /><Metric label="Network" value="18" unit="Mbps" icon={Network} delta="clear" /></section>
        </>}

        {section === "voice" && <section className="voice-layout"><div className="voice-stage" style={{ backgroundImage: `linear-gradient(145deg, rgba(4,10,24,.84), rgba(4,10,24,.38)), url(${voiceImage})` }}><div className="voice-stage-copy"><span className="eyebrow light">Voice profile</span><h2>{language} is your native setting.</h2><p>Arthur listens for the language you use and replies in a natural voice. The production desktop app keeps the wake word local.</p><div className="voice-stage-actions"><button className="primary-button" onClick={() => setListening(!listening)}><Waves size={17} /> {listening ? "Pause listening" : "Preview wake word"}</button><button className="outline-button" onClick={() => setWakeWordOpen(true)}><TerminalSquare size={16} /> Review local setup</button></div></div><div className="voice-wave"><span /><span /><span /><span /><span /><span /><span /></div></div><div className="voice-options"><div className="section-heading"><div><span className="eyebrow">Language routing</span><h3>Natural switching</h3></div><Languages size={19} /></div>{["Kinyarwanda", "English", "French", "Kiswahili"].map((item) => <div className="language-row" key={item}><span className={`language-radio ${language === item ? "active" : ""}`} /><div><b>{item}</b><small>{language === item ? "Native profile language" : "Available when spoken"}</small></div>{language === item && <StatusPill>Default</StatusPill>}</div>)}<button className="outline-button full" onClick={() => toast("Arthur would save a new pronunciation note to the active profile.")}> <Plus size={16} /> Teach a pronunciation</button></div></section>}

        {section === "api" && <section className="api-layout"><div className="api-banner"><div><span className="eyebrow">Developer-controlled integrations</span><h2>Parallel provider boxes, one safe vault.</h2><p>Use this preview to inspect the setup flow. It does not transmit, save, or test any secret.</p></div><div className="api-banner-seal"><KeyRound size={25} /><span>Placeholder-only<br/>preview</span></div></div><div className="provider-grid">{[...providerCards, ...customIntegrations].map(([label, provider, detail, key]) => <article className="provider-card" key={label}><div className="provider-heading"><span className="provider-icon"><Sparkles size={16} /></span><div><h3>{label}</h3><p>{detail}</p></div><StatusPill tone="gray">Not connected</StatusPill></div><label>Provider<select defaultValue={provider}><option>{provider}</option><option>Custom provider</option><option>Disabled</option></select></label>{provider === "Supabase" ? <><label>Project URL<input type="url" name="supabase-url" placeholder="https://your-project.supabase.co" /></label><label>Publishable key<input type="password" name="supabase-publishable-key" placeholder="sb_publishable_..." /></label></> : provider === "openWakeWord" ? <div className="wakeword-card-note"><StatusPill tone="amber">Local install required</StatusPill><p>The desktop app requests approval before opening Command Prompt or enabling tray listening.</p><button className="outline-button" onClick={() => setWakeWordOpen(true)}><TerminalSquare size={15} /> Review setup</button></div> : <label>Developer key<input type="password" name={key} placeholder="Stored locally in the desktop app" /></label>}<div className="provider-actions"><button className="outline-button" onClick={() => toast("Connection test is intentionally disabled in this browser preview.")}>Test</button><button className="text-button" onClick={() => toast(`${label} is marked as a configured placeholder.`)}>Save placeholder</button></div></article>)}</div><button className="add-integration" onClick={() => setIntegrationOpen(true)}> <Plus size={18} /> Add an approved integration <ChevronRight size={17} /></button></section>}

        {section === "permissions" && <section className="permission-layout"><div className="permission-hero"><span className="eyebrow">Consent before capability</span><h2>Arthur can be capable without becoming intrusive.</h2><p>Permission switches describe the Windows desktop behavior. This preview only changes its display state.</p><StatusPill tone="amber">Approval required for consequential actions</StatusPill></div><div className="permission-list">{[["automation", MonitorCog, "PC automation", "Open, scroll, organize, and manage approved desktop tasks."], ["health", Activity, "Workstation health", "Read system load, disk state, and performance telemetry."], ["research", Globe2, "Quiet research", "Search and summarize information without opening a browser window."], ["smartHome", Power, "Smart home discovery", "Ask before connecting to a detected Home Assistant hub."]].map(([id, Icon, label, detail]) => <article className="permission-row" key={String(id)}><span className="permission-icon"><Icon size={20} /></span><div><h3>{label as string}</h3><p>{detail as string}</p></div><button aria-pressed={permissions[id as keyof typeof permissions]} className={`switch ${permissions[id as keyof typeof permissions] ? "on" : ""}`} onClick={() => { const permissionId = id as keyof typeof permissions; setPermissions((current) => ({ ...current, [permissionId]: !current[permissionId] })); }}><span /></button></article>)}</div><div className="safety-note"><Fingerprint size={21} /><p><b>Always confirmed:</b> deletion, sending messages, purchases, installations, private data actions, and administrator changes.</p></div></section>}

        {section === "updates" && <section className="update-layout"><div className="update-card"><div className="update-icon"><UploadCloud size={24} /></div><div><span className="eyebrow">Update channel</span><h2>Arthur 0.1.0 is current.</h2><p>When a signed update is available, Arthur asks before downloading or installing it. New permissions are never silently enabled.</p></div><StatusPill tone="green">Verified / current</StatusPill></div><div className="update-settings"><label className="check-row"><input type="checkbox" defaultChecked /> <span><b>Ask before downloading</b><small>Arthur presents the size, notes, and permission changes first.</small></span></label><label className="check-row"><input type="checkbox" defaultChecked /> <span><b>Keep settings through updates</b><small>Profiles, voice choices, and approved tools remain under your control.</small></span></label><label className="check-row"><input type="checkbox" checked={visualPrompt} onChange={(e) => setVisualPrompt(e.target.checked)} /> <span><b>Ask before showing visuals</b><small>Arthur remains spoken-first unless you allow a screen panel.</small></span></label></div><button className="outline-button" onClick={() => toast("No signed update is currently available in this preview.")}> <Radar size={16} /> Request signed update check</button></section>}
      </section>
      {setupOpen && <SetupModal close={() => setSetupOpen(false)} save={saveProfile} />}
      {integrationOpen && <IntegrationModal close={() => setIntegrationOpen(false)} save={(card) => setCustomIntegrations((current) => [...current, card])} />}
      {wakeWordOpen && <WakeWordModal close={() => setWakeWordOpen(false)} />}
      {apiGuideOpen && <ApiGuideModal close={() => setApiGuideOpen(false)} />}
    </main>
  );
}
