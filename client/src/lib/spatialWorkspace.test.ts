import { describe, expect, it } from "vitest";
import {
  createInitialSpatialWorkspace,
  discardSpatialModule,
  focusedSpatialModule,
  moveSpatialFocus,
  reorderSpatialModule,
  restoreSpatialModule,
} from "./spatialWorkspace";

describe("local spatial workspace contract", () => {
  it("reorders only declared local modules and records a local-user event", () => {
    const state = createInitialSpatialWorkspace();
    const next = reorderSpatialModule(state, "voice", "research");
    expect(next.modules[0].id).toBe("voice");
    expect(next.lastEvent).toMatchObject({ actor: "local-user", kind: "module.move", moduleId: "voice" });
  });

  it("keeps a reversible discard and restores the local focus", () => {
    const state = createInitialSpatialWorkspace();
    const discarded = discardSpatialModule(state, "diagnostics");
    expect(discarded.modules.some((module) => module.id === "diagnostics")).toBe(false);
    const restored = restoreSpatialModule(discarded);
    expect(focusedSpatialModule(restored)?.id).toBe("diagnostics");
    expect(restored.lastEvent?.kind).toBe("module.restore");
  });

  it("moves focus within the current local module list without a transport", () => {
    const state = moveSpatialFocus(createInitialSpatialWorkspace(), 1);
    expect(focusedSpatialModule(state)?.id).toBe("diagnostics");
    expect(state.lastEvent?.actor).toBe("local-user");
  });
});
