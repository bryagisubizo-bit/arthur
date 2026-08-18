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

type Section = "command" | "voice" | "api" | "permissions" | "updates";

const heroImage = "/manus-storage/arthur-hero-atmosphere_eca500cb.png";
const analyticsImage = "/manus-storage/arthur-analytics-orbit_3b540420.png";
const voiceImage = "/manus-storage/arthur-voice-signal_cd52a5c8.png";
const markImage = "/manus-storage/arthur-mark_c216fbf0.png";

const providerCards = [
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
  ["api", KeyRound, "API vault"],
  ["permissions", ShieldCheck, "Permissions"],
  ["updates", UploadCloud, "Updates"],
] as const;

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
  const greeting = useMemo(() => `At your signal, ${title}.`, [title]);

  const runCommand = () => {
    if (!command.trim()) return toast.error("Give Arthur something to prepare first.");
    toast.success("Arthur would answer by voice in the desktop app.", { description: "This browser preview never contacts a provider or controls your computer." });
    setCommand("");
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

      <section className="command-canvas">
        <header className="topbar"><div><div className="eyebrow">Local workstation / windows 11</div><h1>{section === "command" ? "Command desk" : section === "voice" ? "Voice studio" : section === "api" ? "Developer API vault" : section === "permissions" ? "Permission register" : "Update control"}</h1></div><div className="top-actions"><StatusPill tone="green">Verified / stable</StatusPill><button className="outline-button" onClick={() => setSetupOpen(true)}><UserRound size={16} /> Personal protocol</button></div></header>

        {section === "command" && <>
          <section className="hero-command" style={{ backgroundImage: `linear-gradient(90deg, rgba(5, 11, 24, .95) 18%, rgba(5,11,24,.42) 72%, rgba(5,11,24,.86)), url(${heroImage})` }}>
            <div className="hero-copy"><div className="eyebrow light">Arthur is standing by</div><h2>{greeting}</h2><p>Voice-first assistance, carefully governed. Ask in {language}, English, French, or Kiswahili.</p><div className="hero-meta"><StatusPill>Wake word ready</StatusPill><span><LockKeyhole size={14} /> Spoken replies by default</span></div></div>
            <div className={`listening-orb ${listening ? "listening" : ""}`}><span className="orbit orbit-a" /><span className="orbit orbit-b" /><span className="orb-core"><Mic size={27} /></span><span className="orb-label">{listening ? "LISTENING" : "ARTHUR"}</span></div>
          </section>
          <section className="command-entry"><div className="command-prefix"><TerminalSquare size={18} /> <span>Speak or type a request</span></div><input value={command} onChange={(e) => setCommand(e.target.value)} onKeyDown={(e) => e.key === "Enter" && runCommand()} placeholder="For example: prepare a concise research brief on…" /><button className="voice-button" onClick={() => setListening(!listening)} aria-label="Toggle listening"><Mic size={18} /></button><button className="primary-button compact" onClick={runCommand}>Prepare <ArrowUpRight size={16} /></button></section>
          <section className="quick-grid"><button onClick={() => setCommand("Summarize my calendar and alert me to conflicts")}> <BellRing size={17} /> Prepare day brief</button><button onClick={() => setCommand("Check workstation health and explain any bottleneck")}> <CircleGauge size={17} /> Prepare health readout</button><button onClick={() => setCommand("Research the latest information and give me a spoken summary")}> <Search size={17} /> Prepare private research</button><button onClick={() => setSection("permissions")}> <ShieldCheck size={17} /> Inspect permissions</button></section>
          <section className="command-lower"><div className="conversation-card"><div className="section-heading"><div><span className="eyebrow">Recent exchange</span><h3>Short, honest, and audible.</h3></div><button className="text-button" onClick={() => toast("Transcript remains local in the desktop version.")}>Inspect local transcript</button></div><div className="exchange"><span className="exchange-mark">A</span><div><p className="exchange-time">NOW / Arthur</p><p>“Your system is running comfortably. I can prepare the research you asked for, then I’ll wait for your approval before I show anything on screen.”</p><div className="exchange-actions"><button onClick={() => toast("In the desktop app, Arthur would repeat this through your selected voice.")}> <Volume2 size={14} /> Speak again</button><button onClick={() => toast("Visual panels appear only after you confirm.")}> <MonitorCog size={14} /> Request visual panel</button></div></div></div></div>
            <div className="analytics-card" style={{ backgroundImage: `linear-gradient(145deg, rgba(8, 17, 37, .72), rgba(8,17,37,.96)), url(${analyticsImage})` }}><div className="section-heading"><div><span className="eyebrow">Live workstation</span><h3>Quiet telemetry</h3></div><Activity size={19} /></div><div className="mini-chart"><svg viewBox="0 0 280 84" aria-label="Illustrative system telemetry"><path d="M0 61 C18 57, 25 32, 44 44 S70 64, 89 33 S120 49, 141 36 S170 53, 189 24 S227 45, 280 20" fill="none" stroke="url(#chartGradient)" strokeWidth="3" /><path d="M0 61 C18 57, 25 32, 44 44 S70 64, 89 33 S120 49, 141 36 S170 53, 189 24 S227 45, 280 20 L280 84 L0 84Z" fill="url(#fillGradient)" opacity=".5" /><defs><linearGradient id="chartGradient" x1="0" x2="1"><stop stopColor="#55d9ff"/><stop offset="1" stopColor="#2f6bff"/></linearGradient><linearGradient id="fillGradient" x1="0" x2="0" y2="1"><stop stopColor="#2f6bff" stopOpacity=".45"/><stop offset="1" stopColor="#2f6bff" stopOpacity="0"/></linearGradient></defs></svg></div><div className="analytics-foot"><span><b>42%</b> balanced load</span><span>next scan 02:14</span></div></div></section>
          <section className="metrics-row"><Metric label="CPU load" value="42" unit="%" icon={Cpu} delta="steady" /><Metric label="Memory" value="61" unit="%" icon={Database} delta="+3.2" /><Metric label="Network" value="18" unit="Mbps" icon={Network} delta="clear" /></section>
        </>}

        {section === "voice" && <section className="voice-layout"><div className="voice-stage" style={{ backgroundImage: `linear-gradient(145deg, rgba(4,10,24,.84), rgba(4,10,24,.38)), url(${voiceImage})` }}><div className="voice-stage-copy"><span className="eyebrow light">Voice profile</span><h2>{language} is your native setting.</h2><p>Arthur listens for the language you use and replies in a natural voice. The production desktop app keeps the wake word local.</p><button className="primary-button" onClick={() => setListening(!listening)}><Waves size={17} /> {listening ? "Pause listening" : "Preview wake word"}</button></div><div className="voice-wave"><span /><span /><span /><span /><span /><span /><span /></div></div><div className="voice-options"><div className="section-heading"><div><span className="eyebrow">Language routing</span><h3>Natural switching</h3></div><Languages size={19} /></div>{["Kinyarwanda", "English", "French", "Kiswahili"].map((item) => <div className="language-row" key={item}><span className={`language-radio ${language === item ? "active" : ""}`} /><div><b>{item}</b><small>{language === item ? "Native profile language" : "Available when spoken"}</small></div>{language === item && <StatusPill>Default</StatusPill>}</div>)}<button className="outline-button full" onClick={() => toast("Arthur would save a new pronunciation note to the active profile.")}> <Plus size={16} /> Teach a pronunciation</button></div></section>}

        {section === "api" && <section className="api-layout"><div className="api-banner"><div><span className="eyebrow">Developer-controlled integrations</span><h2>Parallel provider boxes, one safe vault.</h2><p>Use this preview to inspect the setup flow. It does not transmit, save, or test any secret.</p></div><div className="api-banner-seal"><KeyRound size={25} /><span>Placeholder-only<br/>preview</span></div></div><div className="provider-grid">{providerCards.map(([label, provider, detail, key]) => <article className="provider-card" key={label}><div className="provider-heading"><span className="provider-icon"><Sparkles size={16} /></span><div><h3>{label}</h3><p>{detail}</p></div><StatusPill tone="gray">Not connected</StatusPill></div><label>Provider<select defaultValue={provider}><option>{provider}</option><option>Custom provider</option><option>Disabled</option></select></label><label>Developer key<input type="password" name={key} placeholder="Stored locally in the desktop app" /></label><div className="provider-actions"><button className="outline-button" onClick={() => toast("Connection test is intentionally disabled in this browser preview.")}>Test</button><button className="text-button" onClick={() => toast(`${label} is marked as a configured placeholder.`)}>Save placeholder</button></div></article>)}</div><button className="add-integration" onClick={() => toast("The production plugin registry will add a reviewed API or MCP integration here.")}> <Plus size={18} /> Add an approved integration <ChevronRight size={17} /></button></section>}

        {section === "permissions" && <section className="permission-layout"><div className="permission-hero"><span className="eyebrow">Consent before capability</span><h2>Arthur can be capable without becoming intrusive.</h2><p>Permission switches describe the Windows desktop behavior. This preview only changes its display state.</p><StatusPill tone="amber">Approval required for consequential actions</StatusPill></div><div className="permission-list">{[["automation", MonitorCog, "PC automation", "Open, scroll, organize, and manage approved desktop tasks."], ["health", Activity, "Workstation health", "Read system load, disk state, and performance telemetry."], ["research", Globe2, "Quiet research", "Search and summarize information without opening a browser window."], ["smartHome", Power, "Smart home discovery", "Ask before connecting to a detected Home Assistant hub."]].map(([id, Icon, label, detail]) => <article className="permission-row" key={String(id)}><span className="permission-icon"><Icon size={20} /></span><div><h3>{label as string}</h3><p>{detail as string}</p></div><button aria-pressed={permissions[id as keyof typeof permissions]} className={`switch ${permissions[id as keyof typeof permissions] ? "on" : ""}`} onClick={() => { const permissionId = id as keyof typeof permissions; setPermissions((current) => ({ ...current, [permissionId]: !current[permissionId] })); }}><span /></button></article>)}</div><div className="safety-note"><Fingerprint size={21} /><p><b>Always confirmed:</b> deletion, sending messages, purchases, installations, private data actions, and administrator changes.</p></div></section>}

        {section === "updates" && <section className="update-layout"><div className="update-card"><div className="update-icon"><UploadCloud size={24} /></div><div><span className="eyebrow">Update channel</span><h2>Arthur 0.1.0 is current.</h2><p>When a signed update is available, Arthur asks before downloading or installing it. New permissions are never silently enabled.</p></div><StatusPill tone="green">Verified / current</StatusPill></div><div className="update-settings"><label className="check-row"><input type="checkbox" defaultChecked /> <span><b>Ask before downloading</b><small>Arthur presents the size, notes, and permission changes first.</small></span></label><label className="check-row"><input type="checkbox" defaultChecked /> <span><b>Keep settings through updates</b><small>Profiles, voice choices, and approved tools remain under your control.</small></span></label><label className="check-row"><input type="checkbox" checked={visualPrompt} onChange={(e) => setVisualPrompt(e.target.checked)} /> <span><b>Ask before showing visuals</b><small>Arthur remains spoken-first unless you allow a screen panel.</small></span></label></div><button className="outline-button" onClick={() => toast("No signed update is currently available in this preview.")}> <Radar size={16} /> Request signed update check</button></section>}
      </section>
      {setupOpen && <SetupModal close={() => setSetupOpen(false)} save={saveProfile} />}
    </main>
  );
}
