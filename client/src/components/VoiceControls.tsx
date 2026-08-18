/**
 * Orbital Command Atelier: voice configuration remains a visible consent contract rather than an ambient capture feature.
 */
import { FolderCog, Mic, MonitorCog, SlidersHorizontal, Volume2 } from "lucide-react";
import { toast } from "sonner";

type VoiceSettings = { microphone: boolean; speaker: boolean; screenAnalysis: boolean; fileAnalysis: boolean };

export default function VoiceControls({ settings, toggle }: { settings: VoiceSettings; toggle: (key: keyof VoiceSettings) => void }) {
  const controls: Array<[keyof VoiceSettings, typeof Mic, string, string]> = [
    ["microphone", Mic, "Microphone input", "Allows local wake-word and speech capture after device calibration."],
    ["speaker", Volume2, "Spoken replies", "Uses the selected voice device for responses; visual output still requires approval."],
    ["screenAnalysis", MonitorCog, "Screen analysis", "Arthur asks before inspecting a shared screen or any on-screen content."],
    ["fileAnalysis", FolderCog, "File analysis", "Arthur asks you to select files and explain the requested operation before analysis."],
  ];
  return <section className="voice-controls"><div className="voice-controls-heading"><div><span className="eyebrow">Devices & multimodal consent</span><h2>Listen locally. Inspect only when invited.</h2><p>These switches describe the installed Windows assistant. This browser preview does not open a microphone, speaker, screen, or file.</p></div><button className="outline-button" onClick={() => toast("The desktop app would run a five-call calibration and show a visible signal level.")}>Calibrate microphone <SlidersHorizontal size={15} /></button></div><div className="voice-control-grid">{controls.map(([id, Icon, label, detail]) => <article className="voice-control-card" key={id}><span className="voice-control-icon"><Icon size={18} /></span><div><b>{label}</b><small>{detail}</small></div><button className={`switch ${settings[id] ? "on" : ""}`} aria-pressed={settings[id]} onClick={() => toggle(id)}><span /></button></article>)}</div></section>;
}
