export type IntentKind = "device-control" | "research" | "notes" | "appearance" | "self-improvement" | "clarification";

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

  return intentPatterns.find(({ pattern }) => pattern.test(clean))?.assessment ?? {
    kind: "clarification",
    label: "Clarification required",
    summary: "Arthur understood that you want help, but it does not yet have a reviewed interpretation. It will ask a follow-up instead of inventing a command or provider route.",
    requiredRoom: "Needs a confirmed capability category",
    consequence: "review",
    alternatePhrasing: ["Tell Arthur the outcome you want", "Say which file, app, device, or information source is involved"],
  };
}
