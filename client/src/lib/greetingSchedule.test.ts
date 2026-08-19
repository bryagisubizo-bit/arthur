import { describe, expect, it } from "vitest";
import { isInLocalTimeWindow, renderGreeting } from "./greetingSchedule";

describe("Arthur local greeting schedule", () => {
  it("treats an overnight Do Not Disturb window as active after its start and before its end", () => {
    expect(isInLocalTimeWindow("23:15", "22:00", "07:00")).toBe(true);
    expect(isInLocalTimeWindow("06:59", "22:00", "07:00")).toBe(true);
    expect(isInLocalTimeWindow("12:00", "22:00", "07:00")).toBe(false);
  });

  it("expands only documented local greeting tokens", () => {
    expect(renderGreeting("Good {time_of_day}, {recipient}.", "Madam Aline", true, 9)).toBe("Good morning, Madam Aline.");
  });
});
