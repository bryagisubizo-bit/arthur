# Arthur Desktop AI Assistant

Arthur is a Windows-first desktop assistant prototype with a voice-first design, a dark holographic-style interface, first-run profile setup, multilingual profile fields, permissions, update settings, and parallel developer API configuration cards.

## Current prototype scope

This first build is the application foundation. It includes the desktop shell, first-run setup, profile settings, explicit conduct and reviewed-memory controls, permission settings, developer integration cards, masked API-key fields, provider selection, local configuration persistence, update-channel settings, and a command-center dashboard with placeholder system metrics.

The live AI, speech, wake-word, browser research, singing, music, Home Assistant, and Windows automation adapters still need their provider credentials and implementation-specific connectors. The UI is structured so those capabilities can be added without changing the configuration flow. The current provider grid includes OpenAI, Anthropic, SerpAPI, Luxand, Seper, APIFrame, APIBox, Supabase, openWakeWord, Piped-compatible music, BhariyaMusic-compatible music, Home Assistant, updates, and a custom API/MCP hook.

## Run from source

Install Python 3.12 or newer, open a terminal in this folder, create a virtual environment, and install the dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

On first launch, Arthur asks for the user’s display name, pronunciation note, native language, additional languages, music source, wake word, and preferred title. The configuration is saved under `data/arthur_config.json`.

## Configure providers

Open **API Integrations**. Each provider card is independent and arranged in a two-column grid. A card contains a provider selector, a masked developer-key field, optional endpoint and model fields, an enable toggle, a connection-test button, and a save button.

For a production release, API keys must remain in Windows Credential Manager or a protected backend. Never commit real keys to GitHub or place them in a public installer. The current prototype intentionally contains no live credentials.

Read [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) before configuring a provider. It identifies the values each supported integration needs, where to obtain them, which values are client-safe, and which values must stay server-only. Unverified providers such as APIFrame, APIBox, Seper, and other custom APIs must be added through the custom integration form with their documented HTTPS endpoint, authentication scheme, privacy policy, and revocation path.

## Conduct, learning, and safe capability boundary

Open **Conduct & Memory** to configure Arthur’s refined delivery style, direct and calm tone, optional dry wit, preferred-title protocol, reviewed learning, suggested routines, retention period, local health monitoring, and schedule assistance. Arthur can remember approved preferences such as pronunciations, sayings, language choices, routines, and device preferences; it must ask before saving them and provide a way to edit or delete them.

Arthur does not include intrusion, credential harvesting, security bypassing, covert surveillance, weapons, combat, or unauthorized account access. Protective capabilities are limited to local system-health reporting, user-approved data analysis, approved integrations, and recommendations or actions that follow the permissions policy.

## Build the Windows executable

On Windows, double-click `build_windows.bat`. It creates a virtual environment, installs requirements, runs every bundled `test_*.py` regression, and runs PyInstaller. The standalone build is placed in `dist\Arthur\Arthur.exe`.

The current batch file does not require Python to be installed on the end user’s computer after packaging. The Linux sandbox cannot produce a Windows executable; run the batch file on Windows 11 for the real Windows build.

## Secure developer credentials

The project contains placeholders only. Real API keys must be entered locally in Arthur’s administrator API screen after you rotate any keys that were previously exposed. The key field is masked and the code attempts to store the value in the operating system credential manager through `keyring`; it is not written to `data/arthur_config.json`. The `.env.example` file is only a names-and-placeholders template. The `music_client.py` adapter is configurable and does not make requests or start playback automatically.

The Supabase service-role key and database connection string are server-only values. They must never be bundled into Arthur.exe or the ZIP file.

## Optional openWakeWord installation

On Windows, select **Install openWakeWord after approval** from Arthur’s permissions page, or run `install_openwakeword.bat` manually. The script visibly shows `pip install openwakeword sounddevice` and asks for the Windows user’s approval before it installs anything. Enable local wake-word detection only after selecting a verified model, granting microphone permission, and completing a calibration check.

When background mode is enabled, closing Arthur hides its window to the Windows system tray rather than exiting it. The listener must remain visibly controllable from the tray and should stop when the user pauses listening, signs out, selects **Exit Arthur**, or shuts down Windows. Wake-word detection is calibrated rather than guaranteed; retain a mute/pause control and avoid reporting unsupported GPU or temperature data as real measurements.

## Reviewed natural-language commands

Arthur includes a **Reviewed Commands** page. A user can speak or type an ordinary request such as “show my disk space” or “show Kali WSL memory.” Arthur maps only recognised requests to a fixed, transparent command template and shows that template before anything runs.

- **Windows diagnostics:** system information, signed-in user, local network configuration, processes, storage, and a basic internet check.
- **Local WSL/Linux diagnostics:** local system, storage, memory, network, and process information after a developer configures a trusted local WSL distribution.
- **Confirmation:** medium-risk actions, such as locking the current workstation, ask for explicit user approval.
- **Pause:** users can keep planning available while pausing all command execution.

Arthur never sends raw user or LLM-generated text to a shell. It does not support arbitrary PowerShell, Command Prompt, WSL, or Kali commands; network scans, exploitation, credential access, evasion, malware, and destructive operations are excluded. See [`FEATURE_AUDIT.md`](FEATURE_AUDIT.md) for the current capability map.

## Build the installer

Install [Inno Setup](https://jrsoftware.org/isinfo.php) before running `build_windows.bat`. The script detects Inno Setup 7 or 6 and creates `installer\output\ArthurSetup-0.1.6.exe` after the PyInstaller build succeeds. If the compiler cannot be detected, open `installer\ArthurSetup.iss` and click **Compile** instead. Do not compile the installer before `dist\Arthur\Arthur.exe` exists; the installer displays a direct recovery message if the PyInstaller payload is missing.

Before public distribution, add a code-signing certificate, replace the prototype local secret storage, and connect the selected providers through a backend or secure credential store.

## Planned next modules

The next implementation stages are the speech pipeline for English, Kinyarwanda, French, and Kiswahili; a local wake-word detector; spoken-only replies; safe Windows tools for scrolling, application control, file organization, and system health; web research; user memory; music playback; original singing; Home Assistant discovery; plugin APIs; and consent-based updates.
