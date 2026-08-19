import { describe, expect, it } from "vitest";
import { createPrivateColloquialDraft, filterLanguages, findLanguage, languageFromPreferenceRequest, prepareMultilingualSearch } from "./languageLibrary";

describe("Arthur language library", () => {
  it("finds language names, codes, and native labels locally", () => {
    expect(filterLanguages("rw").some((entry) => entry.name === "Kinyarwanda")).toBe(true);
    expect(filterLanguages("Français").some((entry) => entry.name === "French")).toBe(true);
    expect(filterLanguages("العربية").some((entry) => entry.name === "Arabic")).toBe(true);
    expect(findLanguage("Navajo")?.name).toBe("Diné Bizaad (Navajo)");
    expect(findLanguage("nv")?.communityReview).toContain("community review");
  });

  it("recognises a reviewed language-preference request without a provider call", () => {
    expect(languageFromPreferenceRequest("Arthur, speak in Arabic")?.code).toBe("ar");
    expect(languageFromPreferenceRequest("Research Arabic poetry")).toBeUndefined();
  });

  it("keeps a multilingual research question unchanged and review-only", () => {
    const prepared = prepareMultilingualSearch("amakuru y'ikoranabuhanga", "Kinyarwanda");
    expect(prepared.ready).toBe(true);
    expect(prepared.query).toBe("amakuru y'ikoranabuhanga");
    expect(prepared.reason).toContain("approved research provider");
  });

  it("stores only a clearly unverified private colloquial draft", () => {
    const draft = createPrivateColloquialDraft("Navajo", "sample expression", "regional context", "source to verify");
    expect(draft.language).toBe("Diné Bizaad (Navajo)");
    expect(draft.reviewStatus).toBe("Private draft — not community reviewed");
    expect(() => createPrivateColloquialDraft("English", "", "regional context", "source")).toThrow("expression");
  });
});
