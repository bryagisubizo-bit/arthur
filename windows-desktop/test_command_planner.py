"""Focused regression checks for Arthur's reviewed local-command policy."""

from command_planner import CommandPlanner, RiskLevel, language_switch_target


def main() -> None:
    windows = CommandPlanner()
    system = windows.plan("Arthur, show my system status")
    assert system.allowed is True
    assert system.risk == RiskLevel.LOW
    assert system.argv == ("systeminfo",)

    lock = windows.plan("please lock my computer")
    assert lock.allowed is True
    assert lock.requires_confirmation is True
    assert lock.risk == RiskLevel.MEDIUM

    language = windows.plan("Arthur, speak in Kinyarwanda please")
    assert language.allowed is True
    assert language.intent == "language_switch"
    assert language.requires_confirmation is False
    assert language_switch_target("vuga mu Kinyarwanda") == "Kinyarwanda"
    extended_language = windows.plan("Arthur, speak in Arabic")
    assert extended_language.allowed is True
    assert extended_language.intent == "language_switch"
    assert language_switch_target("Arthur, speak in Arabic") == "Arabic"

    camera = windows.plan("open camera")
    assert camera.allowed is True
    assert camera.argv == ("ms-camera:",)
    assert camera.requires_confirmation is True
    assert camera.risk == RiskLevel.MEDIUM

    whatsapp = windows.plan("open WhatsApp")
    assert whatsapp.allowed is True
    assert whatsapp.argv == ("whatsapp:",)
    assert whatsapp.requires_confirmation is True

    message = windows.plan("text someone on WhatsApp")
    assert message.allowed is True
    assert message.intent == "whatsapp_message_draft"
    assert message.argv == ()
    assert message.requires_confirmation is True

    spatial = windows.plan("Arthur, open the spatial room")
    assert spatial.allowed is True
    assert spatial.intent == "open_spatial_workspace"
    assert spatial.shell == "local-navigation"
    assert spatial.argv == ()
    assert spatial.requires_confirmation is True

    blocked = windows.plan("scan a public network and hack it")
    assert blocked.allowed is False
    assert blocked.risk == RiskLevel.BLOCKED

    linux_without_setup = windows.plan("show Kali Linux memory")
    assert linux_without_setup.allowed is False

    wsl = CommandPlanner(wsl_distro="kali-linux")
    linux_memory = wsl.plan("show Kali Linux memory")
    assert linux_memory.allowed is True
    assert linux_memory.argv[:4] == ("wsl.exe", "-d", "kali-linux", "--")


if __name__ == "__main__":
    main()
