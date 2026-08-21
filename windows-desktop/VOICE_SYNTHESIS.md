# Arthur Voice Synthesis Pathway

Arthur’s speech-output preference documents a safe pathway from an approved reply to audible output:

> **Approved reply text → speech units / selected engine → audio output**

The preference itself does not start a speech engine, download a neural model, clone a voice, open the microphone, connect a provider, send text or audio, or enable background work.

## Choose a route

During first-run setup, or later under **Personal Protocol**, choose one route before completing the profile.

| Route | Intended use | Separate activation boundary |
|---|---|---|
| **Local Windows speech engine** (`local_windows_tts`) | Uses a speech engine already approved and available on the Windows PC. | The user explicitly runs **Voice Studio → Test Arthur’s voice** or **Replay Arthur’s introduction**. A missing or unavailable local engine is reported; Arthur does not install one. |
| **Developer-configured neural voice provider** (`developer_neural_tts`) | Reserves a place for a developer-managed neural speech provider. | A developer must deliberately configure and approve a provider connection through API Vault before any future implementation may send approved reply text. Selecting the route makes no connection. |

## Safe activation and testing

For a local engine, open **Voice Studio**, confirm the **Spoken replies** diagnostic identifies the selected route, then press **Test Arthur’s voice**. This is a user-initiated local playback test; it is not microphone listening and does not use wake-word detection.

For a developer provider route, do not treat selection as activation. Keep the provider unconnected until its integration, privacy terms, data handling, user approval, and a dedicated connection test are all reviewed. Arthur currently provides the route description only; it does not implement provider text transmission or neural model downloads.

## Deliberate exclusions

Arthur does not provide voice cloning through this pathway. Any future voice identity feature must be separately designed with explicit, revocable consent, a clear recording boundary, and a dedicated validation flow. Microphone listening, speech recognition, wake-word readiness, and background behavior remain separate consent-gated capabilities.
