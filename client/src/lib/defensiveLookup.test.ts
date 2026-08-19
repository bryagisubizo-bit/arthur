import { describe, expect, it } from "vitest";
import { approveDefensiveLookup, defensiveLookupBlockedActions, requestDefensiveLookup } from "./defensiveLookup";

describe("defensive lookup gate", () => {
  it("does not prepare a lookup until the user explicitly enables the capability", () => {
    expect(requestDefensiveLookup("example.org", false)).toMatchObject({ kind: "disabled" });
  });

  it("holds one concrete target for approval instead of preparing it immediately", () => {
    expect(requestDefensiveLookup("", true)).toMatchObject({ kind: "needs-target" });
    const request = requestDefensiveLookup("CVE-2026-1234", true);
    expect(request).toEqual({
      kind: "awaiting-approval",
      target: "CVE-2026-1234",
      operation: "Passive reputation, exposure, vulnerability, or threat-context lookup",
      approval: "One explicit approval is required before Arthur prepares this lookup for an approved connected provider.",
    });
    expect(approveDefensiveLookup(request)).toEqual({
      kind: "approved",
      target: "CVE-2026-1234",
      operation: "Passive reputation, exposure, vulnerability, or threat-context lookup",
      nextStep: "No provider was contacted. Arthur now requires an approved connected provider and a separate routing review.",
    });
    expect(approveDefensiveLookup(null)).toMatchObject({ kind: "not-ready" });
  });

  it("blocks requests for excluded security actions before they can be prepared", () => {
    for (const request of ["scan example.org", "exploit CVE-2026-1234", "test a password", "handle malware", "auto-run remediation"]) {
      expect(requestDefensiveLookup(request, true)).toMatchObject({ kind: "blocked" });
    }
    expect(defensiveLookupBlockedActions).toEqual([
      "Active scanning",
      "Exploitation",
      "Credential testing",
      "Malware handling",
      "Automatic actions",
    ]);
  });
});
