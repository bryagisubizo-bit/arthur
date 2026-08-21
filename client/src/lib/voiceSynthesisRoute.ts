export type VoiceSynthesisRouteId = "local_windows_tts" | "developer_neural_tts";

export type VoiceSynthesisRoute = {
  id: VoiceSynthesisRouteId;
  label: string;
  detail: string;
  boundary: string;
};

export const voiceSynthesisRouteOptions: VoiceSynthesisRoute[] = [
  {
    id: "local_windows_tts",
    label: "Local Windows speech engine",
    detail: "Arthur passes approved reply text to the installed local speech engine.",
    boundary: "Selecting this route does not download a neural voice model or start the microphone.",
  },
  {
    id: "developer_neural_tts",
    label: "Developer-configured neural voice provider",
    detail: "A separately configured provider may synthesize approved reply text after a connection is tested.",
    boundary: "Selecting this route does not connect a provider or transmit text.",
  },
];

export function voiceSynthesisRouteById(value: string | null | undefined): VoiceSynthesisRoute | undefined {
  return voiceSynthesisRouteOptions.find((route) => route.id === value);
}

export function requireVoiceSynthesisRoute(value: string) {
  const route = voiceSynthesisRouteById(value);
  if (!route) {
    return { valid: false as const, message: "Choose how Arthur should speak approved replies before authorising the profile." };
  }
  return { valid: true as const, route };
}
