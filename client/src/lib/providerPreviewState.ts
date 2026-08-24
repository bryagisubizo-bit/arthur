export type ProviderPreviewOutcome = "key-required" | "desktop-test-required" | "local-setup-required" | "desktop-setup-ready";

export function previewProviderOutcome(provider: string, hasDraftCredential: boolean, action: "test" | "save"): ProviderPreviewOutcome {
  if (provider === "openWakeWord") return "local-setup-required";
  if (!hasDraftCredential) return "key-required";
  return action === "test" ? "desktop-test-required" : "desktop-setup-ready";
}
