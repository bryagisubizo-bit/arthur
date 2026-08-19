export const defensiveLookupBlockedActions = [
  "Active scanning",
  "Exploitation",
  "Credential testing",
  "Malware handling",
  "Automatic actions",
] as const;

export type DefensiveLookupDecision =
  | { kind: "disabled"; reason: string }
  | { kind: "blocked"; reason: string }
  | { kind: "needs-target"; reason: string }
  | { kind: "awaiting-approval"; target: string; operation: string; approval: string };

export type DefensiveLookupApproval =
  | { kind: "not-ready"; reason: string }
  | { kind: "approved"; target: string; operation: string; nextStep: string };

const blockedRequestPattern = /\b(scan|scanning|exploit|exploitation|credential|password|brute[\s-]?force|malware|payload|automatic action|auto[-\s]?run)\b/i;

/**
 * This records a local, non-networked lookup request. It intentionally does
 * not select a provider, issue an HTTP request, or prepare any follow-up work.
 */
export function requestDefensiveLookup(request: string, enabled: boolean): DefensiveLookupDecision {
  const target = request.trim();
  if (!enabled) return { kind: "disabled", reason: "Enable defensive lookups before preparing a request." };
  if (!target) return { kind: "needs-target", reason: "State one URL, domain, IP address, file hash, indicator, or CVE to review." };
  if (blockedRequestPattern.test(target)) {
    return { kind: "blocked", reason: "That request falls outside Arthur’s passive defensive lookup boundary." };
  }
  return {
    kind: "awaiting-approval",
    target,
    operation: "Passive reputation, exposure, vulnerability, or threat-context lookup",
    approval: "One explicit approval is required before Arthur prepares this lookup for an approved connected provider.",
  };
}

/** A requested lookup cannot become prepared until this exact request is approved. */
export function approveDefensiveLookup(decision: DefensiveLookupDecision | null): DefensiveLookupApproval {
  if (!decision || decision.kind !== "awaiting-approval") {
    return { kind: "not-ready", reason: "Only one waiting passive lookup can be approved and prepared." };
  }
  return {
    kind: "approved",
    target: decision.target,
    operation: decision.operation,
    nextStep: "No provider was contacted. Arthur now requires an approved connected provider and a separate routing review.",
  };
}
