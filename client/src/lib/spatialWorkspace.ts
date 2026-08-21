/**
 * Local-only spatial layout engine.
 *
 * This file intentionally models visual workspace events, not device input or
 * network traffic. A future approved transport can relay these typed events,
 * but rendering a workspace never opens a socket, camera, microphone, or provider.
 */
export type SpatialEventKind = "module.focus" | "module.move" | "module.discard" | "module.restore";

export type SpatialModule = {
  id: string;
  label: string;
  category: "context" | "signal" | "control";
  detail: string;
};

export type SpatialWorkspaceEvent = {
  id: string;
  revision: number;
  actor: "local-user";
  kind: SpatialEventKind;
  moduleId: string;
  at: number;
};

export type SpatialWorkspaceState = {
  modules: SpatialModule[];
  focusedId: string;
  discarded: { module: SpatialModule; index: number } | null;
  revision: number;
  lastEvent: SpatialWorkspaceEvent | null;
};

const initialModules: SpatialModule[] = [
  { id: "research", label: "Research field", category: "context", detail: "Approved source context remains visible." },
  { id: "diagnostics", label: "System diagnostics", category: "signal", detail: "Local read-only health surface." },
  { id: "notes", label: "Private note", category: "context", detail: "User-controlled local note surface." },
  { id: "voice", label: "Voice signal", category: "signal", detail: "Speech readiness, not microphone capture." },
  { id: "home", label: "Smart-home review", category: "control", detail: "Connection proposal only; no device control." },
];

export const createInitialSpatialWorkspace = (): SpatialWorkspaceState => ({
  modules: initialModules.map((module) => ({ ...module })),
  focusedId: initialModules[0].id,
  discarded: null,
  revision: 0,
  lastEvent: null,
});

function record(state: SpatialWorkspaceState, kind: SpatialEventKind, moduleId: string, at = Date.now()): SpatialWorkspaceState {
  const revision = state.revision + 1;
  return {
    ...state,
    revision,
    lastEvent: { id: `local-${revision}-${moduleId}`, revision, actor: "local-user", kind, moduleId, at },
  };
}

export function focusedSpatialModule(state: SpatialWorkspaceState) {
  return state.modules.find((module) => module.id === state.focusedId) ?? null;
}

export function focusSpatialModule(state: SpatialWorkspaceState, moduleId: string): SpatialWorkspaceState {
  if (!state.modules.some((module) => module.id === moduleId) || state.focusedId === moduleId) return state;
  return record({ ...state, focusedId: moduleId }, "module.focus", moduleId);
}

export function moveSpatialFocus(state: SpatialWorkspaceState, direction: number): SpatialWorkspaceState {
  if (!state.modules.length) return state;
  const currentIndex = Math.max(0, state.modules.findIndex((module) => module.id === state.focusedId));
  const nextIndex = (currentIndex + direction + state.modules.length) % state.modules.length;
  return focusSpatialModule(state, state.modules[nextIndex].id);
}

export function reorderSpatialModule(state: SpatialWorkspaceState, sourceId: string, targetId: string): SpatialWorkspaceState {
  const sourceIndex = state.modules.findIndex((module) => module.id === sourceId);
  const targetIndex = state.modules.findIndex((module) => module.id === targetId);
  if (sourceIndex < 0 || targetIndex < 0 || sourceIndex === targetIndex) return state;
  const modules = [...state.modules];
  const [source] = modules.splice(sourceIndex, 1);
  modules.splice(targetIndex, 0, source);
  return record({ ...state, modules }, "module.move", sourceId);
}

export function discardSpatialModule(state: SpatialWorkspaceState, moduleId: string): SpatialWorkspaceState {
  const index = state.modules.findIndex((module) => module.id === moduleId);
  if (index < 0) return state;
  const module = state.modules[index];
  const modules = state.modules.filter((item) => item.id !== moduleId);
  const nextFocus = modules[Math.min(index, Math.max(modules.length - 1, 0))]?.id ?? "";
  return record({ ...state, modules, focusedId: nextFocus, discarded: { module, index } }, "module.discard", moduleId);
}

export function restoreSpatialModule(state: SpatialWorkspaceState): SpatialWorkspaceState {
  if (!state.discarded) return state;
  const { module, index } = state.discarded;
  const modules = [...state.modules];
  modules.splice(Math.min(index, modules.length), 0, module);
  return record({ ...state, modules, focusedId: module.id, discarded: null }, "module.restore", module.id);
}
