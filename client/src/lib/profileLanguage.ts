import { findLanguage, languageLibrary, type LanguageEntry } from "./languageLibrary";

export type PrimarySystemLanguage = Pick<LanguageEntry, "name" | "code" | "nativeLabel" | "readiness">;

export type PrimarySystemLanguageResult =
  | { valid: true; language: PrimarySystemLanguage }
  | { valid: false; message: string };

export const primarySystemLanguageOptions: PrimarySystemLanguage[] = languageLibrary.map(({ name, code, nativeLabel, readiness }) => ({
  name,
  code,
  nativeLabel,
  readiness,
}));

/**
 * Validate a profile’s deliberate primary language choice without starting
 * listening, recording, translation, or a provider request.
 */
export function requirePrimarySystemLanguage(value: string): PrimarySystemLanguageResult {
  const selected = value.trim();
  if (!selected) {
    return { valid: false, message: "Choose a primary system language before using Arthur’s typed or voice interactions." };
  }
  const language = findLanguage(selected);
  if (!language) {
    return { valid: false, message: "Choose a language from Arthur’s local language library." };
  }
  return {
    valid: true,
    language: {
      name: language.name,
      code: language.code,
      nativeLabel: language.nativeLabel,
      readiness: language.readiness,
    },
  };
}
