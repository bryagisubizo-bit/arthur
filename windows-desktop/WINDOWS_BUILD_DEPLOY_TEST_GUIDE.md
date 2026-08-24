# Arthur for Windows: Build, Distribution, and Test Guide

**Purpose.** This guide turns the existing Arthur Python/PySide6 prototype into a locally installed Windows application. The browser preview remains a design and account-management surface; it is not the Windows background service. The desktop executable must keep sensitive keys in Windows Credential Manager, execute only reviewed local adapters, and ask for consent before any action that is not read-only.

## 1. Choose the deployment route

| Goal | Recommended route | What the user receives | Approval boundary |
|---|---|---|---|
| Build the Windows desktop app | Build on a 64-bit Windows 11 development PC using the supplied `build_windows.bat` | A packaged application in the build output folder | The builder reviews output before installer creation |
| Make an installer | Run `build_windows.bat`; it invokes Inno Setup when its compiler is available | One `ArthurSetup.exe` installer | The installer must not bundle live credentials |
| Share the browser preview | Create a checkpoint, then use the project interface’s **Publish** button | A hosted preview URL | Publishing is separate from distributing the Windows executable |
| Run background assistance | Install Arthur on the user’s own Windows PC | Tray-resident local application | The user explicitly enables background readiness and local wake listening |

> **Important:** A desktop assistant does not need cloud deployment to remain in the Windows system tray. Cloud services should be optional, provider-specific backends for approved research, speech, account sync, or updates—not an unrestricted remote-control channel.

## 2. Build the installer on Windows 11

Run the build on Windows. PyInstaller bundles an application with its dependencies and is not a cross-compiler: a Windows package is built on Windows.[1] The project already includes `build_windows.bat` and `installer/ArthurSetup.iss`.

| Step | Action | Expected result |
|---|---|---|
| 1 | Copy the credential-free Arthur source bundle to a Windows 11 development machine and extract it, for example as `C:\Arthur`. | The source tree contains `app.py`, `requirements.txt`, `build_windows.bat`, and `installer\ArthurSetup.iss`. |
| 2 | Install Python 3.12 (64-bit) and Inno Setup. | Python is available from Command Prompt; Inno Setup provides the installer compiler. |
| 3 | Open **Command Prompt** in `C:\Arthur` and run `build_windows.bat`. | Arthur creates or reuses `.venv`, installs the declared dependencies, runs every `test_*.py` regression, and then PyInstaller creates `dist\Arthur\Arthur.exe`. |
| 4 | If Inno Setup 7 or 6 is installed, wait for the script to invoke `ISCC.exe` automatically. If it is not found, open `installer\ArthurSetup.iss` in Inno Setup Compiler and select **Build → Compile**. | Inno Setup creates `installer\output\ArthurSetup-0.1.6.exe`. |
| 5 | Install only on a disposable test environment first. | The installer creates Start Menu and optional desktop shortcuts without carrying a developer secret. |

Inno Setup supports 64-bit Windows applications, produces a single installation executable, and supports uninstall and code-signing workflows.[2] Before distribution, code-sign the final installer if you have a code-signing certificate; the signed installer should be the artifact given to users.

> **Required build order:** do not compile `installer\ArthurSetup.iss` until PyInstaller has created `dist\Arthur\Arthur.exe`. The installer script now stops early with a direct recovery message when this file is missing; run `build_windows.bat` from the Arthur project folder and compile again.

### Installer permission review

Before Arthur is copied to Windows, the installer shows **Arthur permissions review**. It offers separate, optional choices for local wake listening, local camera features, background readiness, smart-home connections, provider/API setup, and local system sensor diagnostics. Leaving every option unchecked installs Arthur with its safest local defaults.

