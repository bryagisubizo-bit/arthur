/**
 * Browser-preview contract for Arthur's Windows-only application bridge.
 * It intentionally has no browser automation, capture, clipboard, or native APIs.
 */
export const applicationBridgeActions = [
  "inspect_accessible_controls",
  "navigate_visible_interface",
  "click",
  "type",
  "clipboard",
  "file_selection",
  "communication",
] as const;

export type ApplicationBridgeAction = (typeof applicationBridgeActions)[number];

export type ApplicationBridgeScope = {
  title: string;
  approved: boolean;
};

export function createApplicationScope(title: string, approved = false): ApplicationBridgeScope | null {
  const cleaned = title.trim();
  return cleaned && cleaned.length <= 120 ? { title: cleaned, approved } : null;
}

export function applicationBridgeStatus(scope: ApplicationBridgeScope | null) {
  if (!scope) return "Closed. The browser preview cannot enumerate, inspect, or control desktop applications.";
  if (!scope.approved) return `Scope entered for “${scope.title}”, but desktop inspection remains blocked until that exact app is approved.`;
  return `Approved review scope: “${scope.title}”. Clicks, typing, clipboard, files, and communication still need separate confirmation.`;
}

export function prepareApplicationNavigation(scope: ApplicationBridgeScope | null, goal: string) {
  if (!scope?.approved) return { state: "blocked" as const, detail: "Choose and approve one visible desktop app before preparing a navigation plan." };
  return {
    state: "prepared" as const,
    detail: `Plan prepared locally for “${scope.title}”: ${goal.trim() || "review visible interface"}. No application was inspected or changed.`,
  };
}

export function bridgeActionState(scope: ApplicationBridgeScope | null, action: ApplicationBridgeAction) {
  if (!scope?.approved) return { state: "blocked" as const, detail: "Per-app approval is required." };
  if (["click", "type", "clipboard", "file_selection", "communication"].includes(action)) {
    return { state: "confirmation_required" as const, detail: `${action.replaceAll("_", " ")} requires execution-time confirmation in Windows.` };
  }
  return { state: "review_required" as const, detail: "This preview cannot access Windows UI Automation; use the installed desktop prototype after reviewing its optional adapter." };
}
