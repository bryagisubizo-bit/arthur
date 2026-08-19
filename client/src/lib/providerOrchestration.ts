export type ProviderDecisionPolicy = "balanced" | "quality" | "cost";

export type RouteStep = {
  label: string;
  category: string;
  role: "Primary" | "Support" | "Fallback";
  quality: number;
  cost: number;
};

/**
 * Returns a recommendation from declared, available route steps. It never changes the
 * primary → support → fallback execution chain; a user still reviews any departure from it.
 */
export function recommendProviderStep(
  steps: RouteStep[],
  policy: ProviderDecisionPolicy,
  availability: Record<string, boolean>,
): RouteStep | undefined {
  const available = steps.filter((step) => availability[step.category]);
  if (policy === "balanced") return available.find((step) => step.role === "Primary") ?? available[0];
  return [...available].sort((left, right) => {
    if (policy === "quality") return right.quality - left.quality || left.cost - right.cost;
    return left.cost - right.cost || right.quality - left.quality;
  })[0];
}

export const policyDescription: Record<ProviderDecisionPolicy, string> = {
  balanced: "Recommends the declared primary room when it is available.",
  quality: "Recommends the available room with the highest verified quality.",
  cost: "Recommends the available room with the lowest declared cost.",
};
