import {
  createSelfCustomizationProposal,
  type AppearancePatch,
  type SelfCustomizationProposal,
} from "./selfCustomization";

export type SelfCustomizationLifecycleState = "idle" | "prepared" | "approved" | "rejected" | "clarification";

export type SelfCustomizationLifecycle = {
  state: SelfCustomizationLifecycleState;
  proposal?: SelfCustomizationProposal;
  appliedPreferencePatch?: AppearancePatch;
};

export function prepareSelfCustomization(request: string): SelfCustomizationLifecycle {
  const proposal = createSelfCustomizationProposal(request);
  return {
    state: proposal.scope === "clarification" ? "clarification" : "prepared",
    proposal,
  };
}

export function approveSelfCustomization(lifecycle: SelfCustomizationLifecycle): SelfCustomizationLifecycle {
  if (lifecycle.state !== "prepared" || !lifecycle.proposal?.approvalAllowed) return lifecycle;
  return {
    state: "approved",
    proposal: lifecycle.proposal,
    ...(lifecycle.proposal.localPreferencePatch ? { appliedPreferencePatch: lifecycle.proposal.localPreferencePatch } : {}),
  };
}

export function rejectSelfCustomization(lifecycle: SelfCustomizationLifecycle): SelfCustomizationLifecycle {
  if (lifecycle.state !== "prepared" || !lifecycle.proposal) return lifecycle;
  return { state: "rejected", proposal: lifecycle.proposal };
}

export function reviseSelfCustomization(): SelfCustomizationLifecycle {
  return { state: "idle" };
}
