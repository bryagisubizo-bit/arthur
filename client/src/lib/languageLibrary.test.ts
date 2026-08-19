import { describe, expect, it } from "vitest";
import { createPrivateColloquialDraft, filterLanguages, findLanguage, getSourceConfirmedExpressions, languageFromPreferenceRequest, prepareMultilingualSearch, prepareSourceConfirmedExpression } from "./languageLibrary";

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

  it("keeps cited endangered-language expressions scoped to their region and source", () => {
    const records = getSourceConfirmedExpressions("Haida");
    expect(records).toHaveLength(1);
    expect(records[0].regionalContext).toContain("Northern dialect");
    expect(records[0].evidenceUrl).toMatch(/^https:/);
    expect(records[0].reviewStatus).toBe("Source-confirmed — not community-reviewed");
  });

  it("requires attested HTTPS evidence without upgrading a record to community review", () => {
    const preview = prepareSourceConfirmedExpression({
      language: "Manx", expression: "Example", meaning: "Example meaning", regionalContext: "Isle of Man",
      useContext: "Context documented by the source", sensitivityNote: "Use only in the cited context",
      evidenceKind: "community-language-program", evidenceTitle: "Named community resource", evidenceUrl: "https://example.org/source", evidenceReviewed: true,
    });
    expect(preview.reviewStatus).toBe("Source-confirmed — not community-reviewed");
    expect(preview.verificationNote).toContain("not community review");
    expect(() => prepareSourceConfirmedExpression({
      language: "Manx", expression: "Example", meaning: "Example meaning", regionalContext: "Isle of Man",
      useContext: "Context", sensitivityNote: "Note", evidenceKind: "community-language-program", evidenceTitle: "Named source", evidenceUrl: "http://example.org", evidenceReviewed: true,
    })).toThrow("HTTPS");
  });
});
