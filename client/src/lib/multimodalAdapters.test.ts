import { describe, expect, it } from "vitest";
import { multimodalAdapterContracts, multimodalContractById } from "./multimodalAdapters";

describe("multimodal adapter contracts", () => {
  it("keeps all capture, streaming, and environment adapters disabled with a closed transport", () => {
    expect(multimodalAdapterContracts).toHaveLength(5);
    expect(multimodalAdapterContracts.every((contract) => contract.defaultState === "disabled" && contract.transport === "closed")).toBe(true);
  });

  it("describes the credentials and explicit activation boundary for the environment hub", () => {
    const environment = multimodalContractById("environment_hub");
    expect(environment?.credentials).toContain("Home Assistant");
    expect(environment?.activationRequirement).toContain("approve each control action");
  });
});
