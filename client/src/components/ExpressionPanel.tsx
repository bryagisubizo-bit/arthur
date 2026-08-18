/**
 * Orbital Command Atelier: expressive settings stay user-owned and visibly provider-dependent.
 */
import { Check, Palette, Volume2 } from "lucide-react";
import { toast } from "sonner";

type ColourMode = "cobalt" | "tide" | "amber";
type VoiceStyle = "diplomatic" | "warm" | "direct";

const colours: Array<{ id: ColourMode; name: string; detail: string; swatches: [string, string] }> = [
  { id: "cobalt", name: "Cobalt signal", detail: "Arthur’s original cool-blue instrument palette.", swatches: ["#2f6bff", "#55d9ff"] },
  { id: "tide", name: "Tidal teal", detail: "A calmer sea-glass workspace with high contrast.", swatches: ["#168c9d", "#79f0df"] },
  { id: "amber", name: "Amber archive", detail: "A warm, focused workspace for low-glare sessions.", swatches: ["#b46a19", "#ffcf7d"] },
];

const voices: Array<{ id: VoiceStyle; name: string; detail: string; sample: string }> = [
  { id: "diplomatic", name: "Diplomatic Arthur", detail: "Refined British calm with measured pacing.", sample: "At your signal. I have the details." },
  { id: "warm", name: "Warm studio", detail: "Softer delivery for long research and quiet focus.", sample: "Whenever you are ready, we can take this one step at a time." },
  { id: "direct", name: "Clear & direct", detail: "Short, confident responses for fast commands.", sample: "Understood. I will prepare the safe option." },
];

export type { ColourMode, VoiceStyle };

export default function ExpressionPanel({ colourMode, voiceStyle, setColourMode, setVoiceStyle }: { colourMode: ColourMode; voiceStyle: VoiceStyle; setColourMode: (value: ColourMode) => void; setVoiceStyle: (value: VoiceStyle) => void }) {
  return <section className="expression-panel"><div className="expression-heading"><div><span className="eyebrow">Personal expression / visual and voice profile</span><h2>Choose the colour of Arthur’s workspace and the character of its voice.</h2><p>Your choices alter this preview immediately. Voice playback remains provider-dependent and is never recorded from this panel.</p></div></div><div className="expression-grid"><section className="expression-group"><div className="expression-label"><Palette size={18} /><div><b>Workspace colour</b><small>Changes Arthur’s accent and signal colour.</small></div></div><div className="colour-options">{colours.map((item) => <button className={`colour-option ${colourMode === item.id ? "selected" : ""}`} key={item.id} onClick={() => { setColourMode(item.id); toast(`${item.name} is active.`); }} aria-pressed={colourMode === item.id}><span className="colour-pair"><i style={{ background: item.swatches[0] }} /><i style={{ background: item.swatches[1] }} /></span><span><b>{item.name}</b><small>{item.detail}</small></span>{colourMode === item.id && <Check size={16} />}</button>)}</div></section><section className="expression-group"><div className="expression-label"><Volume2 size={18} /><div><b>Voice character</b><small>Sets the desired delivery when a voice provider is configured.</small></div></div><div className="voice-style-options">{voices.map((item) => <button className={`voice-style-option ${voiceStyle === item.id ? "selected" : ""}`} key={item.id} onClick={() => { setVoiceStyle(item.id); toast(`${item.name} selected.`, { description: "A configured desktop voice provider would apply this style." }); }} aria-pressed={voiceStyle === item.id}><span><b>{item.name}</b><small>{item.detail}</small><em>“{item.sample}”</em></span>{voiceStyle === item.id && <Check size={16} />}</button>)}</div></section></div></section>;
}
