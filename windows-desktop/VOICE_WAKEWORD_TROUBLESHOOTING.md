# Arthur Voice & Wake-Word Troubleshooting

## Why the earlier desktop prototype did not speak or react

The earlier Windows prototype intentionally showed a placeholder response stating that live voice providers would be connected after API configuration. It did not yet connect command acknowledgements to a text-to-speech engine, and installing `openwakeword` alone did not start a microphone listener or provide a selected wake-word model. The revised prototype adds a local Windows speech runtime and a consent-first Voice Studio diagnostic.

> **Important:** Arthur remains silent and does not listen by default. The user must separately enable local spoken replies and local wake-word listening.

## 1. Install the revised local dependencies

After extracting the revised source bundle, run this once in PowerShell from the Arthur folder:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

This includes `pyttsx3`, which uses the local Windows Speech API (SAPI) for a basic offline spoken diagnostic. It does not require a cloud speech key.

## 2. Test spoken output first

1. Start Arthur with `python app.py`.
2. Open **Voice studio**.
3. Turn on **Speak reviewed acknowledgements**.
4. Select **Test local voice**.
5. Confirm that you hear Arthur’s local test sentence.

If no sound is heard:

| Check | Windows action |
|---|---|
| Output device | Select the correct speakers/headphones from the taskbar volume control. |
| Volume | Raise Windows volume and app volume; make sure the device is not muted. |
| Windows voices | Open **Settings → Accessibility → Speech** and install or select an English voice if none is available. |
| Dependencies | Re-run `pip install -r requirements.txt` in Arthur’s activated virtual environment. |
| Diagnostic text | Read the exact status message in Voice studio; it reports whether the local speech engine is unavailable or speaking. |

## 3. Prepare a local wake-word model

`openwakeword` is the detection runtime; it needs a compatible local model file. Arthur does not treat installation as permission to listen.

1. In **Voice studio**, select the desired microphone from the diagnostic control.
2. Use the microphone diagnostic and allow Windows microphone access when requested.
3. Choose a compatible local `openWakeWord` model file in the model selector. The model path is stored locally; a model is not downloaded automatically.
4. Review the displayed model and microphone status.
5. Select **Enable local wake-word listener** only when ready.

Arthur can keep listening while hidden in the Windows system tray only after the user has explicitly enabled background readiness and the local listener. Use the tray menu’s **Pause wake-word listening** command to stop it immediately.

## 4. If Arthur does not detect the wake word

| Symptom | Likely reason | Resolution |
|---|---|---|
| Listener cannot start | No model selected or the file path is invalid. | Select a valid local model file and rerun the diagnostic. |
| “Microphone unavailable” | Windows privacy access is disabled or another application has exclusive use. | Open **Settings → Privacy & security → Microphone**, enable desktop-app access, then close competing recording apps. |
| No detections | Wrong microphone selected, input level too low, or unsupported model/phrase. | Select the active microphone, raise input level, speak normally near the microphone, and verify the chosen model’s supported phrase. |
| Detections occur but no sound | Voice output remains disabled or Windows output is muted. | Run **Test local voice** and enable spoken acknowledgements separately. |
| Arthur hides to tray but does not react | Listening is paused or was never explicitly enabled. | Restore Arthur and inspect the Voice studio status; enable the listener only after the diagnostics pass. |

## 5. Privacy and safety boundary

Arthur’s local listener only detects the chosen wake word. It does not automatically execute a command, capture credentials, scan systems, or perform background updates. A recognised wake word moves Arthur to a visible ready state; any non-read-only computer action continues to use the reviewed command plan and confirmation gate.
