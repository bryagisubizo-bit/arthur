import { languageFromPreferenceRequest } from "./languageLibrary";

export type IntentKind =
  | "device-control"
  | "research"
  | "notes"
  | "appearance"
  | "self-improvement"
  | "language-preference"
  | "app-launch"
  | "message-draft"
  | "voice-visualizer"
  | "voice-cloning"
  | "clarification";

export type IntentAssessment = {
  kind: IntentKind;
  label: string;
  summary: string;
  requiredRoom: string;
  vaultCategory?: string;
  consequence: "read-only" | "review" | "proposal";
  alternatePhrasing: string[];
};

const intentPatterns: Array<{ pattern: RegExp; assessment: IntentAssessment }> = [
  {
    pattern: /\b(speak|talk|reply|parle|vuga|ongea|sema)\s+(in\s+|mu\s+|en\s+)?(kinyarwanda|ikinyarwanda|english|anglais|french|fran[çc]ais|kiswahili|swahili)\b/i,
    assessment: {
      kind: "language-preference",
      label: "Reply-language preference",
      summary: "Arthur recognised a request to change its reply language. The desktop prototype repeats and saves the selected local preference; spoken transcription in that language still needs an approved speech-to-text room.",
      requiredRoom: "Local profile preference — no provider call",
      consequence: "review",
      alternatePhrasing: ["Speak in Kinyarwanda", "Parle en français", "Ongea Kiswahili"],
    },
  },
  {
    pattern: /\b(text|message|send (?:a )?(?:whatsapp )?message|whatsapp someone)\b/i,
    assessment: {
      kind: "message-draft",
      label: "Message draft only",
      summary: "Arthur recognised a messaging request. It may collect a recipient and exact draft for your review, but it never selects a contact, opens a conversation, or sends a message automatically.",
      requiredRoom: "Windows & local desktop",
      vaultCategory: "Windows & local desktop",
      consequence: "review",
      alternatePhrasing: ["Text someone on WhatsApp", "Prepare a message", "Draft a WhatsApp note"],
    },
  },
  {
    pattern: /\b(open|launch|start)\s+(?:the )?(camera|whatsapp)\b/i,
    assessment: {
      kind: "app-launch",
      label: "Reviewed application launch",
      summary: "Arthur recognised a fixed Windows app route. The desktop prototype shows the exact URI and asks before it launches the installed Camera or WhatsApp application; it never runs generated shell text.",
      requiredRoom: "Windows & local desktop",
      vaultCategory: "Windows & local desktop",
      consequence: "review",
      alternatePhrasing: ["Open camera", "Launch WhatsApp", "Start the Camera app"],
    },
  },
  {
    pattern: /\b(open|show|start)\s+(?:the )?(voice|audio|sound)\s+(?:signal|visuali[sz]er|orb)\b/i,
    assessment: {
      kind: "voice-visualizer",
      label: "Local voice signal",
      summary: "Arthur can open its local voice-signal workspace. It uses a transient amplitude indicator only while listening or a command session is active; it does not save a recording.",
      requiredRoom: "Local visual feedback — no API resource required",
      consequence: "read-only",
      alternatePhrasing: ["Show the voice orb", "Open the sound visualizer", "Start the audio signal"],
    },
  },
  {
    pattern: /\b(clone|copy|replicate)\s+(?:my )?voice\b/i,
    assessment: {
      kind: "voice-cloning",
      label: "Voice-cloning request",
      summary: "Arthur recognised a request to clone your own voice. It requires a selected provider, a separate informed-consent review, an explicit sample and retention policy, and a final provider-action confirmation. This preview neither records nor uploads audio.",
      requiredRoom: "Voice synthesis & cloning — provider and consent required",
      vaultCategory: "Voice & speech",
      consequence: "proposal",
      alternatePhrasing: ["Clone my voice", "Make a copy of my voice", "Use my voice for Arthur"],
    },
  },
  {
    pattern: /\b(quieter|lower (the )?volume|turn (the )?(sound|volume) down|reduce (the )?sound|make it less loud)\b/i,
    assessment: {
      kind: "device-control",
      label: "Audio adjustment",
      summary: "Arthur recognised alternate wording for a Windows audio change. The desktop audio adapter would preview the target level and ask before changing it.",
      requiredRoom: "Windows & local desktop",
      vaultCategory: "Windows & local desktop",
      consequence: "review",
      alternatePhrasing: ["Make it quieter", "Lower the sound", "Reduce the volume"],
    },
  },
  {
    pattern: /\b(research|look up|find information|search for|tell me about)\b/i,
    assessment: {
      kind: "research",
      label: "Research brief",
      summary: "Arthur recognised a research request and will use only the approved research room after checking its connection and source policy.",
      requiredRoom: "Search, news & research",
      vaultCategory: "Search, news & research",
      consequence: "read-only",
      alternatePhrasing: ["Look this up", "Find information about this", "Research this for me"],
    },
  },
  {
    pattern: /\b(remember|write this down|make a note|note that|keep this)\b/i,
    assessment: {
      kind: "notes",
      label: "Private note",
      summary: "Arthur recognised a note request. It would show the exact proposed note and ask whether it may be saved and studied.",
      requiredRoom: "Databases, storage & AI memory",
      vaultCategory: "Databases, storage & AI memory",
      consequence: "review",
      alternatePhrasing: ["Write this down", "Keep this for me", "Remember this"],
    },
  },
  {
    pattern: /\b(change (the )?(colour|color|theme|font|typing|layout)|make (the )?(text|type) (larger|smaller)|use (a )?(dark|blue|dense|calm) (theme|layout))\b/i,
    assessment: {
      kind: "appearance",
      label: "Personal appearance",
      summary: "Arthur recognised a preference change. It can apply an in-app appearance setting after showing the affected controls; no provider is needed.",
      requiredRoom: "Local presentation setting — no API resource required",
      consequence: "review",
      alternatePhrasing: ["Use larger writing", "Change the theme", "Make the interface calmer"],
    },
  },
  {
    pattern: /\b(change yourself|improve yourself|redesign yourself|add a feature|make yourself)\b/i,
    assessment: {
      kind: "self-improvement",
      label: "Reviewable evolution request",
      summary: "Arthur recognised a request to change its software. It can prepare a provider-assisted plan, code-diff scope, test list, and rollback point, but never changes itself automatically.",
      requiredRoom: "App building, code & deployment",
      vaultCategory: "App building, code & deployment",
      consequence: "proposal",
      alternatePhrasing: ["Improve yourself", "Add a feature", "Redesign this screen"],
    },
  },
];

