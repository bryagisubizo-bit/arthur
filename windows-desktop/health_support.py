"""Cautious symptom-support wording for Arthur; never a diagnosis engine."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SymptomGuidance:
    urgency: str
    heading: str
    summary: str
    next_step: str
    emergency: bool


EMERGENCY_TERMS = (
    "chest pain", "trouble breathing", "difficulty breathing", "shortness of breath",
    "face drooping", "one sided weakness", "one-sided weakness", "cannot speak",
    "unconscious", "passed out", "seizure", "severe bleeding", "anaphylaxis",
    "severe allergic", "suicidal", "self harm", "self-harm",
)
URGENT_TERMS = (
    "high fever", "dehydrated", "cannot keep fluids", "severe pain", "pregnant",
    "worsening", "blood in", "confused", "persistent vomiting",
)


def prepare_symptom_guidance(symptoms: str) -> SymptomGuidance:
    text = " ".join(symptoms.lower().split())
    if not text:
        return SymptomGuidance(
            "information needed",
            "Tell me what you are experiencing.",
            "Arthur can help organise symptoms and explain when professional care may be important, but it cannot diagnose a disease.",
            "Describe what you feel, when it started, whether it is getting worse, and any relevant medical conditions or medicines you want to mention.",
            False,
        )
    if any(term in text for term in EMERGENCY_TERMS):
        return SymptomGuidance(
            "emergency",
            "Please seek emergency help now.",
            "Your description includes a possible emergency warning sign. Arthur cannot assess its cause safely from text.",
            "Contact your local emergency service now, or ask someone nearby to help. Do not wait for an app response if symptoms are severe, sudden, or worsening.",
            True,
        )
    if any(term in text for term in URGENT_TERMS):
        return SymptomGuidance(
            "urgent review",
            "A prompt clinical review may be appropriate.",
            "Arthur cannot determine what condition is causing these symptoms. Some details you mentioned can need assessment sooner rather than later.",
            "Contact a clinician, urgent-care service, or local health advice line today; seek emergency care immediately if symptoms become severe or new warning signs appear.",
            False,
        )
    return SymptomGuidance(
        "guidance only",
        "This is information, not a diagnosis.",
        "Arthur cannot tell you which disease you have or rule out a serious cause from a message. It can help you prepare clear information for a clinician.",
        "Consider a clinician or pharmacist if symptoms persist, worsen, concern you, or affect daily activities. Seek urgent help for severe, sudden, or rapidly worsening symptoms.",
        False,
    )
