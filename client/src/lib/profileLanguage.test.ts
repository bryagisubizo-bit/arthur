import { describe, expect, it } from "vitest";
import { primarySystemLanguageOptions, requirePrimarySystemLanguage } from "./profileLanguage";

describe("Arthur primary system language profile", () => {
  it("requires an explicit language before typed or voice interactions", () => {
    expect(requirePrimarySystemLanguage("").valid).toBe(false);
    expect(requirePrimarySystemLanguage("Unlisted language").valid).toBe(false);
  });

  it("accepts a language from the local catalogue and preserves its visible voice-routing label", () => {
    const selection = requirePrimarySystemLanguage("Kinyarwanda");
    expect(selection).toEqual({
      valid: true,
      language: expect.objectContaining({ name: "Kinyarwanda", code: "rw", nativeLabel: "Ikinyarwanda" }),
    });
    expect(primarySystemLanguageOptions.some((entry) => entry.name === "Diné Bizaad (Navajo)")).toBe(true);
  });
});
