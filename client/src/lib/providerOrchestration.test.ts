import { describe, expect, it } from "vitest";
import { recommendProviderStep, type RouteStep } from "./providerOrchestration";

const route: RouteStep[] = [
  { label: "Primary", category: "A", role: "Primary", quality: 4, cost: 3 },
  { label: "Support", category: "B", role: "Support", quality: 5, cost: 2 },
  { label: "Fallback", category: "C", role: "Fallback", quality: 3, cost: 1 },
];

const available = { A: true, B: true, C: true };

describe("recommendProviderStep", () => {
  it("keeps the declared chain untouched while balanced recommends its primary step", () => {
    expect(route.map((step) => step.role)).toEqual(["Primary", "Support", "Fallback"]);
    expect(recommendProviderStep(route, "balanced", available)?.label).toBe("Primary");
  });

  it("changes only the recommendation for quality and cost preferences", () => {
    expect(recommendProviderStep(route, "quality", available)?.label).toBe("Support");
    expect(recommendProviderStep(route, "cost", available)?.label).toBe("Fallback");
    expect(route.map((step) => step.label)).toEqual(["Primary", "Support", "Fallback"]);
  });

  it("does not recommend an unavailable room", () => {
    expect(recommendProviderStep(route, "quality", { A: true, B: false, C: true })?.label).toBe("Primary");
  });
});
