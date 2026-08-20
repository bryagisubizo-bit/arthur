# Arthur Voice Setup

Arthur supports **typed commands immediately** after you complete the required profile setup. Spoken-command understanding requires separate, deliberate setup.

## Required first-run choices

During first run, choose a **primary system language** and one **speech-recognition route**:

| Route | What you must complete afterwards | What Arthur does not do automatically |
|---|---|---|
| **Local / offline speech recognition** | Approve installation of a local speech-recognition engine and download the language models you select. Verify the model in Voice Studio. | It does not install an engine, download models, turn on the microphone, or retain audio merely because you select this route. |
| **Developer-configured speech-to-text provider** | The developer must add and test an approved provider connection in the API Vault. Then verify the route in Voice Studio. | It does not connect a provider, send audio, or use a stored key merely because you select this route. |

## Enabling spoken commands

After selecting the route, open **Voice Studio** and complete these independent steps:

1. Choose the intended microphone and use **Check microphone readiness**.
2. If you want wake-word activation, choose an approved local wake-word model and use **Check wake-word readiness**.
3. Explicitly approve and start the local listener.
4. Ensure the selected speech-recognition route is actually ready. Wake-word detection by itself acknowledges “Arthur”; it does **not** transcribe the command that follows.

> Arthur should only interpret a spoken command after the selected recognition route is ready and you have approved microphone listening. The app never silently enables background listening, engine/model installation, or provider connection.

