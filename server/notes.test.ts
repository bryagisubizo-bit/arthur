import { describe, expect, it } from "vitest";
import { noteDraftSchema } from "./noteSchemas";

describe("Arthur personal note validation", () => {
  it("accepts an explicit study request on a private self note", () => {
    const result = noteDraftSchema.parse({
      category: "self",
      title: "Focus preference",
      content: "I prefer short spoken briefings before 09:00.",
      learningState: "studying",
      captureMethod: "typed",
    });

    expect(result.learningState).toBe("studying");
  });

  it("rejects blank notes rather than treating them as a learning signal", () => {
    expect(() => noteDraftSchema.parse({ category: "general", title: "", content: "" })).toThrow();
  });
});
