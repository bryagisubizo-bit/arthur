/**
 * A DOM-first contextual graph. It deliberately consumes only the local layout
 * contract, so future 3D or synchronized renderers can be introduced as adapters.
 */
import { Network, Radio, ShieldCheck } from "lucide-react";
import type { SpatialModule, SpatialWorkspaceEvent } from "@/lib/spatialWorkspace";

type SpatialContextGraphProps = {
  modules: SpatialModule[];
  focusedId: string;
  revision: number;
  lastEvent: SpatialWorkspaceEvent | null;
  unlocked: boolean;
};

export default function SpatialContextGraph({ modules, focusedId, revision, lastEvent, unlocked }: SpatialContextGraphProps) {
  const focused = modules.find((module) => module.id === focusedId);
  return (
    <section className="spatial-context-graph" aria-label="Arthur local spatial context graph">
      <header className="spatial-graph-heading">
        <div><span className="eyebrow">Context map / local state</span><h4>Module relationships remain reviewable.</h4></div>
        <span className="spatial-sync-status"><Radio size={14} /> No transport open</span>
      </header>
      <div className="spatial-graph-grid">
        <article className="spatial-focus-node">
          <Network size={18} />
          <span>Focused module</span>
          <b>{focused?.label ?? "No module selected"}</b>
          <small>{focused?.detail ?? "Restore or select a local workspace card."}</small>
        </article>
        <div className="spatial-node-list" role="list" aria-label="Visible workspace modules">
          {modules.map((module) => <div key={module.id} role="listitem" className={`spatial-node ${module.id === focusedId ? "active" : ""}`}><span>{module.category}</span><b>{module.label}</b></div>)}
        </div>
      </div>
      <footer className="spatial-event-foot"><ShieldCheck size={15} /><span>Revision {revision} · {lastEvent ? `${lastEvent.kind} by local user` : "No layout events yet"} · {unlocked ? "session access verified" : "room access required"}</span></footer>
    </section>
  );
}
