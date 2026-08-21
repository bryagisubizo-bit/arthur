import { describe, expect, it } from "vitest";
import { applicationBridgeStatus, bridgeActionState, createApplicationScope, prepareApplicationNavigation } from "./applicationBridge";

describe("application bridge contract", () => {
  it("remains closed until an exact app scope is approved", () => {
    const scope = createApplicationScope("Untitled - Notepad");
    expect(scope?.approved).toBe(false);
    expect(applicationBridgeStatus(scope)).toContain("blocked");
    expect(prepareApplicationNavigation(scope, "Open File").state).toBe("blocked");
  });

  it("prepares plans but still blocks consequential desktop actions", () => {
    const scope = createApplicationScope("Untitled - Notepad", true);
    expect(prepareApplicationNavigation(scope, "Open File").state).toBe("prepared");
    expect(bridgeActionState(scope, "click").state).toBe("confirmation_required");
    expect(bridgeActionState(scope, "inspect_accessible_controls").state).toBe("review_required");
  });
});
