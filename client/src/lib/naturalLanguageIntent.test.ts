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

  it("recognises supported reply-language requests as an offline local preference", () => {
    const result = assessNaturalLanguage("Arthur, vuga mu Kinyarwanda");
    expect(result.kind).toBe("language-preference");
    expect(result.requiredRoom).toContain("Local profile preference");
  });

  it("keeps messaging as a reviewable draft and app routes as reviewed actions", () => {
    const draft = assessNaturalLanguage("Text someone on WhatsApp");
    expect(draft.kind).toBe("message-draft");
    expect(draft.consequence).toBe("review");
    expect(draft.summary).toContain("never selects a contact");
    expect(assessNaturalLanguage("open camera").kind).toBe("app-launch");
  });

  it("keeps visual feedback local and voice cloning proposal-gated", () => {
    expect(assessNaturalLanguage("show the voice orb").kind).toBe("voice-visualizer");
    const cloning = assessNaturalLanguage("clone my voice");
    expect(cloning.kind).toBe("voice-cloning");
    expect(cloning.consequence).toBe("proposal");
  });

  it("requests clarification rather than fabricating a route", () => {
    expect(assessNaturalLanguage("Do the thing").kind).toBe("clarification");
  });
});
