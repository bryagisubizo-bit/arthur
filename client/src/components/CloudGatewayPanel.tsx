import { useMemo, useState } from "react";
import { Cloud, Cpu, MonitorCog, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { cloudGatewayPresets, cloudGatewayState, lowResourcePolicy, validateCloudGatewayEndpoint } from "@/lib/cloudGateway";

export default function CloudGatewayPanel({ privacyLocked }: { privacyLocked: boolean }) {
  const [providerLabel, setProviderLabel] = useState<string>(cloudGatewayPresets[0]);
  const [endpoint, setEndpoint] = useState("");
  const [approvedData, setApprovedData] = useState("Approved text only; no microphone, camera, screen, or file content.");
  const [streamingRequested, setStreamingRequested] = useState(false);
  const [reviewed, setReviewed] = useState(false);
  const draft = useMemo(() => ({ providerLabel, endpoint, approvedData, streamingRequested }), [providerLabel, endpoint, approvedData, streamingRequested]);
  const state = cloudGatewayState(draft, privacyLocked);

  return (
    <section className="cloud-gateway-panel" aria-label="Cloud-assisted operating model">
      <div className="cloud-gateway-heading"><div><span className="eyebrow">Cloud-assisted / resource-aware</span><h3>Keep the desktop lean. Open the cloud route only by review.</h3></div><Cloud size={20} /></div>
      <p>Arthur uses the Windows device for consent, native layout, manual monitor review, and display state. An approved cloud gateway may later handle selected intelligence requests. This preview never saves a key, calls a URL, or opens a stream.</p>
      <div className="cloud-policy-grid">
        <div><Cpu size={16} /><b>Local budget</b><small>{lowResourcePolicy.deviceTarget}</small><span>{lowResourcePolicy.polling}</span></div>
        <div><MonitorCog size={16} /><b>Desktop monitor map</b><small>Windows prototype only</small><span>The browser cannot enumerate screens, PIDs, or move windows. The installed app asks before one reviewed placement.</span></div>
        <div><ShieldCheck size={16} /><b>Data boundary</b><small>{lowResourcePolicy.transportDefault} by default</small><span>{lowResourcePolicy.cloudWork}</span></div>
      </div>
      <div className="cloud-gateway-form">
        <label>Gateway class<select value={providerLabel} onChange={(event) => setProviderLabel(event.target.value)}>{cloudGatewayPresets.map((preset) => <option key={preset}>{preset}</option>)}</select></label>
        <label>HTTPS endpoint (not connected)<input value={endpoint} onChange={(event) => setEndpoint(event.target.value)} placeholder="https://gateway.example.com/v1" inputMode="url" /></label>
        <label>Approved data boundary<input value={approvedData} onChange={(event) => setApprovedData(event.target.value)} /></label>
      </div>
      <label className="review-choice"><input type="checkbox" checked={streamingRequested} onChange={(event) => setStreamingRequested(event.target.checked)} /> I want to review a later named streaming session. It remains off unless separately approved.</label>
      <div className="cloud-gateway-status"><SlidersHorizontal size={16} /><span>{state}</span><button className="outline-button" onClick={() => setReviewed(true)}>Review connection requirements</button></div>
      {reviewed && <div className="cloud-review-note" role="status">{endpoint.trim() ? validateCloudGatewayEndpoint(endpoint).detail : "Before any connection: set one HTTPS endpoint, store its developer-owned API key or OAuth token in Windows Credential Manager, declare the exact data boundary, and confirm the scope. Streaming requires a named client, duration, stop control, and its own approval."}</div>}
    </section>
  );
}
