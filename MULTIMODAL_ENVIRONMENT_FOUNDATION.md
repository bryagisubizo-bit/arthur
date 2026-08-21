# Arthur: Lightweight Multimodal & Environment Foundation

> **Current implementation state:** the coordinate contract, adapter registry, and environment proposals are reviewable local code only. Arthur does not open a capture device, listen on a socket, contact a cloud service, connect to Home Assistant or MQTT, discover a network, or change a device.

## Component tree

```text
Arthur Spatial Workspace
├── Coordinate Layer
│   ├── Focus zone: current card, X/Y/Z = 0/0/300
│   ├── Periphery: supporting local cards
│   └── Ambient: low-priority local review cards
├── Contextual Core
│   ├── Local revision state (arthur.coordinate.v1)
│   ├── Consent ledger boundary
│   └── Optional future adapter gateway
└── Adapter Layer — all disabled / transport closed
    ├── Speech pipeline
    ├── Camera vision matrix
    ├── Explicit screen/window share
    ├── Loopback coordinate relay
    └── Home Assistant / MQTT environment proposal
```

## API and transport configurations

| Adapter | Current state | Future activation requirements | Credential only when activation is approved |
|---|---|---|---|
| Speech pipeline | Disabled; transport closed | Route selection, device consent, engine/provider review | Developer key only for a provider route |
| Vision matrix | Disabled; transport closed | Spatial Room unlocked, selected camera, visible time-bounded session | Developer key only for an external vision provider |
| Screen/window share | Disabled; transport closed | Per-session operating-system picker and exact share boundary | Developer key only for approved external analysis |
| Coordinate relay | Disabled; transport closed | Loopback port, named client, session duration, firewall review | Authenticated relay credential only for remote synchronization |
| Home Assistant / MQTT | Disconnected proposal | Endpoint, one scene/topic, developer credential, per-action approval | Home Assistant long-lived token or MQTT credentials |

The optional Python `local_coordinate_server.py` builds only JSON-ready `arthur.coordinate.v1` messages. Its startup contract is loopback-only and returns `no_listener_started`; a WebSocket server is deliberately not included. FastAPI’s official WebSocket design uses a connection manager and explicit endpoint route, which Arthur reserves for a later approved runtime adapter rather than enabling by default.[1]

Home Assistant’s WebSocket API requires authentication after a client connects, while MQTT requires a broker and explicit topics. Arthur therefore validates only a future proposal and rejects wildcard MQTT topics; it never discovers a network or attempts control from the UI.[2]

## Low-resource design

The browser and desktop coordinate layers use small in-memory objects, no 3D runtime, no database writes, no local daemon, and no polling loop. This preserves the baseline Windows target. A future live stream should be **opt-in**, loopback-bound first, rate-limited, time-bounded, and disabled when the protected Spatial Room locks.

## References

[1]: https://fastapi.tiangolo.com/advanced/websockets/ "FastAPI — WebSockets"
[2]: https://developers.home-assistant.io/docs/api/websocket/ "Home Assistant — WebSocket API"
