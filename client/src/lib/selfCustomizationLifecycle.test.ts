import { describe, expect, it } from "vitest";
import {
  approveSelfCustomization,
  prepareSelfCustomization,
  rejectSelfCustomization,
  reviseSelfCustomization,
} from "./selfCustomizationLifecycle";

describe("Arthur self-customisation lifecycle", () => {
  it("prepares a proposal without applying a local preference", () => {
    const prepared = prepareSelfCustomization("Use larger compact writing when I am focusing.");
    expect(prepared.state).toBe("prepared");
    expect(prepared.appliedPreferencePatch).toBeUndefined();
  });

  it("applies only the reviewed local patch after explicit approval", () => {
    const prepared = prepareSelfCustomization("Use the tide theme with larger compact writing.");
    const approved = approveSelfCustomization(prepared);
    expect(approved.state).toBe("approved");
    expect(approved.appliedPreferencePatch).toEqual({ colour: "tide", typeScale: "extra", density: "compact" });
  });

  it("does not apply a preference when the proposal is rejected or revised", () => {
    const prepared = prepareSelfCustomization("Use the tide theme with larger compact writing.");
    const rejected = rejectSelfCustomization(prepared);
    expect(rejected.state).toBe("rejected");
    expect(rejected.appliedPreferencePatch).toBeUndefined();
    expect(reviseSelfCustomization()).toEqual({ state: "idle" });
  });

  it("cannot approve an informative proposal that would remove a protected safety boundary", () => {
    const prepared = prepareSelfCustomization("Remove the confirmation requirement for actions.");
    expect(prepared.state).toBe("prepared");
    expect(approveSelfCustomization(prepared)).toEqual(prepared);
  });
});