These choices are recorded only as first-run Arthur preferences in a local file. They do **not** grant Windows microphone, camera, notification, network, Windows Hello, smart-home, or background-execution permission. Arthur still shows a separate in-app explanation and Windows shows its own system prompt or privacy setting when a feature first needs access. A user can decline an installer choice and enable a capability later, or accept a choice and still deny the later Windows permission.

### Local system sensors

Arthur’s **System sensors** workspace is disabled by default unless the installer user chose local diagnostics. When enabled, the user can manually refresh transient CPU, memory, system-drive, battery, and network-adapter readings. Arthur does not retain a history, upload readings, install a monitoring program, or read sensors while this workspace is closed.

Windows may expose one or more ACPI thermal zones; Arthur shows a temperature only when Windows returns one. A missing temperature is not an error and does not imply the PC lacks a sensor. CPU and GPU telemetry generally requires a compatible local adapter; Arthur reports this as unavailable and never installs or launches such an adapter without a separate user-approved integration.

### Limited-internet setup commands

For a first development run, open PowerShell in the extracted Arthur folder and use the following once:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

After that, the normal development launch uses only the existing virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

To reduce repeat downloads, retain the `.venv` folder while working on the same extracted source folder. Run `pip install -r requirements.txt` again only when the source bundle changes, `requirements.txt` changes, or Python reports a missing module.

## 3. First-run tutorial and manual GitHub release checks

On its first successful launch, Arthur asks for the preferred name, pronunciation, native language, additional languages, music source, wake word, and preferred title. It then presents a short tutorial covering the Command desk, permission and listening choices, the developer-managed API Vault, manual updates, and personal controls. When **Voice first** replies and **Introduce Arthur after first-run setup** are enabled, Arthur follows this with one brief local introduction using the selected name or title. The same tutorial is available later from **Updates → Show first-run tutorial**.

In **Voice studio**, users may separately enable or silence three optional local speech cues: the first-interaction introduction, a concise greeting when Arthur opens or is restored from the tray, and a concise acknowledgement of a deliberately detected local wake word. The **Replay Arthur’s introduction** control is always a direct user action. None of these controls opens a microphone, starts background listening, or contacts a provider; disabling **Voice first** keeps the cues visual rather than spoken.

### Microphone and local wake-word readiness

Arthur does not start listening merely because it has been installed. In **Voice studio**, select the intended microphone, use **Check microphone activity**, and choose **Open Windows microphone privacy** if Windows reports access is blocked. In Windows Settings, allow microphone access, allow desktop apps to access the microphone, and verify that Arthur is permitted. Return to Arthur, select the same input device, and run the readiness check again. The check observes a short local level only; it does not save, transcribe, upload, or retain audio.

After the readiness result is clear, choose **Enable local wake listening** and accept the visible consent request. Arthur then starts the selected-device openWakeWord listener only. If a required local dependency or wake model is unavailable, Arthur reports that exact local prerequisite rather than claiming to listen. You may install or repair it deliberately in the project virtual environment with `pip install openwakeword`; Arthur never runs that installation or enables background listening silently. A detected wake word opens Arthur’s command state; command transcription remains a separate, explicitly configured speech-recognition capability.

Arthur’s native Windows prototype follows the same Orbital Command Atelier identity and now uses the requested **hawk on a blue background** as its window, tray, packaged executable, and installer icon. It is a PySide6 desktop interface rather than a web browser, so its layout is deliberately aligned with the preview rather than being a pixel-for-pixel copy of the React preview.

### API Vault websites and connection states

Each API Vault card now includes a labelled official provider website when one is available. Opening a website is only a user-directed way to obtain setup information or an API key; it does not add a key, create an account, test a provider, or establish a live connection. A resource remains **unconnected** until the developer deliberately saves it in the local credential store and completes the applicable approval and safe test path.

For a provider card, **Not connected** means no usable configuration has been saved; **Key required** means the selected remote provider needs a developer key; **Saved locally — not tested** means its settings were stored through Windows Credential Manager but Arthur has made no network request; and **Adapter ready — not tested** means Arthur has an approved test adapter but has still made no request. Only **Last approved test passed** means the developer explicitly approved one narrowly scoped HTTPS test and the provider returned success. A failed or unavailable test never counts as a connection.

