import { describe, expect, it } from "vitest";
import { cloudGatewayState, validateCloudGatewayEndpoint, type CloudGatewayDraft } from "./cloudGateway";

const draft: CloudGatewayDraft = {
  providerLabel: "Developer-configured provider",
  endpoint: "https://gateway.example.test/v1",
  approvedData: "Approved text only",
  streamingRequested: false,
};

describe("cloud gateway contract", () => {
  it("accepts HTTPS only and keeps streaming separate", () => {
    expect(validateCloudGatewayEndpoint(draft.endpoint).valid).toBe(true);
    expect(validateCloudGatewayEndpoint("http://gateway.example.test").valid).toBe(false);
    expect(validateCloudGatewayEndpoint("wss://gateway.example.test").valid).toBe(false);
    expect(draft.streamingRequested).toBe(false);
  });

  it("keeps configured and privacy-locked gateways closed", () => {
    expect(cloudGatewayState(draft, false)).toMatch(/Prepared only/);
    expect(cloudGatewayState(draft, true)).toMatch(/Privacy lock/);
  });
});
