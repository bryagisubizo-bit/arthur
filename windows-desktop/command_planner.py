"""Arthur's safe natural-language command planning layer.

This module intentionally does not accept arbitrary shell text from an LLM or user.
It converts a narrow, reviewed set of PC-management requests into fixed command argv
lists, classifies risk, requires confirmation where appropriate, and emits audit-safe
records. New command families must be added as explicit templates and reviewed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
import os
import platform
import re
import subprocess
from typing import Iterable

from language_library import find_language


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CommandPlan:
    intent: str
    summary: str
    shell: str
    argv: tuple[str, ...]
    risk: RiskLevel
    requires_confirmation: bool
    allowed: bool
    reason: str = ""

    def preview(self) -> str:
        """Return a copyable, transparent preview without executing anything."""
        if not self.allowed:
            return f"Blocked: {self.reason}"
        return " ".join(self.argv)

    def audit_record(self, outcome: str) -> dict[str, str | bool]:
        """Do not log raw user text, file contents, credentials, or environment values."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intent": self.intent,
            "risk": self.risk.value,
            "requires_confirmation": self.requires_confirmation,
            "outcome": outcome,
        }


BLOCKED_TERMS = {
    "disable antivirus",
    "disable firewall",
    "bypass authentication",
    "steal password",
    "dump credentials",
    "extract cookies",
    "reverse shell",
    "keylogger",
    "ransomware",
    "ddos",
    "phishing",
    "exploit",
    "scan public",
    "scan network",
    "hack",
    "breach",
}

LANGUAGE_ALIASES = {
    "English": ("english", "anglais", "icyongereza"),
    "Kinyarwanda": ("kinyarwanda", "ikinyarwanda", "rwanda"),
    "French": ("french", "français", "francais", "french language"),
    "Kiswahili": ("kiswahili", "swahili", "kiwahili"),
}


def language_switch_target(request: str) -> str | None:
    """Return a supported response-language request without changing configuration.

    The desktop UI repeats the choice and persists it only after handling the
    reviewed plan. This helper intentionally understands a few common phrases
    rather than pretending to translate arbitrary commands.
    """
    normalized = re.sub(r"\s+", " ", request.casefold()).strip()
    if not any(marker in normalized for marker in ("speak", "talk", "parle", "vuga", "ongea", "sema")):
        return None
    for language, aliases in LANGUAGE_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return language
    # The local catalogue may suggest an additional profile language, but this
    # remains a preference update only. It never downloads a pack, translates
    # the command, enables listening, or contacts a provider.
    for token in re.findall(r"[\w\-]+", normalized, flags=re.UNICODE):
        entry = find_language(token)
        if entry is not None:
            return entry.name
    return None


def _blocked(message: str) -> CommandPlan:
    return CommandPlan(
        intent="blocked_request",
        summary="Arthur will not prepare or execute that operation.",
        shell="none",
        argv=(),
        risk=RiskLevel.BLOCKED,
        requires_confirmation=False,
        allowed=False,
        reason=message,
    )


def _needs_wsl(distro: str) -> CommandPlan:
    return CommandPlan(
        intent="configure_wsl",
        summary="A verified WSL distribution must be selected before Arthur can run local Linux diagnostics.",
        shell="none",
        argv=(),
        risk=RiskLevel.MEDIUM,
        requires_confirmation=False,
        allowed=False,
        reason=f"Configure a trusted WSL distribution first. Current value: {distro or 'not set'}.",
    )


