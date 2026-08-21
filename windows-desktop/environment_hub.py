"""Disconnected environment-hub proposal contracts for Arthur.

Arthur never discovers a local network, opens an MQTT connection, uses a Home
Assistant token, or changes a device because this module was imported. It only
validates a human-readable proposal so a user can review it later.
"""

from dataclasses import asdict, dataclass
from urllib.parse import urlparse


VALID_MOODS = {"calm", "focus", "neutral"}


@dataclass(frozen=True)
class EnvironmentProposal:
    provider: str
    scene_name: str
    mood: str
    endpoint: str
    scope: str
    transport: str = "closed"
    state: str = "proposal_only"


def prepare_home_assistant_proposal(endpoint: str, scene_name: str, mood: str = "focus") -> dict:
    """Validate a proposed Home Assistant scene without making an HTTP request."""
    parsed = urlparse(str(endpoint).strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Use a complete Home Assistant endpoint such as https://homeassistant.local:8123.")
    if mood not in VALID_MOODS:
        raise ValueError("Mood must be calm, focus, or neutral; Arthur does not infer emotion for device control.")
    if not str(scene_name).strip():
        raise ValueError("Name the one scene that a later explicit review may authorize.")
    return asdict(EnvironmentProposal("Home Assistant", str(scene_name).strip(), mood, parsed.geturl(), "one named scene"))


def prepare_mqtt_proposal(broker_url: str, topic: str, mood: str = "focus") -> dict:
    """Validate a proposed MQTT topic without connecting to a broker."""
    parsed = urlparse(str(broker_url).strip())
    if parsed.scheme not in {"mqtt", "mqtts"} or not parsed.netloc:
        raise ValueError("Use a complete MQTT or MQTTS broker URL; no broker is contacted during review.")
    cleaned_topic = str(topic).strip().strip("/")
    if not cleaned_topic or "#" in cleaned_topic or "+" in cleaned_topic:
        raise ValueError("Use one explicit MQTT publication topic; wildcard topics are not accepted.")
    if mood not in VALID_MOODS:
        raise ValueError("Mood must be calm, focus, or neutral; Arthur does not infer emotion for device control.")
    return asdict(EnvironmentProposal("MQTT", cleaned_topic, mood, parsed.geturl(), "one explicit publication topic"))
