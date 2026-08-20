"""Minimal plugin contract for Arthur integrations.

Plugins declare their capabilities and risk level. Arthur’s future orchestrator
must enforce permissions and confirmations before invoking a plugin.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Optional


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    display_name: str
    description: str
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    risk_level: str = "read_only"  # read_only, write, sensitive, destructive, admin
    requires_api_key: bool = False
    requires_user_confirmation: bool = False


class ArthurPlugin:
    manifest: PluginManifest

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def health_check(self) -> Dict[str, Any]:
        return {"plugin": self.manifest.plugin_id, "ready": False, "reason": "Not configured"}

    def actions(self) -> Iterable[str]:
        return ()

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Plugins must implement execute safely.")


class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, ArthurPlugin] = {}

    def register(self, plugin: ArthurPlugin) -> None:
        plugin_id = plugin.manifest.plugin_id
        if plugin_id in self._plugins:
            raise ValueError(f"Plugin already registered: {plugin_id}")
        self._plugins[plugin_id] = plugin

    def get(self, plugin_id: str) -> Optional[ArthurPlugin]:
        return self._plugins.get(plugin_id)

    def manifests(self) -> list[PluginManifest]:
        return [plugin.manifest for plugin in self._plugins.values()]