class CommandPlanner:
    """Maps recognised phrases to a deliberately small, safe command allowlist."""

    def __init__(self, *, wsl_distro: str = "", approved_directories: Iterable[str] = ()):
        self.wsl_distro = wsl_distro.strip()
        self.approved_directories = {str(Path(path).expanduser().resolve()) for path in approved_directories}

    def plan(self, request: str) -> CommandPlan:
        normalized = re.sub(r"\s+", " ", request.casefold()).strip()
        if not normalized:
            return _blocked("Say or type a specific approved computer task.")
        if any(term in normalized for term in BLOCKED_TERMS):
            return _blocked("Arthur only supports authorized PC administration and does not prepare intrusion, credential, evasion, or attack commands.")

        if "kali" in normalized or "linux" in normalized or "wsl" in normalized:
            return self._plan_wsl(normalized)
        return self._plan_windows(normalized)

    def _plan_windows(self, request: str) -> CommandPlan:
        language = language_switch_target(request)
        if language:
            return CommandPlan(
                "language_switch",
                f"Switch Arthur's reply language to {language}. Arthur will repeat the selection before using it.",
                "local-preference",
                (),
                RiskLevel.LOW,
                False,
                True,
            )

        templates: list[tuple[tuple[str, ...], CommandPlan]] = [
            (
                (
                    "open spatial workspace",
                    "open the spatial workspace",
                    "open spatial room",
                    "open the spatial room",
                    "show spatial workspace",
                    "take me to spatial workspace",
                    "go to spatial workspace",
                ),
                CommandPlan(
                    "open_spatial_workspace",
                    "Open Arthur's protected Spatial workspace after local access verification.",
                    "local-navigation",
                    (),
                    RiskLevel.MEDIUM,
                    True,
                    True,
                ),
            ),
            (
                ("system status", "computer status", "system information"),
                CommandPlan("system_information", "Collect Windows system information.", "cmd", ("systeminfo",), RiskLevel.LOW, False, True),
            ),
            (
                ("who am i", "current user"),
                CommandPlan("current_user", "Show the signed-in Windows account name.", "cmd", ("whoami",), RiskLevel.LOW, False, True),
            ),
            (
                ("ip address", "network address", "network status"),
                CommandPlan("network_information", "Show local network adapter configuration.", "cmd", ("ipconfig",), RiskLevel.LOW, False, True),
            ),
            (
                ("list processes", "running apps", "running applications", "what is running"),
                CommandPlan("process_information", "List running Windows processes.", "cmd", ("tasklist",), RiskLevel.LOW, False, True),
            ),
            (
                ("disk space", "storage status", "drive space"),
                CommandPlan(
                    "storage_information",
                    "Show available file-system space.",
                    "powershell",
                    ("powershell.exe", "-NoProfile", "-Command", "Get-PSDrive -PSProvider FileSystem"),
                    RiskLevel.LOW,
                    False,
                    True,
                ),
            ),
            (
                ("check internet", "test internet", "internet connection"),
                CommandPlan("internet_check", "Perform a basic connectivity check to a public resolver.", "cmd", ("ping", "-n", "1", "1.1.1.1"), RiskLevel.LOW, False, True),
            ),
            (
                ("lock computer", "lock pc", "lock my computer"),
                CommandPlan("lock_workstation", "Lock this Windows session.", "windows", ("rundll32.exe", "user32.dll,LockWorkStation"), RiskLevel.MEDIUM, True, True),
            ),
            (
                ("open camera", "launch camera", "start camera"),
                CommandPlan("launch_camera", "Open the installed Windows Camera app through its fixed URI. Arthur requires your explicit approval before launching it.", "windows-uri", ("ms-camera:",), RiskLevel.MEDIUM, True, True),
            ),
            (
                ("text someone on whatsapp", "message someone on whatsapp", "send a whatsapp message", "open whatsapp and text someone"),
                CommandPlan("whatsapp_message_draft", "Prepare a WhatsApp draft only. Arthur will ask for the recipient and exact message, then the user sends it in WhatsApp.", "message-draft", (), RiskLevel.MEDIUM, True, True),
            ),
            (
                ("open whatsapp", "launch whatsapp", "start whatsapp"),
                CommandPlan("launch_whatsapp", "Open the installed WhatsApp app through its fixed URI. Arthur requires your explicit approval before launching it.", "windows-uri", ("whatsapp:",), RiskLevel.MEDIUM, True, True),
            ),
        ]
        for phrases, plan in templates:
            if any(phrase in request for phrase in phrases):
                return plan
        return _blocked("Arthur has no reviewed command template for that request. Add it through the developer command registry; it cannot run arbitrary generated shell text.")

    def _plan_wsl(self, request: str) -> CommandPlan:
        if not self.wsl_distro:
            return _needs_wsl(self.wsl_distro)
        prefix = ("wsl.exe", "-d", self.wsl_distro, "--")
        templates: list[tuple[tuple[str, ...], CommandPlan]] = [
            (("system status", "system information"), CommandPlan("linux_system_information", "Collect local Linux/WSL kernel information.", "wsl", prefix + ("uname", "-a"), RiskLevel.LOW, False, True)),
            (("who am i", "current user"), CommandPlan("linux_current_user", "Show the current Linux/WSL account name.", "wsl", prefix + ("whoami",), RiskLevel.LOW, False, True)),
            (("disk space", "storage status"), CommandPlan("linux_storage_information", "Show local Linux/WSL file-system space.", "wsl", prefix + ("df", "-h"), RiskLevel.LOW, False, True)),
            (("memory", "ram"), CommandPlan("linux_memory_information", "Show local Linux/WSL memory use.", "wsl", prefix + ("free", "-h"), RiskLevel.LOW, False, True)),
            (("network status", "ip address"), CommandPlan("linux_network_information", "Show local Linux/WSL network addresses.", "wsl", prefix + ("ip", "addr"), RiskLevel.LOW, False, True)),
            (("list processes", "running apps"), CommandPlan("linux_process_information", "List local Linux/WSL processes.", "wsl", prefix + ("ps", "aux"), RiskLevel.LOW, False, True)),
        ]
        for phrases, plan in templates:
            if any(phrase in request for phrase in phrases):
                return plan
        return _blocked("Arthur only permits reviewed local diagnostics for a configured WSL/Kali environment. Network scanning, exploitation, credential collection, and arbitrary Kali commands are not enabled.")

    def execute(self, plan: CommandPlan, *, approved: bool = False, timeout_seconds: int = 25) -> tuple[int, str, str]:
        """Execute a reviewed command without a shell after policy approval.

        Callers must collect explicit approval for medium/high risk plans. The function
        does not accept raw command text and never uses shell=True.
        """
        if not plan.allowed:
            raise PermissionError(plan.reason)
        if plan.requires_confirmation and not approved:
            raise PermissionError("This command requires an explicit confirmation from the signed-in user.")
        if plan.shell == "local-preference":
            return 0, "Local preference updated by the desktop interface.", ""
        if plan.shell == "local-navigation":
            return 0, "Local navigation is completed by the desktop interface after access verification.", ""
        if plan.shell == "message-draft":
            return 0, "Message draft prepared; no message was sent.", ""
        if plan.shell == "windows-uri":
            if os.name != "nt":
                raise OSError("Windows URI application launching is available only in the Windows desktop build.")
            os.startfile(plan.argv[0])  # type: ignore[attr-defined]  # nosec B606 - fixed reviewed URI only
            return 0, f"Opened reviewed Windows URI: {plan.argv[0]}", ""
        completed = subprocess.run(
            plan.argv,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            cwd=str(Path.home()),
            env={**os.environ},
        )
        return completed.returncode, completed.stdout, completed.stderr


def plan_to_dict(plan: CommandPlan) -> dict[str, object]:
    """Small serialization helper for UI rendering; callers must not persist secrets."""
    payload = asdict(plan)
    payload["argv"] = list(plan.argv)
    payload["risk"] = plan.risk.value
    payload["preview"] = plan.preview()
    return payload
