/**
 * Browser-preview contract for a future cloud gateway. It never performs a
 * request, persists credentials, or opens a WebSocket from the preview.
 */
export type CloudGatewayDraft = {
  providerLabel: string;
  endpoint: string;
  approvedData: string;
  streamingRequested: boolean;
};

export const cloudGatewayPresets = [
  "Developer-configured provider",
  "OpenAI-compatible HTTPS gateway",
  "Azure AI gateway",
  "Google Cloud gateway",
  "Private company gateway",
] as const;

export const lowResourcePolicy = {
  deviceTarget: "Windows 11 · 8 GB RAM · ~2.4 GHz CPU",
  localWork: "Consent, native layout, manual monitor review, and display state.",
  cloudWork: "Only explicitly approved text or selected metadata through HTTPS.",
  transportDefault: "closed",
  streamingDefault: "off",
  polling: "No background polling; future approved clients use bounded retry/backoff.",
} as const;

export function validateCloudGatewayEndpoint(endpoint: string): { valid: boolean; detail: string } {
  const candidate = endpoint.trim();
  if (!candidate) return { valid: false, detail: "Enter an HTTPS endpoint only when you are ready to review a connection." };
  try {
    const parsed = new URL(candidate);
    if (parsed.protocol !== "https:") return { valid: false, detail: "Only HTTPS gateways are eligible; streaming and loopback transports are separate future approvals." };
    return { valid: true, detail: "Endpoint format accepted for a later, separate connection review. No request is sent." };
  } catch {
    return { valid: false, detail: "Enter a complete HTTPS URL, for example https://gateway.example.com/v1." };
  }
}

export function cloudGatewayState(draft: CloudGatewayDraft, privacyLocked: boolean): string {
  if (privacyLocked) return "Privacy lock is holding cloud routes closed.";
  if (!draft.endpoint.trim()) return "Closed — no gateway endpoint or credential reference is configured.";
  return validateCloudGatewayEndpoint(draft.endpoint).valid
    ? "Prepared only — no key, request, stream, or data transfer is active."
    : "Blocked — correct the endpoint format before a later connection review.";
}