For OpenAI, choose **Check saved setup** to inspect local state without networking, then select **Run approved live test** only when you want to send one request to OpenAI’s documented `GET /v1/models` endpoint. Arthur displays a confirmation first, sends no prompt, audio, file, or personal data, and does not run this test automatically. Other providers remain local-only until their own approved test adapter is implemented.

The **Language library** is a bundled local catalogue for discovering language names, ISO codes, native labels, and writing systems. English, Kinyarwanda, French, and Kiswahili remain Arthur’s profile-ready defaults. Other catalogue entries may be selected as a local conversation preference or added to favourites, but they require a separately approved local language pack or connected provider before Arthur attempts speech recognition, synthesis, translation, or research in them. Selecting a language never downloads a pack, opens the microphone, translates text, or sends a request.

Use **Prepare multilingual search** to keep a question exactly as written in the selected language and review whether an approved research or language provider is required. Arthur does not submit, translate, save, or send the query from this step. The user may copy the prepared text or explicitly approve a relevant provider workflow later.

The **Language library** also includes **Diné Bizaad (Navajo)** (`nv`) under its endonym with a community-governance/review state. It does not label Diné Bizaad extinct, infer proficiency, bundle vocabulary, or imply that speech, translation, or search support exists. Selected under-resourced and revitalisation-focused languages use qualified context such as “authoritative community source required,” not a broad technical or cultural claim. Source notes are recorded in `LANGUAGE_COMMUNITY_SOURCES.md`.

Arthur does not bundle “slang” for any language. The **Community context / private drafts** control may store a user-supplied local draft only after they provide the expression, regional context, and source or community-review note. Every such draft is visibly **not community reviewed** and is not copied to a provider, translated, searched, spoken, or used in replies automatically. Add a verified entry only with permission and a suitable community-approved source.

For an all-language identifier catalogue, use **Choose local ISO 639-3 table** and select a copy of the official standard table that you have obtained yourself. Arthur stages the identifiers only in its current local session; it does not upload, redistribute, install packs for, or claim speech/translation support for any imported code. A **Prepare review preview** remains local and cannot publish an entry. It requires a language, regional context, expression, plain meaning, source/community attribution, and a sensitivity or usage note before Arthur will show an explicitly unverified preview. The identifier and source boundaries are recorded in `LANGUAGE_CATALOGUE_STANDARD_SOURCES.md`.

For selected endangered, under-resourced, or revitalisation-focused languages, Arthur may display a **Source-confirmed — not community-reviewed** example. Every such record keeps the cited language or dialect label, region, intended use, sensitivity note, named evidence source, and HTTPS link together. This status means that a human checked the listed source; it does **not** mean that every community endorses the wording, that Arthur can publish it, or that the expression may be spoken, translated, searched, learned, or used in replies automatically. To prepare a local source-confirmed preview for a new expression, a reviewer must provide the language, expression, meaning, region or dialect, use context, sensitivity note, an approved evidence-source category, a named source, HTTPS evidence URL, and an explicit attestation. The evidence policy and currently cited resources are recorded in `LANGUAGE_ENDANGERED_EXPRESSION_VERIFICATION_SOURCES.md`.

Arthur uses **manual update checks only**. It does not poll GitHub in the background, retry automatically, pull source code from a branch, or accept an update silently. A user may choose one listed release asset only after a metadata check, approve its download, and then make a separate decision about handing the verified installer to Windows. This protects limited data plans and ensures that every network and update step is visible to the user.

