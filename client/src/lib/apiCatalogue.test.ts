import { describe, expect, it } from "vitest";
import { apiCatalogue, catalogueCounts, providerPlaceholderKey } from "./apiCatalogue";

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

  it("lists the requested threat-intelligence providers only in the review-required defensive room", () => {
    const security = apiCatalogue.find((category) => category.id === "security");
    const requestedProviders = [
      "SecurityTrails", "URLScan.io", "AlienVault OTX", "GreyNoise", "IBM X-Force", "CrowdStrike", "Microsoft Defender",
      "Google Safe Browsing", "Have I Been Pwned", "NIST NVD", "MITRE ATT&CK", "CVE.org", "EPSS", "OpenCTI",
      "MISP", "PhishTank", "URLhaus", "MalwareBazaar", "ThreatFox", "CIRCL",
    ];

    expect(security).toMatchObject({ auth: "Review required", owner: "Review required", reviewRequired: true });
    expect(security?.function).toContain("never performs active scanning");
    expect(security?.providers).toEqual(expect.arrayContaining(requestedProviders));
    expect(new Set(security?.providers).size).toBe(security?.providers.length);
  });

  it("keeps provider placeholders unique within each room and assigns category-scoped React keys", () => {
    const keys = new Set<string>();

    for (const category of apiCatalogue) {
      expect(new Set(category.providers).size).toBe(category.providers.length);
      for (const provider of category.providers) {
        keys.add(providerPlaceholderKey(category.id, provider));
      }
    }

    expect(keys.size).toBe(catalogueCounts.providers);
  });
});
