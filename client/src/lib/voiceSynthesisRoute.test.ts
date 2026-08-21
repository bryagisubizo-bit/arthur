import { describe, expect, it } from "vitest";
import { requireVoiceSynthesisRoute, voiceSynthesisRouteById, voiceSynthesisRouteOptions } from "./voiceSynthesisRoute";

describe("voice synthesis routes", () => {
  it("offers a local and a separately configured provider route", () => {
    expect(voiceSynthesisRouteOptions.map((route) => route.id)).toEqual(["local_windows_tts", "developer_neural_tts"]);
  });

  it("does not treat an unknown selection as a valid route", () => {
    expect(voiceSynthesisRouteById("untrusted")).toBeUndefined();
    expect(requireVoiceSynthesisRoute("")).toEqual({ valid: false, message: "Choose how Arthur should speak approved replies before authorising the profile." });
  });
});