| User action | What Arthur may do | What Arthur will not do |
|---|---|---|
| Enter `owner/repository` and select **Save update source** | Store the release source locally; optionally store a user-provided scoped private-repository token in Windows Credential Manager. | Contact GitHub or download any update. |
| Select **Check GitHub Releases now** and confirm the one-time request | Read GitHub’s small latest-release metadata response and display version, publication date, asset names, sizes, and whether GitHub supplied a SHA-256 digest. | Download an asset, run an installer, schedule a retry, or check in the background. |
| Select one release asset and choose **Approve selected download** | Download only that user-selected HTTPS asset and verify its SHA-256 digest when GitHub provides one. A missing digest or mismatch blocks the release; a mismatched local file is deleted. | Launch or install the asset. |
| Review the verified local installer | Make a second, independent choice to ask Windows to open an existing `.exe` or `.msi` installer. The installer retains its own elevation and prompts. | Accept an update silently, elevate a process, or complete installer prompts on the user’s behalf. |

The built-in default source is `bryagisubizo-bit/arthur`. Release `v0.1.0` is available as the first verified installer release. Arthur reads new versioned releases manually, and accepts only an asset that GitHub reports with a `sha256:` digest before presenting the separate Windows installer handoff.[5]

## 4. Test locally before release

The first pass should be a no-credential, no-background, no-provider test. The second pass adds one provider at a time, using a non-production project or key where the provider offers one.

