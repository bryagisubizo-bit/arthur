export type ProviderNeed = {
  phrases: readonly string[];
  room: string;
  reason: string;
};

/**
 * Maps only clearly external requests to the declared API catalogue category
 * needed to continue. It never selects a substitute provider or generates a
 * command when an approved resource is absent.
 */
export const providerNeeds: readonly ProviderNeed[] = [
  {
    phrases: ["research", "search the web", "latest information"],
    room: "Web research",
    reason: "No approved Web research API room is connected. Add a search provider in the API vault to continue.",
  },
  {
    phrases: ["calendar", "meeting", "schedule"],
    room: "Calendar & productivity",
    reason: "No approved Calendar & productivity API room is connected. Add a calendar provider in the API vault to continue.",
  },
  {
    phrases: ["play music", "play song", "sing", "make a song"],
    room: "Music",
    reason: "No approved Music API room is connected. Add a music provider in the API vault to continue.",
  },
  {
    phrases: ["home assistant", "lights", "thermostat", "smart home"],
    room: "Smart home",
    reason: "No approved Smart home API room is connected. Add a Home Assistant room in the API vault to continue.",
  },
  {
    phrases: ["analyse screen", "analyze screen", "analyse file", "analyze file"],
    room: "Files & documents",
    reason: "No approved Files & documents room is connected. Add an analysis provider and select the source to continue.",
  },
];

export function findProviderNeed(request: string): ProviderNeed | undefined {
  const input = request.trim().toLowerCase();
  return providerNeeds.find(({ phrases }) => phrases.some((phrase) => input.includes(phrase)));
}
