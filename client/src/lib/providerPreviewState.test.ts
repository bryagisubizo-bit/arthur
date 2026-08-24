import { describe, expect, it } from "vitest";
import { previewProviderOutcome } from "./providerPreviewState";

describe("previewProviderOutcome", () => {
  it("does not claim a connection when a browser preview has no credential", () => {
    expect(previewProviderOutcome("OpenAI", false, "test")).toBe("key-required");
  });

  it("sends entered preview values to the desktop setup path rather than testing them", () => {
    expect(previewProviderOutcome("Anthropic", true, "test")).toBe("desktop-test-required");
    expect(previewProviderOutcome("SerpAPI", true, "save")).toBe("desktop-setup-ready");
  });

  it("keeps local wake-word setup separate from provider testing", () => {
    expect(previewProviderOutcome("openWakeWord", true, "test")).toBe("local-setup-required");
  });
});