| Test area | Procedure | Pass condition |
|---|---|---|
| First run | Install Arthur, select language, name, pronunciation, and title. | Preferences can be changed later; no API key is shown in the UI. |
| Background consent | Decline background readiness, close the window, and confirm Arthur is not listening. Then accept it and confirm the tray state, pause button, and Exit action. | Background listening is never enabled merely by installation. |
| Natural wording | Ask three equivalent requests, such as “make it quieter,” “lower the sound,” and “reduce volume.” | Arthur routes them to the same reviewed capability and shows the plan before any change. |
| Reply language | Say “speak in Kinyarwanda,” “parle en français,” or the equivalent supported request. | Arthur updates the local reply-language preference and confirms it; it does not claim it can translate every possible device command offline. |
| Language library | Open **Language library**, search by a language name, ISO code, native label, or writing system, select a catalogue entry, and mark it as a favourite. | The choice remains local, the existing four profile-ready languages remain available, and no pack download, microphone activation, translation, or provider request occurs. |
| Local all-language identifiers | In **Language library**, choose a local ISO 639-3 table and then search an imported identifier. | Arthur stages the selected table locally for discovery only; it does not upload the table, redistribute it, install a pack, or claim language capability. |
| Colloquial review preview | Enter a language, regional context, expression, meaning, source/community attribution, and sensitivity note, then choose **Prepare review preview**. | Arthur shows an explicitly unverified local preview only; it does not publish, translate, speak, search, or send the entry. |
| Source-confirmed evidence preview | Select a language with a source-confirmed example, inspect its retained region or dialect, use context, sensitivity note, and HTTPS citation. Then prepare a new preview with all evidence fields and reviewer attestation; repeat with an `http://` URL and with attestation cleared. | Existing examples remain explicitly **not community-reviewed**. A new preview remains local and cannot grant community review, publishing permission, or automatic use; missing attestation and non-HTTPS evidence are rejected. |
| Multilingual query review | Enter a question in the selected language and choose **Prepare multilingual search**. | Arthur preserves the question exactly as written, identifies any missing local pack or approved provider, and does not perform a web search or transmit text. |
| Local app route | Request “open camera” or “open WhatsApp,” then decline and accept the confirmation. | Arthur shows a fixed Windows URI route and launches it only after approval; no generated shell text is used. |
| WhatsApp draft | Ask Arthur to text someone on WhatsApp, including “open WhatsApp and text someone.” | Arthur opens a recipient-and-message draft review; it never selects a contact, types into WhatsApp, or sends a message. |
| Safety | Try a blocked security or raw-shell request. | Arthur refuses; it does not construct or execute generated shell text. |
| Visual output | Set visual results to “ask before showing,” then request a chart or screen result. | Arthur asks before displaying it. |
| Provider room | Leave a required provider unconfigured and issue a matching request. | Arthur identifies the exact missing room and does not call a fallback silently. |
| Update control | In **Updates**, choose **Check GitHub Releases now**, then test the selected-asset download and installer-handoff questions with a disposable signed release. | Arthur performs no background check. It downloads only after the first approval, rejects absent or mismatched SHA-256 digest records, and asks separately before Windows opens the verified installer. |
| Live-preview parity | Visit Command desk, Tools & routing, **Spatial workspace**, Voice studio, Private notes, Autonomy & change, and API vault. | The Windows shell uses the same Orbital Command Atelier workspace model, while clearly labelling Windows-only or provider-dependent states. |
| Defensive lookup gate | Open API vault, leave defensive lookup disabled, then enable it and inspect the boundary text. | The gate remains off by default and permits only a separately approved passive enrichment request; scanning, exploitation, credential testing, malware handling, and automatic actions remain unavailable. |
| Local voice diagnostic | In **Voice studio**, enable spoken acknowledgements and select **Test local voice**. | Arthur reports whether the local Windows speech engine is available; the test does not require a cloud provider. |
| Local microphone activity | In **Voice studio**, select **Test microphone activity (3 sec)** and approve the single test dialog. Speak or make a brief sound while it runs; repeat after muting the input or denying Windows microphone permission. | Arthur reports only whether it observed a transient local input level. The test stores no recording, transcript, or audio data, sends nothing to a provider, and does not enable wake-word or background listening. |
| Greeting controls | Complete first-run setup, restore Arthur from the tray, and use **Replay Arthur’s introduction**. Then disable **Voice first** and repeat. | Each enabled cue uses the selected local Windows voice and the configured name/title. With Voice first disabled, Arthur does not speak; no cue starts listening or opens a microphone. |
| Wake-word diagnostic | Select a microphone and a compatible local wake-word model, then explicitly enable the listener. | Arthur does not listen until the selected model, microphone access, and user approval are all present. With a valid installed model, it opens the **Voice signal** workspace on detection; the tray **Pause** action stops it immediately. |
| Voice signal | Enable local listening, then initiate a command or say the configured wake word. | The local animated orb opens for the command session and reacts only to transient input level; it does not retain or upload audio. |
| Personalisation | Leave the local sample permissions disabled, then enable and save each permission before choosing one test photo or own-voice file. | Arthur never opens a camera or microphone automatically. It copies only the selected local file, does not upload it, and requires a separate proposal before any developer-configured voice-cloning service can be considered. |
| Smart home | In **API vault**, select Home Assistant, Philips Hue, SmartThings, Tuya, MQTT, or another local hub. | Arthur only records connection configuration and a review preference; it does not scan the network, discover devices, or control devices automatically. |
| Touch workspace | Open **Spatial workspace** on a touch display. Swipe across the card field, drag one card to a new position, alter the in-app scale, then choose **Discard selected** and test **Undo discard**. | Gestures affect Arthur’s own card layout only. Discard always asks first and is reversible during the session; Arthur does not move the Windows pointer or control another app. |
| Local air gesture | Leave the consent checkbox off, then try **Enable local air gestures**. Next, install the optional local adapter, accept the consent dialog, and stop it from the page, tray, and Exit action. | No camera opens without both consent acknowledgements. While active, the interface shows a local-camera status, processes hand landmarks only in memory, retains no video or templates, and stops capture on pause, close, or exit. |
| Protected Spatial room | Say “Arthur, open the Spatial room,” choose password-only, Windows-Hello-only, or experimental local-camera face access, then test cancellation, the selected verification method, its failure path, recovery path, deletion path, and **Lock room now**. | Arthur asks to proceed, then requires the selected local access method. It enables no workspace controls until successful verification; lock immediately stops local air gestures. A local camera opens only for separately approved experimental face enrolment or verification. |
| Symptom support | Enter ordinary symptoms, an urgent description, and a possible emergency warning sign in **Symptom support**. | Arthur calls the content guidance rather than a diagnosis, directs urgent and emergency descriptions to professional help, and does not save the text unless the user independently chooses a permitted local note action. |

