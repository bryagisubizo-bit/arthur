# Arthur: Local Wake-Word Setup on Windows

Arthur keeps wake-word listening **off by default**. The local model, a selected microphone, Windows microphone permission, and an explicit enable action are all required before any listening begins.

> On Windows, openWakeWord installs the ONNX inference runtime because modern TFLite support is unavailable there. Arthur therefore accepts both `.onnx` and `.tflite` model files, while recommending `.onnx` on Windows. [1]

## Run the setup script from a source installation

Open PowerShell in the Arthur source folder and run the following commands. The script installs the local packages and downloads only the official openWakeWord example models. It does **not** start the microphone or enable background listening.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\SETUP_OPENWAKEWORD_WINDOWS.ps1
```

The script requires an existing `.venv` source environment. If you do not have one, create it first:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
.\SETUP_OPENWAKEWORD_WINDOWS.ps1
```

## Integrate the selected model in Arthur

| Step | What to do | What it does not do |
|---|---|---|
| 1 | Open **Voice studio** and choose **Choose model**. | It does not activate the microphone. |
| 2 | Select a reviewed local `.onnx` model on Windows, or a compatible `.tflite` model. | It does not verify a model’s origin automatically. |
| 3 | Choose a microphone and use **Check microphone readiness**. | It does not save audio. |
| 4 | Use **Enable local wake-word listener** and approve the prompt. | It does not grant Windows permissions automatically. |

The models downloaded by openWakeWord are **official example models**, not an Arthur model. To wake Arthur by saying “Arthur,” obtain or train a reviewed, local Arthur-specific ONNX model and select that file. Do not label an unrelated model as Arthur.

## Installed desktop application

For the installed Arthur desktop application, use the corrected installer release that bundles the local wake-word runtime. Do not copy Python packages into the installed application folder. Select the local model in **Voice studio** instead.

## References

[1]: https://github.com/dscripka/openWakeWord "openWakeWord official repository"
