export type SymptomGuidance = {
  urgency: "information needed" | "guidance only" | "urgent review" | "emergency";
  heading: string;
  summary: string;
  nextStep: string;
};

const emergencyTerms = [
  "chest pain", "trouble breathing", "difficulty breathing", "shortness of breath",
  "face drooping", "one sided weakness", "one-sided weakness", "cannot speak",
  "unconscious", "passed out", "seizure", "severe bleeding", "anaphylaxis",
  "severe allergic", "suicidal", "self harm", "self-harm",
];

const urgentTerms = [
  "high fever", "dehydrated", "cannot keep fluids", "severe pain", "pregnant",
  "worsening", "blood in", "confused", "persistent vomiting",
];

export function prepareSymptomGuidance(symptoms: string): SymptomGuidance {
  const text = symptoms.toLowerCase().replace(/\s+/g, " ").trim();
  if (!text) {
    return {
      urgency: "information needed",
      heading: "Tell Arthur what you are experiencing.",
      summary: "Arthur can organise symptoms and explain when professional care may be important, but it cannot diagnose a disease.",
      nextStep: "Describe what you feel, when it started, whether it is worsening, and any relevant conditions or medicines you choose to mention.",
    };
  }
  if (emergencyTerms.some((term) => text.includes(term))) {
    return {
      urgency: "emergency",
      heading: "Please seek emergency help now.",
      summary: "Your description includes a possible emergency warning sign. Arthur cannot safely assess its cause from text.",
      nextStep: "Contact local emergency services now, or ask someone nearby to help. Do not wait for an app response if symptoms are severe, sudden, or worsening.",
    };
  }
  if (urgentTerms.some((term) => text.includes(term))) {
    return {
      urgency: "urgent review",
      heading: "A prompt clinical review may be appropriate.",
      summary: "Arthur cannot determine which condition is causing these symptoms. Some details can need an assessment sooner rather than later.",
      nextStep: "Contact a clinician, urgent-care service, or local health advice line today. Seek emergency care immediately if severe or new warning signs appear.",
    };
  }
  return {
    urgency: "guidance only",
    heading: "This is information, not a diagnosis.",
    summary: "Arthur cannot tell you which disease you have or rule out a serious cause from a message. It can help you prepare clear information for a clinician.",
    nextStep: "Consider a clinician or pharmacist if symptoms persist, worsen, concern you, or affect daily activities. Seek urgent help for severe, sudden, or rapidly worsening symptoms.",
  };
}
