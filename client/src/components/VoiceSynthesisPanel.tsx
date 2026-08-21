import { AudioLines, CheckCircle2, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { voiceSynthesisRouteById, voiceSynthesisRouteOptions, type VoiceSynthesisRouteId } from "@/lib/voiceSynthesisRoute";

type VoiceSynthesisPanelProps = {
  synthRoute: string;
  setSynthRoute: (routeId: VoiceSynthesisRouteId) => void;
};

export default function VoiceSynthesisPanel({ synthRoute, setSynthRoute }: VoiceSynthesisPanelProps) {
  const route = voiceSynthesisRouteById(synthRoute);

  return (
    <section className="consent-box" aria-labelledby="voice-synthesis-heading">
      <AudioLines size={24} />
      <div className="min-w-0">
        <strong id="voice-synthesis-heading">Voice synthesis / speech output</strong>
        <p>Approved reply text is prepared, processed by the chosen speech engine, then rendered as audio. This panel is a preference only—not an engine activation.</p>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {voiceSynthesisRouteOptions.map((option) => (
            <button
              key={option.id}
              type="button"
              onClick={() => setSynthRoute(option.id)}
              className={`rounded-xl border p-3 text-left transition ${synthRoute === option.id ? "border-cyan-300/70 bg-cyan-300/10" : "border-white/10 bg-white/[.03] hover:border-white/25"}`}
              aria-pressed={synthRoute === option.id}
            >
              <span className="flex items-center gap-2 text-sm font-semibold text-white">{synthRoute === option.id && <CheckCircle2 size={15} className="text-cyan-300" />}{option.label}</span>
              <span className="mt-1 block text-xs leading-5 text-slate-300">{option.detail}</span>
            </button>
          ))}
        </div>
        <p className="mt-3 text-sm text-slate-200"><ShieldCheck size={14} className="mr-1 inline text-cyan-300" />{route?.boundary ?? "Choose a local or provider route. No engine, model, microphone, provider, or audio pathway starts from this selection."}</p>
        <button className="text-button mt-2" type="button" onClick={() => toast(route ? `${route.label} remains a local preference only.` : "Choose a speech-output route first.", { description: "No engine, model, microphone, provider, text transmission, or voice cloning was started." })}>Review local preference</button>
      </div>
    </section>
  );
}