## 5. Voice and wake-word setup

The initial desktop prototype showed a voice placeholder, so installing `openwakeword` by itself could not make Arthur speak, detect a phrase, or interpret a command. The revised source bundle adds a local spoken-response diagnostic through Windows Speech and a guided Voice studio configuration flow.

1. After extracting the revised source, reactivate the virtual environment and run `pip install -r requirements.txt` so the local speech dependency is installed.
2. Open **Voice studio** and select **Test local voice** or **Replay Arthur’s introduction** before working on the wake word. This is the safe speaker test: it speaks a short local line through the selected Windows voice and does not open the microphone. Fix Windows speaker, voice, or package issues before continuing. Choose the first-interaction, arrival, and wake acknowledgements you want; all are optional and can be silenced later.
3. If you want to confirm that Windows is receiving sound, select **Test microphone activity (3 sec)** and approve the one-time prompt. Speak briefly during the three-second window. Arthur measures only a transient level, immediately discards it, and cannot transcribe or understand your words during this diagnostic. This test neither saves audio nor starts wake-word or background listening.
4. In **Local greeting wording & quiet hours**, choose an opening, first-interaction, or wake greeting to edit. The script is local plaintext, limited to 240 characters, and supports only `{recipient}` and `{time_of_day}`. Use **Restore selected safe default** if the wording needs to be reset.
5. Enable **time-of-day wording** only if wanted. Arthur chooses morning, afternoon, or evening wording only when it is already opened or the user deliberately wakes it; it does not set a timer, start a scheduler, wake the PC, or initiate speech by itself.
6. To suppress non-essential greetings, enable **Do Not Disturb** and select a local start and end time. The status line explains whether the schedule is active. An explicit user replay remains available, while automatic opening, first-interaction, and wake acknowledgements stay silent during active quiet hours.
7. Select the correct microphone and allow desktop microphone access in Windows Privacy settings.
8. Select a compatible **local** openWakeWord model. Installing the Python package alone is insufficient: the listener requires a compatible `.tflite` model file for the configured wake word. Arthur does not download a model or begin listening automatically.
9. Review the model and microphone status, then explicitly select **Enable local wake-word listener**. Once all three prerequisites are present—model, microphone permission, and explicit enablement—the local listener begins immediately and opens **Voice signal** when it detects the wake word.
10. Use the tray menu’s **Pause local listeners** item to stop local listening and any active local air gestures immediately; exit also stops both listeners.

See `VOICE_WAKEWORD_TROUBLESHOOTING.md` for symptom-by-symptom Windows troubleshooting and the privacy boundary.

## 6. Optional local air-gesture setup

Touch controls require no extra package: they operate in Arthur’s own **Spatial workspace** through Windows touch, drag, swipe, and standard mouse/trackpad input. Camera-based air gestures are deliberately optional because they need a visible, user-approved local camera session.

1. First verify ordinary touch controls work. Do not install gesture packages merely for the visual effect.
2. If the user wants the optional local adapter, reactivate the project environment and run:

```powershell
pip install -r requirements-gesture-optional.txt
```

3. In Windows **Settings → Privacy & security → Camera**, allow desktop camera access only if the user is ready to use the feature.
4. In **Spatial workspace**, select the intended camera index, check the consent acknowledgement, and approve the second confirmation dialog. Arthur will show that the local camera is active.
5. The prototype recognises a limited set of **Arthur-workspace-only** gestures: sideways hand movement selects a neighbouring card, pinch changes canvas scale, and an open palm asks before removing the selected card. It does not identify people, store recordings, retain landmarks, send video to a provider, inject pointer input, or execute a PC action.
6. Use **Stop local air gestures**, the tray **Pause local listeners** action, closing the window, or **Exit Arthur** to stop capture. Removing the optional packages disables the adapter entirely.

