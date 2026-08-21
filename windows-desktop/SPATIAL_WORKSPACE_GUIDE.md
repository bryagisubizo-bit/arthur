# Arthur Spatial Workspace Guide

## What works now

Arthur’s **Spatial Workspace** is a protected local canvas for arranging Arthur’s own modules. After choosing one local access method and unlocking the room, users can select, drag/reorder, scale, discard, and restore the visible workspace cards. The browser preview includes the same module layout contract and a contextual node map.

> **Selecting, arranging, or viewing modules does not activate camera access, microphone capture, environmental sensing, provider connections, smart-home control, background execution, or network synchronization.**

| Surface | Current behavior | Data boundary |
|---|---|---|
| Browser preview | Local browser state for cards, focus, revisions, discard, restore, and node-map display. | No WebSocket or provider connection opens. |
| Windows app | Protected local room with touch controls and optional, separately approved local air-gesture flow. | No camera is opened unless the user separately confirms the local gesture or face-access workflow. |
| Contextual graph | Shows the selected module, visible modules, and a local revision/event message. | It is a visual explanation, not an agent tool call or telemetry feed. |

## How to use the current local workspace

1. Open **Spatial Workspace** in Arthur and choose one room-access method: local password, Windows Hello, or the experimental local camera face route.
2. Unlock the room using that method.
3. Select a card, use previous/next controls, or drag cards to change their order. Use **Discard selected** only for the current layout and **Undo discard** to restore it.
4. Read the contextual module map to see the local focus and last layout event. “No transport open” means nothing is being synchronized to another device or service.

## Future activation gates

Any future adapter needs its **own** visible setup, purpose, scope, revoke control, and test. A spatial layout action alone can never enable an adapter.

| Future capability | Required before activation | Not enabled by this release |
|---|---|---|
| Local air gestures | Room unlock, camera selection, clear check box, explicit confirmation, and visible camera-active test. | Camera opening, frame retention, hand-template storage. |
| Real-time shared workspace | Authenticated session design, persistent transport review, data-retention policy, and a user session start control. | Socket connection, background transport, cross-device sync. |
| Provider-backed visual analysis | Developer-configured provider route, approved key storage, scope notice, connection test, and per-use user confirmation. | Uploading visual, audio, file, or workspace content. |
| Agent tool gateway | Typed tool manifest, policy evaluation, consent record, and separate confirmation for consequential actions. | Ambient execution, arbitrary app control, or implicit device access. |

## Implementation map

The browser’s local state contract is in `client/src/lib/spatialWorkspace.ts`; it is covered by `client/src/lib/spatialWorkspace.test.ts`. `SpatialContextGraph.tsx` renders the visual node-map adapter. The Windows equivalent appears in `app.py` under `SpatialWorkspacePage`, where its map explicitly states that no transport is open.

For the deeper component boundaries and current technology references, see [SPATIAL_ARCHITECTURE.md](./SPATIAL_ARCHITECTURE.md).