export function assessNaturalLanguage(request: string): IntentAssessment {
  const clean = request.trim();
  if (!clean) {
    return {
      kind: "clarification",
      label: "Awaiting your request",
      summary: "Speak or type a goal in your own words. Arthur will classify the intent, name the required room, and ask when the request is ambiguous or consequential.",
      requiredRoom: "No room selected",
      consequence: "review",
      alternatePhrasing: [],
    };
  }

  const selectedLanguage = languageFromPreferenceRequest(clean);
  if (selectedLanguage) {
    return {
      kind: "language-preference",
      label: "Reply-language preference",
      summary: `Arthur recognised ${selectedLanguage.name} as a local conversation preference. It will not download a pack, turn on listening, translate text, or call a provider from this request.`,
      requiredRoom: "Local profile preference — no provider call",
      consequence: "review",
      alternatePhrasing: ["Speak in Kinyarwanda", "Parle en français", "Speak in Arabic"],
    };
  }

  return intentPatterns.find(({ pattern }) => pattern.test(clean))?.assessment ?? {
    kind: "clarification",
    label: "Clarification required",
    summary: "Arthur understood that you want help, but it does not yet have a reviewed interpretation. It will ask a follow-up instead of inventing a command or provider route.",
    requiredRoom: "Needs a confirmed capability category",
    consequence: "review",
    alternatePhrasing: ["Tell Arthur the outcome you want", "Say which file, app, device, or information source is involved"],
  };
}
