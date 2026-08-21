import { Camera, Mic, MonitorUp, Radio, ShieldCheck, Workflow } from "lucide-react";
import { toast } from "sonner";
import { multimodalAdapterContracts, type MultimodalAdapterId } from "@/lib/multimodalAdapters";

const adapterIcons: Record<MultimodalAdapterId, typeof Mic> = {
  speech_stream: Mic,
  vision_matrix: Camera,
  screen_share: MonitorUp,
  coordinate_stream: Radio,
  environment_hub: Workflow,
};

/** Visible contract panel; deliberately contains no browser capture or network APIs. */
export default function MultimodalReadinessPanel() {
  return <section className="tools-panel multimodal-readiness-panel" aria-label="Multimodal and environment adapter readiness">
    <div className="section-heading"><div><span className="eyebrow">Multimodal & environment / review only</span><h3>Every input and connection remains intentionally closed.</h3></div><ShieldCheck size={19} /></div>
    <p className="tools-intro">Arthur’s coordinate layer can prepare local JSON revisions, but no browser microphone, camera, screen capture, WebSocket, Home Assistant endpoint, MQTT broker, or provider connection is opened from this preview.</p>
    <div className="multimodal-contract-grid">{multimodalAdapterContracts.map((contract) => { const Icon = adapterIcons[contract.id]; return <article key={contract.id} className="multimodal-contract"><Icon size={17} /><div><span>{contract.defaultState} · transport {contract.transport}</span><b>{contract.label}</b><small>{contract.input}</small><p>{contract.activationRequirement}</p><em>{contract.credentials}</em></div><button className="text-button" onClick={() => toast(`${contract.label} activation is a separate review.`, { description: contract.activationRequirement })}>Review boundary</button></article>; })}</div>
  </section>;
}
