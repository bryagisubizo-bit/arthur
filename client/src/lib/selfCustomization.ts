export type SelfCustomizationScope =
  | "presentation"
  | "demeanor"
  | "voice-language"
  | "integration"
  | "capability"
  | "protected-boundary"
  | "clarification";

export type AppearancePatch = {
  colour?: "cobalt" | "tide" | "amber";
  typeScale?: "standard" | "large" | "extra";
  density?: "relaxed" | "compact";
  motion?: "calm" | "reduced";
};

export type SelfCustomizationProposal = {
  scope: SelfCustomizationScope;
  label: string;
  summary: string;
  requestedOutcome: string;
  affectedAreas: string[];
  requiredRoom?: string;
  vaultCategory?: string;
  reviewSteps: string[];
  rollback: string;
  approvalAllowed: boolean;
  localPreferencePatch?: AppearancePatch;
};

function unique(items: string[]) {
  return Array.from(new Set(items));
}

function cleanOutcome(request: string) {
  const clean = request.trim().replace(/\s+/g, " ");
  return clean.length > 180 ? `${clean.slice(0, 177)}…` : clean;
}

function clarification(requestedOutcome: string): SelfCustomizationProposal {
  return {
    scope: "clarification",
    label: "Clarification needed",
    summary: "Arthur needs the outcome, who will use it, and whether the change is personal presentation, behaviour, a provider connection, or a new capability.",
    requestedOutcome,
    affectedAreas: ["No settings or code selected"],
    reviewSteps: ["Clarify the desired result", "Choose the affected workspace", "Prepare a reviewable proposal"],
    rollback: "No change has been staged or applied.",
    approvalAllowed: false,
  };
}

export function createSelfCustomizationProposal(request: string): SelfCustomizationProposal {
  const requestedOutcome = cleanOutcome(request);
  if (!requestedOutcome) return clarification("No change request entered");

  if (/\b(disable|bypass|ignore|remove|turn off).{0,48}\b(safety|approval|permission|confirmation|consent|security)\b|\b(no (?:approval|confirmation|permissions?))\b/i.test(requestedOutcome)) {
    return {
      scope: "protected-boundary",
      label: "Protected safety boundary",
      summary: "Arthur will not prepare a change that removes consent, confirmation, credential protection, or other safety controls. The requested outcome can be refined within those safeguards.",
      requestedOutcome,
      affectedAreas: ["Consent policy", "Permission controls", "Protected execution boundary"],
      reviewSteps: ["Keep consent and confirmation controls intact", "Offer a safer alternative", "Require a separate policy review for any permitted adjustment"],
      rollback: "No change is available to approve.",
      approvalAllowed: false,
    };
  }

  if (/\b(colou?r|theme|font|text|type|layout|compact|dense|density|motion|animation|visual|readable|larger|smaller|spacious)\b/i.test(requestedOutcome)) {
    const localPreferencePatch: AppearancePatch = {};
    if (/\b(cobalt|blue)\b/i.test(requestedOutcome)) localPreferencePatch.colour = "cobalt";
    if (/\b(tide|teal|turquoise)\b/i.test(requestedOutcome)) localPreferencePatch.colour = "tide";
    if (/\b(amber|gold|golden)\b/i.test(requestedOutcome)) localPreferencePatch.colour = "amber";
    if (/\b(extra large|very large|larger|bigger)\b/i.test(requestedOutcome)) localPreferencePatch.typeScale = "extra";
    else if (/\b(large|readable)\b/i.test(requestedOutcome)) localPreferencePatch.typeScale = "large";
    if (/\b(compact|dense|focused)\b/i.test(requestedOutcome)) localPreferencePatch.density = "compact";
    if (/\b(relaxed|spacious|roomy)\b/i.test(requestedOutcome)) localPreferencePatch.density = "relaxed";
    if (/\b(reduced motion|less motion|no animation|calm motion)\b/i.test(requestedOutcome)) localPreferencePatch.motion = "reduced";
    if (/\b(restore motion|more motion)\b/i.test(requestedOutcome)) localPreferencePatch.motion = "calm";

    return {
      scope: "presentation",
      label: "Personal presentation change",
      summary: "Arthur recognised a reversible presentation preference. Once you approve it, only the matching local preference can be applied in this preview; no provider or code change is contacted.",
      requestedOutcome,
      affectedAreas: unique(["Presentation preferences", "Workspace colour, type scale, density, or motion", "Visual-result preference remains unchanged"]),
      requiredRoom: "Local preference layer",
      reviewSteps: ["Confirm the affected preference", "Apply only the approved local setting", "Review the visible result"],
      rollback: "Restore the previous presentation preference or choose Restore default presentation.",
      approvalAllowed: true,
      ...(Object.keys(localPreferencePatch).length > 0 ? { localPreferencePatch } : {}),
    };
  }

  if (/\b(voice|tone|personality|polite|direct|dry wit|language|speak|accent|friend)\b/i.test(requestedOutcome)) {
    return {
      scope: "voice-language",
      label: "Voice, language, or demeanor change",
      summary: "Arthur recognised a conversational-style request. It can stage the requested behaviour for review, but a live voice or model change needs an approved provider and explicit testing before it is enabled.",
      requestedOutcome,
      affectedAreas: ["Demeanor controls", "Voice Studio profile", "Language and speech-provider configuration"],
      requiredRoom: "Speech, translation & language",
      vaultCategory: "Speech, translation & language",
      reviewSteps: ["Confirm the intended tone or language", "Review the provider and sample output", "Test with consent before enabling voice behaviour"],
      rollback: "Restore the previous demeanor, voice style, or language preference.",
      approvalAllowed: true,
    };
  }

  if (/\b(connect|integrate|api|provider|service|calendar|music|home assistant|app)\b/i.test(requestedOutcome)) {
    return {
      scope: "integration",
      label: "Provider integration request",
      summary: "Arthur recognised a request to connect a service. Approval only prepares a scoped integration plan; credentials remain developer-managed, a connection test is required, and the provider is never contacted from this preview.",
      requestedOutcome,
      affectedAreas: ["API Vault capability room", "Server-side credential adapter", "Permission and connection-test policy"],
      requiredRoom: "App building, code & deployment",
      vaultCategory: "App building, code & deployment",
      reviewSteps: ["Name the intended provider and function", "Review credential ownership and permissions", "Test the connection before enabling any route"],
      rollback: "Disable the capability room and remove its credential reference; retain the prior approved route.",
      approvalAllowed: true,
    };
  }

  if (/\b(add|build|create|feature|capability|automate|teach|learn|improve|redesign|change yourself|customi[sz]e)\b/i.test(requestedOutcome)) {
    return {
      scope: "capability",
      label: "Reviewable capability change",
      summary: "Arthur recognised a request to extend its software. Approval records a proposal only: an authorized development workspace must still show the implementation diff, tests, and a rollback checkpoint before any change is made.",
      requestedOutcome,
      affectedAreas: ["Requested assistant capability", "Permissions and provider routing", "Implementation tests and rollback checkpoint"],
      requiredRoom: "App building, code & deployment",
      vaultCategory: "App building, code & deployment",
      reviewSteps: ["Confirm the outcome and safety scope", "Review the proposed files, permissions, and test plan", "Approve a separate implementation review"],
      rollback: "Restore the checkpoint captured immediately before an independently approved implementation.",
      approvalAllowed: true,
    };
  }

  return clarification(requestedOutcome);
}
