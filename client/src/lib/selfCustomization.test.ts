import { describe, expect, it } from "vitest";
import { createSelfCustomizationProposal } from "./selfCustomization";

describe("Arthur self-customisation proposals", () => {
  it("creates a reversible local presentation proposal from natural phrasing", () => {
    const proposal = createSelfCustomizationProposal("Arthur, use larger compact writing when I am focusing.");
    expect(proposal.scope).toBe("presentation");
    expect(proposal.approvalAllowed).toBe(true);
    expect(proposal.localPreferencePatch).toEqual({ typeScale: "extra", density: "compact" });
  });

  it("recognises a requested workspace colour without involving a provider", () => {
    const proposal = createSelfCustomizationProposal("Use the tide theme when I am writing.");
    expect(proposal.scope).toBe("presentation");
    expect(proposal.localPreferencePatch).toEqual({ colour: "tide" });
    expect(proposal.vaultCategory).toBeUndefined();
  });

  it("routes a new capability through a review-only development proposal", () => {
    const proposal = createSelfCustomizationProposal("Please add a capability that organises my project notes.");
    expect(proposal.scope).toBe("capability");
    expect(proposal.vaultCategory).toBe("App building, code & deployment");
    expect(proposal.rollback).toContain("checkpoint");
  });

  it("does not permit safety-control removal proposals", () => {
    const proposal = createSelfCustomizationProposal("Remove the confirmation requirement for actions.");
    expect(proposal.scope).toBe("protected-boundary");
    expect(proposal.approvalAllowed).toBe(false);
  });

  it("asks for clarification instead of inventing an implementation", () => {
    expect(createSelfCustomizationProposal("Make it better somehow").scope).toBe("clarification");
  });
});
