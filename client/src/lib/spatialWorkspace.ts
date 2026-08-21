/**
 * Local-only spatial layout engine.
 *
 * This file intentionally models visual workspace events, not device input or
 * network traffic. A future approved transport can relay these typed events,
 * but rendering a workspace never opens a socket, camera, microphone, or provider.
 */
export type SpatialEventKind = "module.focus" | "module.move" | "module.discard" | "module.restore";
export type SpatialZone = "focus" | "periphery" | "ambient";

export type SpatialCoordinate = {
  x: number;
  y: number;
  z: number;
  zone: SpatialZone;
};

export type SpatialModule = {
  id: string;
  label: string;
  category: "context" | "signal" | "control";
  detail: string;
  preferredZone: Exclude<SpatialZone, "focus">;
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

export type SpatialCoordinateRevision = {
  schema: "arthur.coordinate.v1";
  transport: "closed";
  revision: number;
  actor: "local-user";
  event: SpatialEventKind | "initial";
  focusedModuleId: string;
  modules: Array<{ id: string; label: string; coordinate: SpatialCoordinate }>;
};

const initialModules: SpatialModule[] = [
  { id: "research", label: "Research field", category: "context", detail: "Approved source context remains visible.", preferredZone: "periphery" },
  { id: "diagnostics", label: "System diagnostics", category: "signal", detail: "Local read-only health surface.", preferredZone: "periphery" },
  { id: "notes", label: "Private note", category: "context", detail: "User-controlled local note surface.", preferredZone: "periphery" },
  { id: "voice", label: "Voice signal", category: "signal", detail: "Speech readiness, not microphone capture.", preferredZone: "periphery" },
  { id: "home", label: "Smart-home review", category: "control", detail: "Connection proposal only; no device control.", preferredZone: "ambient" },
];

const preferredCoordinates: Record<string, Omit<SpatialCoordinate, "zone">> = {
  diagnostics: { x: -72, y: -8, z: 40 },
  notes: { x: 72, y: 8, z: 40 },
  voice: { x: -64, y: 58, z: 35 },
  home: { x: 0, y: -70, z: 10 },
};

/**
 * Calculate workspace-relative placement only. These numbers are never desktop
 * pixel positions and this helper never moves a Windows application.
 */
export function coordinateForSpatialModule(module: SpatialModule, focusedId: string): SpatialCoordinate {
  if (module.id === focusedId) return { x: 0, y: 0, z: 300, zone: "focus" };
  const preferred = preferredCoordinates[module.id] ?? { x: 64, y: -36, z: 35 };
  return { ...preferred, zone: module.preferredZone };
}

/**
 * Create JSON-ready local state for browser/desktop parity. The fixed closed
 * transport value makes explicit that rendering this revision does not open a
 * WebSocket or send it anywhere.
 */
export function coordinateRevision(state: SpatialWorkspaceState): SpatialCoordinateRevision {
  return {
    schema: "arthur.coordinate.v1",
    transport: "closed",
    revision: state.revision,
    actor: "local-user",
    event: state.lastEvent?.kind ?? "initial",
    focusedModuleId: state.focusedId,
    modules: state.modules.map((module) => ({ id: module.id, label: module.label, coordinate: coordinateForSpatialModule(module, state.focusedId) })),
  };
}

export function modulesInSpatialZone(state: SpatialWorkspaceState, zone: SpatialZone): SpatialModule[] {
  return state.modules.filter((module) => coordinateForSpatialModule(module, state.focusedId).zone === zone);
}

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
