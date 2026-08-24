#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m py_compile app.py api_layer.py runtime_assets.py prepare_runtime_assets.py openwakeword_service.py
python3 -m unittest -v test_api_layer test_runtime_assets test_voice_runtime test_packaging_handoff