> **Do not use air gestures as a safety-critical input.** Windows touch and visible buttons remain the reliable way to approve, discard, or arrange work. Any later automation or PC action continues to require its own reviewed confirmation.

## 7. Protected Spatial room and optional Windows Hello

The **Spatial workspace** is a protected local room. A user can request it from the Command desk by voice or text with phrases such as **“Arthur, open the Spatial room”** or **“open Spatial workspace.”** Arthur first asks whether to continue, then requires local access verification before it exposes touch cards, in-app scale controls, discard/undo controls, or camera-based gesture controls.

1. In **Spatial workspace**, choose **Choose room access method**. The user must deliberately select **one** method: **Use local password only**, **Use Windows Hello only**, or **Use experimental local camera face access**. Arthur does not activate a face check until the user selects a face-based method and then starts its visible setup or verification flow.
2. For password-only access, choose and confirm a password of at least 10 characters. Arthur stores only a salted verifier in Windows Credential Manager; it does not put the plaintext password in `arthur_config.json`, source control, or an audit log.
3. For Windows-Hello-only access, configure face or PIN in **Windows Settings → Accounts → Sign-in options** first. Arthur can select Windows Hello only when its optional OS adapter is installed and Windows reports the feature available. Selecting it removes an existing unused Arthur room-password verifier after a clear confirmation.
4. For Windows-Hello-only access, Arthur does **not** operate its own face scanner. It neither captures an enrolment image nor stores, compares, uploads, or receives Windows Hello face templates. Windows Hello performs face/PIN verification at the operating-system layer; Arthur receives only a local success or failure result.
5. If the Windows Hello adapter is wanted, the user may manually review and run the optional command from the Arthur source folder:

```powershell
pip install -r requirements-hello-optional.txt
```

> **Access boundary:** A Windows-Hello-only room requires Windows Hello. If it is unavailable, cancelled, fails, or is removed, Arthur keeps the room locked and explains how to restore Windows Hello or change the access method after authorised access. It does not silently fall back to a password. There is no voice-only, Arthur-camera-only, or hidden bypass for this protected room.

### Experimental local-camera face access when Windows Hello is unavailable

The local-camera option is a separate, explicitly selected method for a user whose PC camera works but whose Windows Hello face feature is unavailable. It is an **experimental local access convenience**, not a replacement for Windows Hello, Windows sign-in, a hardware security key, or an administrator account.

1. Review the limitation above. If a stronger access-control mechanism is available, prefer it.
2. Manually install the optional local adapter from the Arthur source folder. Arthur never runs this command itself:

```powershell
pip install -r requirements-face-access-optional.txt
```

3. In **Windows Settings → Privacy & security → Camera**, permit desktop camera access only when ready to enrol.
4. Before enrolment, select **Run visible local camera readiness test** if you want to confirm the selected camera, shutter, and Windows permission. Arthur asks again before it opens the camera, places a camera-active label over the short preview, and lets you cancel with `Esc` or `Q`. The test creates no enrolment and keeps no image, video, model, failed frame, or log.
5. Select **Use experimental local camera face access**, then select **Enroll local face access**. Arthur displays a visible local camera preview and consent notice before capture begins. Cancel to stop immediately.
6. If useful for accessibility, enable **Play a local system tone for camera activation and verification results**. It is off by default. The tone is local, does not start listening, does not speak biometric information, and can be muted at any time.
7. Enter and confirm a recovery secret. It is needed to erase the local face-access material or change the room’s access method if the camera check is unavailable or repeatedly fails.
8. Arthur uses the approved camera session only to create an encrypted local face signature. It does not upload the signature, retain raw frames, retain a video recording, or send the camera feed to a provider. Use **Delete local face access** to delete the encrypted signature and recovery verifier.

