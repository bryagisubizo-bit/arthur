export const speechRecognitionRouteOptions = [
  {
    id: "local-offline",
    label: "Local / offline speech recognition",
    detail: "Requires your separate approval to install a local recognition engine and download language models. Audio remains on this PC when the approved engine is running.",
  },
  {
    id: "developer-provider",
    label: "Developer-configured speech-to-text provider",
    detail: "Requires an approved developer-managed provider connection and a separate microphone/listening consent. Arthur does not transmit audio until that route is connected and you enable it.",
  },
] as const;

export type SpeechRecognitionRouteId = (typeof speechRecognitionRouteOptions)[number]["id"];

export function requireSpeechRecognitionRoute(value: string) {
  const route = speechRecognitionRouteOptions.find((entry) => entry.id === value);
  if (!route) {
    return { valid: false as const, message: "Choose how Arthur should recognise spoken commands before authorising the profile." };
  }
  return { valid: true as const, route };
}
