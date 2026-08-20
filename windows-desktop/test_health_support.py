"""Regression checks for Arthur's cautious symptom-support wording."""

from health_support import prepare_symptom_guidance


def main():
    empty = prepare_symptom_guidance("")
    routine = prepare_symptom_guidance("I have had a mild headache since yesterday")
    urgent = prepare_symptom_guidance("I have a high fever and feel worse")
    emergency = prepare_symptom_guidance("I have chest pain and trouble breathing")
    assert empty.urgency == "information needed"
    assert routine.urgency == "guidance only"
    assert "cannot tell you which disease" in routine.summary
    assert urgent.urgency == "urgent review"
    assert emergency.emergency is True
    assert "emergency" in emergency.urgency
    print("Arthur symptom-support checks passed.")


if __name__ == "__main__":
    main()