> **Face-access boundary:** The experimental local camera check runs only after the user explicitly selects this method and begins enrolment or unlock verification. Camera activity must be visibly indicated. A failed, cancelled, unavailable, or low-confidence check keeps the Spatial room locked; it does not downgrade automatically to a different access method. After three completed local face non-matches, Arthur applies a 60-second local cooldown and shows the remaining time. It stores only the short counter/timer, never a failed frame; cancellation, missing camera permission, and unavailable hardware do not count as non-matches. The recovery secret can remove or replace the method, not reveal protected workspace content. This prototype does not claim the spoof resistance, liveness detection, device binding, or security guarantees of Windows Hello.

## 8. Symptom support is not disease diagnosis

Arthur can help a user organise symptoms, state that a clinician may be appropriate, and surface simple warning-sign escalation language. It cannot determine a disease, rule out a serious condition, prescribe a treatment, assess severity remotely, or replace emergency or professional care.

The Symptom support page is private by default: the typed description remains in the live page only and is cleared by the user. For any severe, sudden, or rapidly worsening symptom—or for chest pain, difficulty breathing, stroke-like signs, severe allergic reaction, loss of consciousness, severe bleeding, or immediate danger—the page tells the user to contact local emergency services rather than wait for app analysis. The optional **Speak guidance locally** button reads the same cautious care-seeking text; it does not provide a diagnosis.

## 9. Virtual testing without risking the main PC

**Windows Sandbox** is the quickest clean test for a Windows Pro, Enterprise, or Education machine. It is a disposable isolated desktop: closing it discards installed software, files, and state. Microsoft notes that it is not supported on Windows Home and that networking is enabled by default, so use networking only when a tested provider flow genuinely requires it.[3]

1. Enable **Windows Sandbox** in “Turn Windows features on or off.”
2. Copy only the installer into a temporary shared folder. Do not map a folder containing developer credential files.
3. Start Sandbox with networking disabled for installer, wake-word, and local safety tests; enable networking only for one approved provider test.
4. Install Arthur, run the test matrix above, and close Sandbox to discard the test state.

For broader compatibility testing, use **Hyper-V** and a separate Windows 11 virtual machine. Microsoft states that client Hyper-V requires Windows 10/11 Pro or Enterprise, a 64-bit processor with SLAT and VM Monitor Mode Extension, and at least 4 GB of memory.[4] Arthur’s target machine has 8 GB RAM, so a VM is best run on a more capable development computer; running both host and Windows 11 guest on the target hardware may be slow.

## 10. What “Arthur changes itself” may safely mean

Arthur may understand a request such as “use larger writing” or “make the notes screen calmer.” It may immediately apply reversible user preferences only after showing the intended setting. For software changes, it must create a **proposal**, not a silent modification.

| Stage | Allowed behaviour | Not allowed |
|---|---|---|
| Interpret | Identify the requested outcome and affected feature area. | Assume unrestricted control of source code or cloud accounts. |
| Plan | Select an approved development room, prepare a scoped change, tests, and rollback point. | Contact a provider with private code or credentials without authorization. |
| Review | Show the diff or implementation plan and obtain approval. | Apply or publish automatically. |
| Implement | Run in the connected developer workspace after approval, then test and checkpoint. | Replace the installed Windows executable while it is running. |
| Update | Offer a signed installer update for user approval. | Download or install an update silently. |

## References

[1]: https://pyinstaller.org/en/stable/ "PyInstaller Manual"
[2]: https://jrsoftware.org/isinfo.php "Inno Setup"
[3]: https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/ "Windows Sandbox"
[4]: https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v "Install Hyper-V in Windows and Windows Server"
[5]: https://docs.github.com/en/rest/releases/releases "GitHub REST API: Releases"
