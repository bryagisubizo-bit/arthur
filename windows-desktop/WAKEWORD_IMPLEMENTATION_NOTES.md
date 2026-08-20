# Arthur Wake-Word Implementation Notes

## Verified local model boundary

Arthur’s desktop listener must remain **opt-in**, local, and visibly indicated. Installing the Python package alone does not create a model for the custom keyword “Arthur.” The listener therefore needs either a selected compatible model file or a deliberately installed approved model before it can start.

The official openWakeWord documentation describes one-time retrieval of supported pre-trained models through `openwakeword.utils.download_models()` and direct model selection through `Model(wakeword_models=["path/to/model.tflite"])`. It also advises that recognition thresholds are environment-specific and should be calibrated through local testing. The project documentation states that Windows installs use ONNX Runtime because current TensorFlow Lite Runtime support is unavailable there; Arthur must therefore not represent `.tflite` as the only supported Windows asset format.

Arthur will preserve the following controls: explicit local-listening approval, an obvious visual listening state, a tray pause command, a cooldown to avoid repeated detections, and no recording or cloud transmission of microphone audio. A custom “Arthur” model remains a separate local asset/training task, not an automatic consequence of installing the package.

## Source

[1] [openWakeWord documentation and reference implementation](https://github.com/dscripka/openWakeWord)
