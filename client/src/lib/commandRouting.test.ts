import { describe, expect, it } from "vitest";
import { findProviderNeed } from "./commandRouting";

describe("provider capability routing", () => {
  it("names the approved catalogue category required for external research", () => {
    expect(findProviderNeed("Research the latest information")?.room).toBe("Web research");
  });

  it("does not invent a provider category for a local diagnostic", () => {
    expect(findProviderNeed("Check my disk space")).toBeUndefined();
  });
});
