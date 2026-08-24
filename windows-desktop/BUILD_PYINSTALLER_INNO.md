# Arthur by Bogitech — Windows Build Handoff

This folder contains the **credential-free source** for Arthur’s Windows desktop prototype. Build it on a Windows 11 PC with Python 3.12, PyInstaller, and Inno Setup 6 or 7. The resulting installer is created locally; it is not included in this source archive.

## What Matches the Manus Preview

The Windows application follows the same functional model as the browser preview, while remaining a native PySide6 app rather than a pixel-for-pixel browser copy.

| Preview capability | Windows desktop equivalent |
|---|---|
| **API Vault** | Independent developer-managed provider cards with masked keys, provider websites, local saved/setup state, and an explicitly approved live test where an adapter exists. |
| **Personal Protocol** | A local profile for the preferred name, pronunciation, title, primary system language, optional languages, wake word, and required speech-recognition route. |
| **Voice language state** | The selected primary language governs typed and voice preferences; it does not turn on microphone listening. |
| **Speech-recognition route** | The profile requires a choice between local/offline recognition and a developer-configured speech-to-text provider. Selecting it alone does not install software, download a model, open the microphone, or connect a provider. |

> **Important:** Do not place an API key, a personal profile, a generated `arthur_config.json`, a `.env` file with values, or an installer-created permissions file into the source archive. Enter keys only after installation through **API Vault**. Arthur uses Windows Credential Manager when its secure storage backend is available.

## 1. Prepare Windows

Install **Python 3.12** and **Inno Setup 6 or 7**. During Python installation, enable **Add Python to PATH**. Open **PowerShell** in the extracted `arthur` folder.

## 2. Build the desktop application

The recommended one-command build is:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

The PowerShell entry point invokes the reviewed `build_windows.bat` workflow. It creates or reuses `.venv`, installs `requirements.txt`, runs the desktop regression tests, uses `Arthur.spec` to build the executable with PyInstaller, and then calls Inno Setup if it finds `ISCC.exe`.

If an earlier build stopped at `ModuleNotFoundError: No module named 'PIL'`, run the following once from the same source folder, then run the one-command build again. `Pillow` is now included in `requirements.txt`, so a newly extracted handoff installs it automatically.

```powershell
.\.venv\Scripts\python.exe -m pip install "Pillow>=10,<12"
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

If PowerShell blocks the command, use:

```powershell
cmd /c build_windows.bat
```

To build only the executable manually, use these commands from the same folder:

```powershell
py -3.12 -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python test_desktop_smoke.py
python test_packaging_handoff.py
python -m PyInstaller --noconfirm --clean Arthur.spec
```

The PyInstaller result is `dist/Arthur/Arthur.exe`.

## 3. Create the installer with Inno Setup

Open `installer/ArthurSetup.iss` in **Inno Setup Compiler** and choose **Build → Compile**. The script expects the PyInstaller payload at `../dist/Arthur/*` relative to the `installer` folder.

The resulting installer is normally written to `installer/output/ArthurSetup-0.1.7.exe`.

If Inno Setup reports “No files found matching `dist/Arthur/*`,” run the PyInstaller build first and confirm that `dist/Arthur/Arthur.exe` exists.

## 4. First launch and safe configuration

During installation, keep only the permissions you actually want. These choices are safe first-run preferences; they do not grant Windows permissions, open a microphone, start background listening, connect a provider, scan your network, or access sensors by themselves.

On first launch, complete the profile by choosing a name, primary system language, and one speech-recognition route. Open **API Vault** only after installation when you are ready to configure a provider. A saved key remains **Saved locally — not tested** until you deliberately run an approved connection test. A basic test does not send a prompt, personal data, audio, or files.

For detailed voice activation steps, read `VOICE_SETUP.md`. For provider acquisition and safe field placement, read `API_SETUP_GUIDE.md`.

## 5. Before distributing an installer

Run these checks from the source folder:

```powershell
python test_desktop_smoke.py
python test_packaging_handoff.py
```

Then install the generated installer on a separate Windows profile or test PC. Confirm that the installer asks for optional capability preferences, the profile requires language and speech-route selections, API Vault does not display embedded keys, and no listening begins until separately enabled and verified.
