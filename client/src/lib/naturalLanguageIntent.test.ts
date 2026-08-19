import { describe, expect, it } from "vitest";
import { assessNaturalLanguage } from "./naturalLanguageIntent";

describe("natural language intent routing", () => {
  it("recognises alternate wording for a volume request", () => {
    expect(assessNaturalLanguage("Could you make it quieter?").kind).toBe("device-control");
    expect(assessNaturalLanguage("Could you make it quieter?").vaultCategory).toBe("Windows & local desktop");
  });

  it("maps provider-assisted outcomes to real catalogue categories and keeps local presentation offline", () => {
    expect(assessNaturalLanguage("Please research this").vaultCategory).toBe("Search, news & research");
    expect(assessNaturalLanguage("Arthur, improve yourself").vaultCategory).toBe("App building, code & deployment");
    expect(assessNaturalLanguage("Change the colour theme").vaultCategory).toBeUndefined();
  });

  it("keeps self-improvement requests review-only", () => {
    const result = assessNaturalLanguage("Arthur, improve yourself with a clearer notes screen");
    expect(result.kind).toBe("self-improvement");
    expect(result.consequence).toBe("proposal");
  });

  it("requests clarification rather than fabricating a route", () => {
    expect(assessNaturalLanguage("Do the thing").kind).toBe("clarification");
  });
});
