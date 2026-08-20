import { describe, expect, it } from "vitest";
import { requireSpeechRecognitionRoute, speechRecognitionRouteOptions } from "./speechRecognitionRoute";

describe("speech-recognition route selection", () => {
  it("requires a deliberate route rather than accepting an empty startup value", () => {
    expect(requireSpeechRecognitionRoute("")).toEqual({
      valid: false,
      message: "Choose how Arthur should recognise spoken commands before authorising the profile.",
    });
  });

  it("exposes both local/offline and developer-configured provider routes", () => {
    expect(speechRecognitionRouteOptions.map((entry) => entry.id)).toEqual(["local-offline", "developer-provider"]);
    expect(requireSpeechRecognitionRoute("local-offline").valid).toBe(true);
    expect(requireSpeechRecognitionRoute("developer-provider").valid).toBe(true);
  });
});
