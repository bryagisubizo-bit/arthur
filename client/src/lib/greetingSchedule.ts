export type GreetingKind = "introduction" | "opening" | "wake";

export const defaultGreetingScripts: Record<GreetingKind, string> = {
  introduction: "Good {time_of_day}, {recipient}. I am Arthur, your local desktop assistant. I am ready when you are.",
  opening: "Good {time_of_day}, {recipient}. Arthur is ready when you are.",
  wake: "Yes, {recipient}. Arthur is ready.",
};

export function isInLocalTimeWindow(current: string, start: string, end: string): boolean {
  const asMinutes = (value: string) => {
    const [hour, minute] = value.split(":").map(Number);
    return Number.isInteger(hour) && Number.isInteger(minute) && hour >= 0 && hour < 24 && minute >= 0 && minute < 60 ? hour * 60 + minute : null;
  };
  const now = asMinutes(current); const from = asMinutes(start); const until = asMinutes(end);
  if (now === null || from === null || until === null || from === until) return false;
  return from < until ? now >= from && now < until : now >= from || now < until;
}

export function localDayPart(hour: number): string {
  return hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
}

export function renderGreeting(script: string, recipient: string, useTimeOfDay: boolean, hour: number): string {
  const safeScript = script.trim().slice(0, 240) || defaultGreetingScripts.opening;
  return safeScript.replaceAll("{recipient}", recipient).replaceAll("{time_of_day}", useTimeOfDay ? localDayPart(hour) : "day");
}
