/**
 * Arthur's browser-facing multimodal contract. It is declarative only: the
 * preview has no getUserMedia call, screen-capture request, socket, broker, or
 * provider client. A later installed-app adapter must obtain its own consent.
 */
export type MultimodalAdapterId = "speech_stream" | "vision_matrix" | "screen_share" | "coordinate_stream" | "environment_hub";

export type MultimodalAdapterContract = {
  id: MultimodalAdapterId;
  label: string;
  input: string;
  defaultState: "disabled";
  transport: "closed";
  activationRequirement: string;
  credentials: string;
};

export const multimodalAdapterContracts: readonly MultimodalAdapterContract[] = [
  { id: "speech_stream", label: "Speech streaming", input: "Microphone and speaker", defaultState: "disabled", transport: "closed", activationRequirement: "Choose a speech route, then separately approve the device and engine or provider.", credentials: "No key for local engines; developer-managed key only for an approved provider." },
  { id: "vision_matrix", label: "Vision matrix", input: "Camera frames", defaultState: "disabled", transport: "closed", activationRequirement: "Unlock the Spatial Room and approve a visible, time-bounded local camera session.", credentials: "No key for local-only handling; developer-managed key only for an approved external vision provider." },
  { id: "screen_share", label: "Screen or window share", input: "One user-selected display or window", defaultState: "disabled", transport: "closed", activationRequirement: "Choose the exact display or window in the operating-system picker for each session.", credentials: "No key for local capture; developer-managed key only before approved external analysis." },
  { id: "coordinate_stream", label: "Coordinate revision relay", input: "Arthur layout JSON", defaultState: "disabled", transport: "closed", activationRequirement: "Approve a loopback port, named local client, session lifetime, and firewall boundary.", credentials: "No key for an approved loopback listener; authenticated relay credentials for any remote sync." },
  { id: "environment_hub", label: "Home Assistant or MQTT hub", input: "One named scene or topic", defaultState: "disabled", transport: "closed", activationRequirement: "Enter an endpoint, developer credential, and one reviewed scene or topic, then approve each control action.", credentials: "Home Assistant long-lived access token or MQTT credentials only after explicit integration approval." },
] as const;

export function multimodalContractById(id: string): MultimodalAdapterContract | undefined {
  return multimodalAdapterContracts.find((contract) => contract.id === id);
}
