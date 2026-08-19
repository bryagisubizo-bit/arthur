import { describe, expect, it } from "vitest";
import { prepareSymptomGuidance } from "./symptomSupport";

describe("Arthur symptom support", () => {
  it("does not diagnose routine symptoms", () => {
    const guidance = prepareSymptomGuidance("A mild headache started yesterday");
    expect(guidance.urgency).toBe("guidance only");
    expect(guidance.summary).toContain("cannot tell you which disease");
  });

  it("flags potential emergency warning signs for urgent help", () => {
    const guidance = prepareSymptomGuidance("I have chest pain and trouble breathing");
    expect(guidance.urgency).toBe("emergency");
    expect(guidance.nextStep).toContain("emergency services");
  });
});
