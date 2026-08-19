import { describe, expect, it } from "vitest";
import { apiCatalogue, catalogueCounts } from "./apiCatalogue";

describe("Arthur API placeholder catalogue", () => {
  it("keeps every capability category routable to an explicit ownership and authentication boundary", () => {
    expect(apiCatalogue.length).toBeGreaterThanOrEqual(25);
    for (const category of apiCatalogue) {
      expect(category.id).not.toHaveLength(0);
      expect(category.function).not.toHaveLength(0);
      expect(category.providers.length).toBeGreaterThan(0);
      expect(category.auth).not.toHaveLength(0);
      expect(category.owner).not.toHaveLength(0);
    }
  });

  it("keeps sensitive financial, health, security, social, and cloud rooms behind review", () => {
    for (const id of ["payments", "health", "security", "social", "cloud"]) {
      expect(apiCatalogue.find((category) => category.id === id)?.reviewRequired).toBe(true);
    }
    expect(catalogueCounts.providers).toBeGreaterThan(120);
  });
});
