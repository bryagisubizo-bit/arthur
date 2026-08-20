import json
import os
from datetime import datetime
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, Qt, QTime, QTimer, Signal, QUrl

from secure_store import get_secret, set_secret
from command_planner import CommandPlanner, RiskLevel, language_switch_target
from github_update import download_release_asset, fetch_latest_release, handoff_verified_installer, validate_repository
from gesture_runtime import GestureEvent, GestureListener, optional_dependency_status
from health_support import prepare_symptom_guidance
from health_information import find_condition_reference, summarise_article_excerpt
from language_library import (
    create_colloquial_draft,
    find_language,
    merged_catalogue,
    normalise_favourites,
    parse_iso6393_table,
    prepare_colloquial_entry_review,
    prepare_source_confirmed_expression,
    prepare_search_query,
    restore_imported_catalogue,
    search_languages,
    serialise_imported_catalogue,
    source_confirmed_expressions,
)
from openwakeword_service import WakeWordListener
from face_access import (
    camera_acceptance_test,
    clear_face_failures,
    delete_enrollment as delete_face_enrollment,
    enroll as enroll_face,
    face_lockout_status,
    has_enrollment as face_is_configured,
    optional_dependency_status as face_dependency_status,
    register_face_failure,
    set_recovery_secret as set_face_recovery_secret,
    verify as verify_face,
    verify_recovery_secret as verify_face_recovery_secret,
)
from spatial_access import clear_password as clear_spatial_password, has_password as spatial_password_is_configured, set_password as set_spatial_password, verify_password as verify_spatial_password
from voice_runtime import VoiceRuntime, available_input_devices, diagnose_wake_word, microphone_readiness, test_microphone_activity
from windows_hello import availability as windows_hello_availability, verify as verify_windows_hello
from provider_connection import run_approved_connection_test, setup_state
from installer_consent import apply_installer_defaults, load_installer_consent
from system_sensors import collect_snapshot
from PySide6.QtGui import QAction, QDesktopServices, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QAbstractItemView,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSwipeGesture,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "Arthur"
APP_PUBLISHER = "Bogitech"
BASE_DIR = Path(__file__).resolve().parent
# An installed application cannot rely on write access to Program Files.  Keep
# user settings and the installer consent record in the current user's AppData.
DATA_DIR = (
    Path(os.getenv("APPDATA", str(Path.home()))) / APP_NAME
    if getattr(sys, "frozen", False)
    else BASE_DIR / "data"
)
CONFIG_FILE = DATA_DIR / "arthur_config.json"
INSTALLER_CONSENT_FILE = DATA_DIR / "installer_permissions.json"


def bundled_path(relative_path: str) -> Path:
    """Resolve an asset from source or from PyInstaller's temporary bundle."""
    return Path(getattr(sys, "_MEIPASS", BASE_DIR)) / relative_path

LANGUAGES = ["English", "Kinyarwanda", "French", "Kiswahili"]
PRIMARY_SYSTEM_LANGUAGE_PLACEHOLDER = "Choose your primary system language"
SPEECH_RECOGNITION_ROUTE_PLACEHOLDER = "Choose how Arthur should recognise spoken commands"
SPEECH_RECOGNITION_ROUTES = {
    "local_offline": {
        "label": "Local / offline speech recognition",
        "detail": "Requires separate approval to install a local recognition engine and download language models. The approved engine can process audio on this PC.",
    },
    "developer_provider": {
        "label": "Developer-configured speech-to-text provider",
        "detail": "Requires an approved developer-managed provider connection and separate microphone/listening consent. Arthur does not send audio until those steps are complete.",
    },
}


def profile_language_choices():
    """Return all bundled local language labels for an explicit profile choice."""
    return tuple(entry.name for entry in merged_catalogue())


def configure_primary_language_combo(combo, selected=""):
    """Populate a profile selector with a non-language placeholder and local catalogue entries."""
    combo.clear()
    combo.addItem(PRIMARY_SYSTEM_LANGUAGE_PLACEHOLDER, "")
    for language in profile_language_choices():
        combo.addItem(language, language)
    selected_index = combo.findData(str(selected or "").strip())
    combo.setCurrentIndex(selected_index if selected_index >= 0 else 0)


def selected_primary_language(combo):
    """Read a deliberate primary-language selection instead of accepting a display placeholder."""
    return str(combo.currentData() or "").strip()


def configure_speech_recognition_route_combo(combo, selected=""):
    """Populate the required first-run route selector without installing or connecting anything."""
    combo.clear()
    combo.addItem(SPEECH_RECOGNITION_ROUTE_PLACEHOLDER, "")
    for route_id, route in SPEECH_RECOGNITION_ROUTES.items():
        combo.addItem(route["label"], route_id)
    selected_index = combo.findData(str(selected or "").strip())
    combo.setCurrentIndex(selected_index if selected_index >= 0 else 0)


def selected_speech_recognition_route(combo):
    """Return only a deliberately selected supported recognition route."""
    route_id = str(combo.currentData() or "").strip()
    return route_id if route_id in SPEECH_RECOGNITION_ROUTES else ""

DEFAULT_GREETING_SCRIPTS = {
    "introduction": "Good {time_of_day}, {recipient}. I am Arthur, your local desktop assistant. I am ready when you are.",
    "opening": "Good {time_of_day}, {recipient}. Arthur is ready when you are.",
    "wake": "Yes, {recipient}. Arthur is ready.",
}


def greeting_period(hour=None):
    """Return a concise local day-part without making an online request."""
    selected_hour = datetime.now().hour if hour is None else int(hour)
    if selected_hour < 12:
        return "morning"
    if selected_hour < 18:
        return "afternoon"
    return "evening"


def _parse_clock(value, fallback):
    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except (TypeError, ValueError):
        return fallback


def is_time_in_window(current, start, end):
    """Check a local, inclusive-start/exclusive-end window, including overnight windows."""
    now_value = _parse_clock(current, datetime.now().time()) if isinstance(current, str) else current
    start_value = _parse_clock(start, datetime.strptime("22:00", "%H:%M").time())
    end_value = _parse_clock(end, datetime.strptime("07:00", "%H:%M").time())
    if start_value == end_value:
        return False
    if start_value < end_value:
        return start_value <= now_value < end_value
    return now_value >= start_value or now_value < end_value


def greeting_is_quiet(config, now=None):
    voice = config.get("voice", {})
    if not voice.get("do_not_disturb_enabled", False):
        return False
    moment = now or datetime.now()
    current = moment.strftime("%H:%M") if hasattr(moment, "strftime") else str(moment)
    return is_time_in_window(current, voice.get("do_not_disturb_start", "22:00"), voice.get("do_not_disturb_end", "07:00"))


def render_greeting_script(config, kind, now=None):
    """Expand only Arthur's documented local tokens; scripts cannot execute code or commands."""
    profile = config.get("profile", {})
    voice = config.get("voice", {})
    scripts = voice.get("greeting_scripts", {})
    default = DEFAULT_GREETING_SCRIPTS.get(kind, DEFAULT_GREETING_SCRIPTS["opening"])
    template = str(scripts.get(kind, default)).strip()[:240] or default
    title = str(profile.get("title", "Sir")).strip() or "Sir"
    name = str(profile.get("display_name", "")).strip()
    recipient = f"{title} {name}".strip() if name else title
    moment = now or datetime.now()
    period = greeting_period(moment.hour if hasattr(moment, "hour") else None) if voice.get("time_of_day_greetings_enabled", False) else "day"
    return template.replace("{recipient}", recipient).replace("{time_of_day}", period)


DEFAULT_PROVIDER_SELECTIONS = {
    "Main AI / Conversation": "OpenAI",
    "Speech-to-Text": "OpenAI Audio",
    "Text-to-Speech": "OpenAI TTS",
    "Wake Word": "openWakeWord",
    "Internet Research": "SerpAPI",
    "Facial Recognition / Vision": "Luxand",
    "Seper": "Seper API",
    "APIFrame": "APIFrame",
    "APIBox": "APIBox",
    "User Accounts / Backend": "Supabase",
    "Music Playback": "Piped client / compatible server",
    "Smart Home": "Home Assistant",
    "Updates": "GitHub Releases",
    "Defensive security & compliance": "Select provider",
}

PROVIDER_OPTIONS = {
    "Main AI / Conversation": ["Select provider", "OpenAI", "Anthropic", "Google Gemini", "Custom OpenAI-compatible"],
    "Speech-to-Text": ["Select provider", "OpenAI Audio", "Google Cloud Speech", "Azure Speech", "Local Whisper", "Custom"],
    "Text-to-Speech": ["Select provider", "OpenAI TTS", "ElevenLabs", "Azure Speech", "Google Cloud TTS", "Windows Voice", "Custom"],
    "Wake Word": ["Select provider", "Porcupine", "openWakeWord", "Local detector"],
    "Internet Research": ["Select provider", "Tavily", "Brave Search", "Bing Search", "SerpAPI", "Custom"],
    "Facial Recognition / Vision": ["Select provider", "Luxand", "Custom vision API"],
    "Seper": ["Select provider", "Seper API", "Custom"],
    "APIFrame": ["Select provider", "APIFrame", "Custom"],
    "APIBox": ["Select provider", "APIBox", "Custom"],
    "Custom Function API": ["Select provider", "Custom API", "Custom MCP / HTTP"],
    "User Accounts / Backend": ["Select provider", "Supabase", "Firebase", "Auth0", "Custom Arthur Server"],
    "Music Playback": ["Select provider", "Spotify", "YouTube Music", "Piped client / compatible server", "BhariyaMusic-compatible server", "Local music files", "Custom"],
    "Original Singing": ["Select provider", "Music generation API", "Singing voice API", "Local singing model", "Disabled"],
    "Smart Home": ["Select provider", "Home Assistant", "Philips Hue", "SmartThings", "Tuya", "MQTT", "Other local hub", "Disabled"],
    "Updates": ["Select provider", "GitHub Releases", "Private update server", "Disabled"],
    "Defensive security & compliance": [
        "Select provider", "SecurityTrails", "URLScan.io", "AlienVault OTX", "GreyNoise", "IBM X-Force",
        "CrowdStrike", "Microsoft Defender", "Google Safe Browsing", "Have I Been Pwned", "NIST NVD",
        "MITRE ATT&CK", "CVE.org", "EPSS", "OpenCTI", "MISP", "PhishTank", "URLhaus",
        "MalwareBazaar", "ThreatFox", "CIRCL",
    ],
}

# These addresses are opened only when the user presses the provider-website
# button. A listed address is setup information, never evidence of a connection.
PROVIDER_WEBSITES = {
    "OpenAI": "https://platform.openai.com/",
    "OpenAI Audio": "https://platform.openai.com/",
    "OpenAI TTS": "https://platform.openai.com/",
    "Anthropic": "https://console.anthropic.com/",
    "Google Gemini": "https://aistudio.google.com/",
    "Google Cloud Speech": "https://cloud.google.com/speech-to-text",
    "Google Cloud TTS": "https://cloud.google.com/text-to-speech",
    "Azure Speech": "https://azure.microsoft.com/products/ai-services/ai-speech",
    "ElevenLabs": "https://elevenlabs.io/",
    "Porcupine": "https://picovoice.ai/platform/porcupine/",
    "openWakeWord": "https://github.com/dscripka/openWakeWord",
    "SerpAPI": "https://serpapi.com/",
    "Tavily": "https://tavily.com/",
    "Brave Search": "https://brave.com/search/api/",
    "Luxand": "https://www.luxand.com/",
    "Supabase": "https://supabase.com/",
    "Firebase": "https://firebase.google.com/",
    "Auth0": "https://auth0.com/",
    "GitHub Releases": "https://docs.github.com/repositories/releasing-projects-on-github",
    "Home Assistant": "https://www.home-assistant.io/",
    "Philips Hue": "https://developers.meethue.com/",
    "SmartThings": "https://developer.smartthings.com/",
    "Tuya": "https://developer.tuya.com/",
    "MQTT": "https://mqtt.org/",
    "Spotify": "https://developer.spotify.com/",
    "YouTube Music": "https://music.youtube.com/",
    "Piped client / compatible server": "https://github.com/KRTirtho/piped_client",
    "SecurityTrails": "https://securitytrails.com/",
    "URLScan.io": "https://urlscan.io/",
    "AlienVault OTX": "https://otx.alienvault.com/",
    "GreyNoise": "https://www.greynoise.io/",
    "IBM X-Force": "https://exchange.xforce.ibmcloud.com/",
    "CrowdStrike": "https://www.crowdstrike.com/",
    "Microsoft Defender": "https://www.microsoft.com/security/business/endpoint-security/microsoft-defender-endpoint",
    "Google Safe Browsing": "https://developers.google.com/safe-browsing",
    "Have I Been Pwned": "https://haveibeenpwned.com/API/v3",
    "NIST NVD": "https://nvd.nist.gov/developers",
    "MITRE ATT&CK": "https://attack.mitre.org/",
    "CVE.org": "https://www.cve.org/",
    "EPSS": "https://www.first.org/epss/",
    "OpenCTI": "https://filigran.io/solutions/opencti",
    "MISP": "https://www.misp-project.org/",
    "PhishTank": "https://phishtank.org/",
    "URLhaus": "https://urlhaus.abuse.ch/",
    "MalwareBazaar": "https://bazaar.abuse.ch/",
    "ThreatFox": "https://threatfox.abuse.ch/",
    "CIRCL": "https://www.circl.lu/",
}

DEFAULT_CONFIG = {
    "profile": {
        "display_name": "",
        "pronunciation": "",
        "native_language": "",
        "additional_languages": [],
        "language_favourites": ["English", "Kinyarwanda", "French", "Kiswahili"],
        "active_conversation_language": "",
        "music_source": "Not configured",
        "wake_word": "Arthur",
        "title": "Sir",
    },
    "privacy": {
        "background_enabled": True,
        "wake_word_background_enabled": False,
        "spoken_only": True,
        "confirm_risky": True,
        "allow_screen_analysis": False,
        "allow_broad_pc_access": False,
    },
    "conduct": {
        "refined_british_style": True,
        "direct_calm_responses": True,
        "dry_wit": True,
        "use_preferred_title": True,
        "propose_routines": False,
        "review_before_learning": True,
        "memory_retention_days": 30,
        "health_monitoring": True,
        "schedule_assistance": False,
        "camera_style_learning_enabled": False,
        "microphone_style_learning_enabled": False,
        "own_voice_cloning_requests_enabled": False,
        "style_sample_retention_days": 7,
    },
    "command_policy": {
        "wsl_distro": "",
        "allow_read_only_execution": False,
        "automation_paused": False,
    },
    "appearance": {
        "color_mode": "Cobalt",
        "type_scale": "Standard",
        "motion_reduced": False,
    },
    "autonomy": {
        "background_ready": False,
        "local_listening": False,
        "execution_consent": True,
        "visual_results": "Ask every time",
        "pause_all": False,
    },
    "voice": {
        "speech_recognition_route": "",
        "wake_word_model": "",
        "wake_word_listener_approved": False,
        "input_device": None,
        "arrival_greeting_enabled": True,
        "first_interaction_greeting_enabled": True,
        "wake_greeting_enabled": True,
        "greeting_scripts": DEFAULT_GREETING_SCRIPTS,
        "time_of_day_greetings_enabled": False,
        "do_not_disturb_enabled": False,
        "do_not_disturb_start": "22:00",
        "do_not_disturb_end": "07:00",
        "local_voice_id": "",
        "rate": 175,
        "volume": 100,
        "pitch": 0,
    },
    "interaction": {
        "touch_workspace_enabled": True,
        "air_gestures_approved": False,
        "gesture_camera_index": 0,
        "spatial_room_hello_enabled": False,
        "spatial_room_access_method": "",
        "spatial_room_face_camera_index": 0,
        "spatial_room_face_audio_cues": False,
    },
    "sensors": {
        "enabled": False,
    },
    "notes": [],
    "security": {
        "defensive_lookup_enabled": False,
    },
    "updates": {
        "github_repository": "bryagisubizo-bit/arthur",
        "manual_check_only": True,
        "last_checked_release": "",
    },
    "integrations": {},
    "setup_complete": False,
}


def load_config():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as handle:
                saved = json.load(handle)
            merged = json.loads(json.dumps(DEFAULT_CONFIG))
            for key, value in saved.items():
                if isinstance(value, dict) and isinstance(merged.get(key), dict):
                    merged[key].update(value)
                else:
                    merged[key] = value
            return merged
        except (OSError, json.JSONDecodeError):
            pass
    defaults = json.loads(json.dumps(DEFAULT_CONFIG))
    return apply_installer_defaults(defaults, load_installer_consent(INSTALLER_CONSENT_FILE))


def save_config(config):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = CONFIG_FILE.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
    temporary.replace(CONFIG_FILE)


class FirstRunDialog(QDialog):
    completed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to Arthur by Bogitech")
        self.setModal(True)
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        title = QLabel("Configure your Arthur profile")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        explanation = QLabel(
            "Choose the primary system language Arthur should use for both typed and voice conversations. You can change it later in Profile. "
            "Then choose how it should recognise spoken commands. The name pronunciation field may contain a phonetic spelling or a short pronunciation note."
        )
        explanation.setWordWrap(True)
        explanation.setObjectName("muted")
        layout.addWidget(explanation)

        form = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("The name Arthur should use for you")
        self.pronunciation = QLineEdit()
        self.pronunciation.setPlaceholderText("Example: Jean = Zhan")
        self.native_language = QComboBox()
        configure_primary_language_combo(self.native_language)
        self.speech_route = QComboBox()
        configure_speech_recognition_route_combo(self.speech_route)
        self.speech_route_note = QLabel("Choose local/offline recognition or a developer-configured provider. This choice does not install software, download a model, open the microphone, record audio, or connect a provider.")
        self.speech_route_note.setObjectName("muted")
        self.speech_route_note.setWordWrap(True)
        self.speech_route.currentIndexChanged.connect(self.update_speech_route_note)
        self.additional = QLineEdit()
        self.additional.setPlaceholderText("Optional: Spanish, Arabic, etc.")
        self.music = QComboBox()
        self.music.addItems(["Not configured", "Spotify", "YouTube Music", "Local music files"])
        self.wake_word = QLineEdit("Arthur")
        self.title = QLineEdit("Sir")
        form.addRow("Name to use:", self.name)
        form.addRow("Pronunciation:", self.pronunciation)
        form.addRow("Primary system language (required):", self.native_language)
        form.addRow("Speech recognition (required):", self.speech_route)
        form.addRow("Route readiness:", self.speech_route_note)
        form.addRow("Other languages:", self.additional)
        form.addRow("Music source:", self.music)
        form.addRow("Wake word:", self.wake_word)
        form.addRow("Preferred title:", self.title)
        layout.addLayout(form)

        self.spoken_only = QCheckBox("Reply by voice by default; ask before showing visual information")
        self.spoken_only.setChecked(True)
        layout.addWidget(self.spoken_only)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_speech_route_note(self):
        route_id = selected_speech_recognition_route(self.speech_route)
        detail = SPEECH_RECOGNITION_ROUTES.get(route_id, {}).get("detail")
        self.speech_route_note.setText(detail or "Choose local/offline recognition or a developer-configured provider. This choice does not install software, download a model, open the microphone, record audio, or connect a provider.")

    def accept(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Name required", "Please enter the name Arthur should use for you.")
            return
        primary_language = selected_primary_language(self.native_language)
        if not primary_language:
            QMessageBox.warning(self, "Language required", "Choose the primary system language Arthur should use for typed and voice interactions.")
            return
        speech_route = selected_speech_recognition_route(self.speech_route)
        if not speech_route:
            QMessageBox.warning(self, "Speech recognition route required", "Choose local/offline speech recognition or a developer-configured speech-to-text provider before configuring the profile.")
            return
        additional = [item.strip() for item in self.additional.text().split(",") if item.strip()]
        self.completed.emit({
            "display_name": self.name.text().strip(),
            "pronunciation": self.pronunciation.text().strip(),
            "native_language": primary_language,
            "additional_languages": additional,
            "music_source": self.music.currentText(),
            "wake_word": self.wake_word.text().strip() or "Arthur",
            "title": self.title.text().strip() or "Sir",
            "spoken_only": self.spoken_only.isChecked(),
            "speech_recognition_route": speech_route,
        })
        super().accept()


class FirstRunTutorialDialog(QDialog):
    """A concise, re-openable desktop orientation that teaches consent boundaries."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arthur — first-run tutorial")
        self.setModal(True)
        self.setMinimumWidth(650)
        layout = QVBoxLayout(self)
        title = QLabel("Welcome to Arthur")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        subtitle = QLabel("A short orientation for a local-first, consent-first desktop assistant.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        lessons = [
            ("1. Command desk", "Use ordinary language. Arthur explains the planned action and keeps risky or sensitive actions behind a confirmation gate."),
            ("2. Permissions & listening", "Arthur starts with local listening off. Enable background readiness, wake-word installation, or screen analysis only if you want them."),
            ("3. API Vault", "You, the developer, choose providers and store their credentials in Windows Credential Manager. Missing rooms remain unavailable instead of being invented."),
            ("4. Updates", "Choose Check GitHub Releases only when you want to use data. Arthur reads small release metadata; it never downloads or installs a release unless you approve it separately."),
            ("5. Your control", "Use Autonomy & change to adjust colour, type size, visual-result consent, and pause-all. Provider or code changes remain reviewable proposals."),
        ]
        for heading, copy in lessons:
            box = QGroupBox(heading)
            box_layout = QVBoxLayout(box)
            text = QLabel(copy)
            text.setWordWrap(True)
            text.setObjectName("muted")
            box_layout.addWidget(text)
            layout.addWidget(box)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class IntegrationCard(QFrame):
    changed = Signal(dict)

    def __init__(self, label, providers, saved=None, parent=None):
        super().__init__(parent)
        self.label = label
        saved = saved or {}
        self.connection_state = saved.get("connection_state", "unconnected")
        self.last_connection_test = saved.get("last_connection_test", "")
        self.setObjectName("integrationCard")
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel(label)
        title.setObjectName("cardTitle")
        self.status = QLabel("Not connected")
        self.status.setObjectName("statusOff")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status)
        layout.addLayout(header)

        self.provider = QComboBox()
        self.provider.addItems(providers)
        default_provider = DEFAULT_PROVIDER_SELECTIONS.get(label, "Select provider")
        if saved.get("provider") in providers:
            self.provider.setCurrentText(saved["provider"])
        elif default_provider in providers:
            self.provider.setCurrentText(default_provider)
        layout.addWidget(self.provider)

        website_row = QHBoxLayout()
        self.website_status = QLabel()
        self.website_status.setObjectName("muted")
        self.website_status.setWordWrap(True)
        self.provider_website_button = QPushButton("Open provider website")
        self.provider_website_button.clicked.connect(self.open_provider_website)
        website_row.addWidget(self.website_status, 1)
        website_row.addWidget(self.provider_website_button)
        layout.addLayout(website_row)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        if label == "User Accounts / Backend":
            self.api_key.setPlaceholderText("Supabase publishable key — never service role or DB password")
        elif label == "Defensive security & compliance":
            self.api_key.setPlaceholderText("Developer key — passive defensive enrichment only")
        else:
            self.api_key.setPlaceholderText("Developer API key — stored in OS credential manager")
        self.api_key.setText(get_secret(label))
        layout.addWidget(self.api_key)

        row = QHBoxLayout()
        self.endpoint = QLineEdit(saved.get("endpoint", ""))
        self.endpoint.setPlaceholderText("Supabase Project URL (https://…supabase.co)" if label == "User Accounts / Backend" else "Optional endpoint URL")
        self.model = QLineEdit(saved.get("model", ""))
        self.model.setPlaceholderText("Public client configuration" if label == "User Accounts / Backend" else "Optional model / voice")
        row.addWidget(self.endpoint)
        row.addWidget(self.model)
        layout.addLayout(row)

        self.local_discovery = None
        if label == "Smart Home":
            self.local_discovery = QCheckBox("Permit a separate review of local device discovery settings — no discovery or control is started")
            self.local_discovery.setChecked(bool(saved.get("local_discovery_review_enabled", False)))
            layout.addWidget(self.local_discovery)
            boundary = QLabel("Arthur never scans the network automatically. After you explicitly review a selected hub, it can use that hub's own authenticated API to list authorised devices; every device action remains confirmation-gated.")
            boundary.setObjectName("muted")
            boundary.setWordWrap(True)
            layout.addWidget(boundary)

        actions = QHBoxLayout()
        self.enabled = QCheckBox("Enabled")
        self.enabled.setChecked(saved.get("enabled", False))
        test = QPushButton("Check saved setup")
        test.clicked.connect(self.check_saved_setup)
        self.live_test = QPushButton("Run approved live test")
        self.live_test.clicked.connect(self.run_live_test)
        save = QPushButton("Save")
        save.clicked.connect(self.save_card)
        actions.addWidget(self.enabled)
        actions.addStretch()
        actions.addWidget(test)
        actions.addWidget(self.live_test)
        actions.addWidget(save)
        layout.addLayout(actions)
        self.provider.currentTextChanged.connect(self.mark_dirty)
        self.provider.currentTextChanged.connect(self.refresh_provider_details)
        self.api_key.textChanged.connect(self.mark_dirty)
        if self.local_discovery is not None:
            self.local_discovery.toggled.connect(self.mark_dirty)
        self.refresh_provider_details()
        self.refresh_connection_status()

    def refresh_provider_details(self):
        provider = self.provider.currentText()
        website = PROVIDER_WEBSITES.get(provider)
        if provider == "Select provider":
            self.website_status.setText("Choose a provider to view its setup website. Arthur is not connected.")
            self.provider_website_button.setEnabled(False)
            self.live_test.setEnabled(False)
            return
        if website:
            self.website_status.setText(f"Official setup website available. Arthur is not connected until you save settings and explicitly approve a live test.")
            self.provider_website_button.setEnabled(True)
            self.live_test.setEnabled(provider == "OpenAI")
            return
        self.website_status.setText("No official website is listed for this local or custom option. Status: not connected.")
        self.provider_website_button.setEnabled(False)
        self.live_test.setEnabled(False)

    def refresh_connection_status(self):
        labels = {
            "unconnected": ("Not connected", "statusOff"),
            "key_required": ("Key required", "statusWarn"),
            "saved_locally": ("Saved locally — not tested", "statusWarn"),
            "adapter_ready": ("Adapter ready — not tested", "statusWarn"),
            "adapter_unavailable": ("No live-test adapter", "statusWarn"),
            "test_passed": ("Last approved test passed", "statusOn"),
            "test_failed": ("Last approved test failed", "statusOff"),
        }
        text, object_name = labels.get(self.connection_state, labels["unconnected"])
        self.status.setText(text)
        self.status.setObjectName(object_name)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def open_provider_website(self):
        provider = self.provider.currentText()
        website = PROVIDER_WEBSITES.get(provider)
        if not website:
            QMessageBox.information(self, "Provider website unavailable", "Arthur has no official website recorded for this local or custom option.")
            return
        if not QDesktopServices.openUrl(QUrl(website)):
            QMessageBox.information(self, "Open provider website", f"Open this address in your browser:\n{website}")

    def secret_value(self):
        return self.api_key.text().strip()

    def payload(self):
        data = {
            "provider": self.provider.currentText(),
            "api_key_present": bool(self.secret_value()),
            "endpoint": self.endpoint.text().strip(),
            "model": self.model.text().strip(),
            "enabled": self.enabled.isChecked(),
            "connection_state": self.connection_state,
            "last_connection_test": self.last_connection_test,
        }
        if self.local_discovery is not None:
            data["local_discovery_review_enabled"] = self.local_discovery.isChecked()
        return data

    def mark_dirty(self):
        self.status.setText("Unsaved")
        self.status.setObjectName("statusWarn")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def save_card(self):
        data = self.payload()
        secret = self.secret_value()
        if data["provider"] == "Select provider":
            QMessageBox.warning(self, "Provider required", f"Choose a provider for {self.label}.")
            return
        if not secret and data["provider"] not in {"Local Whisper", "Windows Voice", "Local detector", "Local music files", "Local singing model", "Disabled", "Home Assistant"}:
            QMessageBox.warning(self, "API key required", f"Enter the developer API key for {self.label}.")
            return
        if secret and not set_secret(self.label, secret):
            QMessageBox.warning(self, "Secure storage unavailable", "Arthur could not access the operating-system credential store. The key was not written to disk.")
            return
        self.connection_state = setup_state(data["provider"], bool(secret))
        self.refresh_connection_status()
        self.changed.emit(self.payload())

    def check_saved_setup(self):
        data = self.payload()
        secret = self.secret_value()
        if data["provider"] == "Select provider":
            QMessageBox.warning(self, "Provider required", f"Choose a provider for {self.label} first.")
            return
        if not secret and data["provider"] not in {"Local Whisper", "Windows Voice", "Local detector", "Local music files", "Local singing model", "Disabled", "Home Assistant"}:
            QMessageBox.warning(self, "API key required", "Enter a developer key before testing this provider.")
            return
        if self.label == "Defensive security & compliance":
            QMessageBox.information(
                self,
                "Defensive room review",
                "This configuration check does not scan, probe, exploit, test credentials, fetch malware, or contact a target. "
                "Arthur will require a separate approved passive-enrichment request before a connected provider can be used.",
            )
            return
        self.connection_state = setup_state(data["provider"], bool(secret))
        self.refresh_connection_status()
        data = self.payload()
        self.changed.emit(data)
        QMessageBox.information(self, "Saved setup checked", f"{self.label} has saved local settings for {data['provider']}.\n\nState: {self.status.text()}. Arthur has not contacted the provider. Only the separate ‘Run approved live test’ action can change a provider to a tested state.")

    def run_live_test(self):
        data = self.payload()
        if data["provider"] == "Select provider":
            QMessageBox.warning(self, "Provider required", f"Choose a provider for {self.label} first.")
            return
        if QMessageBox.question(
            self,
            "Approve live connection test?",
            f"Arthur will send one HTTPS request to the official {data['provider']} API using the key currently entered in this card. No prompt, personal data, audio, or file will be sent. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        result = run_approved_connection_test(data["provider"], self.secret_value())
        self.connection_state = result.state
        self.last_connection_test = datetime.now().isoformat(timespec="seconds")
        self.refresh_connection_status()
        self.changed.emit(self.payload())
        title = "Connection test passed" if result.state == "test_passed" else "Connection test did not pass"
        QMessageBox.information(self, title, result.detail)


class MessageDraftDialog(QDialog):
    """Collect a WhatsApp draft only; this dialog never sends a message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prepare WhatsApp draft")
        self.setMinimumWidth(470)
        layout = QVBoxLayout(self)
        title = QLabel("Prepare a message for your review")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        note = QLabel("Arthur will not send a message. After you approve this draft, it can copy the text so you may paste, review, and send it yourself in WhatsApp.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        self.recipient = QLineEdit()
        self.recipient.setPlaceholderText("Name as it appears in your contacts")
        self.message = QTextEdit()
        self.message.setPlaceholderText("Exact message to prepare")
        self.message.setFixedHeight(110)
        form.addRow("Recipient:", self.recipient)
        form.addRow("Message:", self.message)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.recipient.text().strip() or not self.message.toPlainText().strip():
            QMessageBox.warning(self, "Draft required", "Enter the recipient and exact message before preparing the draft.")
            return
        super().accept()


class Dashboard(QWidget):
    """Windows command desk patterned after the live-preview hero workspace."""

    def __init__(self, config, voice_runtime, save_callback, command_session_callback, spatial_room_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.voice_runtime = voice_runtime
        self.save_callback = save_callback
        self.command_session_callback = command_session_callback
        self.spatial_room_callback = spatial_room_callback
        self.current_plan = None
        self.current_planner = None
        layout = QVBoxLayout(self)
        layout.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("heroPanel")
        hero_layout = QVBoxLayout(hero)
        eyebrow = QLabel("ORBITAL COMMAND ATELIER // WINDOWS 11")
        eyebrow.setObjectName("eyebrow")
        title_row = QHBoxLayout()
        title = QLabel("Ask naturally. Arthur will plan safely.")
        title.setObjectName("heroTitle")
        self.listening = QLabel("● STANDBY")
        self.listening.setObjectName("statusOn")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self.listening)
        subtitle = QLabel("Use ordinary language in Kinyarwanda, English, French, or Kiswahili. Arthur only prepares reviewed local actions and asks before anything consequential.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(eyebrow)
        hero_layout.addLayout(title_row)
        hero_layout.addWidget(subtitle)
        command_row = QHBoxLayout()
        self.command = QLineEdit()
        self.command.setObjectName("commandInput")
        self.command.setPlaceholderText("For example: show my disk space, check my internet, or lock my computer")
        prepare = QPushButton("Prepare plan")
        prepare.setObjectName("primaryButton")
        prepare.clicked.connect(self.handle_command)
        self.command.returnPressed.connect(self.handle_command)
        command_row.addWidget(self.command, 1)
        command_row.addWidget(prepare)
        hero_layout.addLayout(command_row)
        self.execute_plan = QPushButton("Approve & run reviewed action")
        self.execute_plan.setEnabled(False)
        self.execute_plan.clicked.connect(self.execute_current_plan)
        hero_layout.addWidget(self.execute_plan)
        self.command_result = QLabel("No plan prepared. Arthur will show its route, risk, and confirmation requirement before an action can run.")
        self.command_result.setObjectName("commandResult")
        self.command_result.setWordWrap(True)
        hero_layout.addWidget(self.command_result)
        self.focus_cue = QLabel("LOCAL CONTEXT • Standby • Visual results remain gated by your preference")
        self.focus_cue.setObjectName("focusCue")
        hero_layout.addWidget(self.focus_cue)
        layout.addWidget(hero)

        metrics = QGridLayout()
        metrics.setSpacing(14)
        self.cpu = self.metric_card("CPU LOAD", "-- %", "LOCAL SIGNAL")
        self.ram = self.metric_card("MEMORY", "-- %", "LOCAL SIGNAL")
        self.gpu = self.metric_card("GPU LOAD", "—", "LOCAL / OPT-IN")
        self.temp = self.metric_card("SYSTEM TEMP", "—", "LOCAL / OPT-IN")
        for index, card in enumerate([self.cpu, self.ram, self.gpu, self.temp]):
            metrics.addWidget(card, index // 2, index % 2)
        layout.addLayout(metrics)

        ledger = QFrame()
        ledger.setObjectName("ledgerPanel")
        ledger_layout = QVBoxLayout(ledger)
        ledger_title = QLabel("ACTION LEDGER")
        ledger_title.setObjectName("eyebrow")
        self.output = QTextEdit()
        self.output.setObjectName("ledgerOutput")
        self.output.setReadOnly(True)
        self.output.setFixedHeight(130)
        self.output.append("Arthur is ready. Voice output remains the default response mode.")
        self.output.append("The desktop command desk uses fixed reviewed templates; it never runs raw generated shell text.")
        ledger_layout.addWidget(ledger_title)
        ledger_layout.addWidget(self.output)
        layout.addWidget(ledger)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1500)
        self.update_metrics()

    def metric_card(self, label, value, detail):
        card = QFrame()
        card.setObjectName("metricCard")
        box = QVBoxLayout(card)
        top = QHBoxLayout()
        name = QLabel(label)
        name.setObjectName("metricLabel")
        tag = QLabel(detail)
        tag.setObjectName("metricTag")
        top.addWidget(name)
        top.addStretch()
        top.addWidget(tag)
        value_label = QLabel(value)
        value_label.setObjectName("metricValue")
        box.addLayout(top)
        box.addWidget(value_label)
        card.value_label = value_label
        return card

    def update_metrics(self):
        if not self.config.setdefault("sensors", {}).get("enabled", False):
            for card in [self.cpu, self.gpu, self.ram, self.temp]:
                card.value_label.setText("Permission off")
            return
        # The dashboard polls only while its page is visible. Arthur collects no
        # readings when this workspace is closed, hidden, or in the tray.
        if not self.isVisible():
            return
        snapshot = collect_snapshot()
        self.cpu.value_label.setText(snapshot["cpu"]["value"])
        self.ram.value_label.setText(snapshot["memory"]["value"])
        self.gpu.value_label.setText(snapshot["gpu"]["value"])
        self.temp.value_label.setText(snapshot["temperature"]["value"])

    def handle_command(self):
        request = self.command.text().strip()
        if not request:
            return
        self.command_session_callback("Command session active")
        policy = self.config.get("command_policy", {})
        self.current_planner = CommandPlanner(wsl_distro=policy.get("wsl_distro", ""))
        plan = self.current_planner.plan(request)
        self.current_plan = plan
        tone = "BLOCKED" if not plan.allowed else plan.risk.value.upper()
        confirmation = " • confirmation required" if plan.requires_confirmation else " • reviewed diagnostic"
        self.command_result.setText(f"{tone}{confirmation}\n{plan.summary}\nRoute: {plan.preview()}")
        visual_preference = self.config.get("autonomy", {}).get("visual_results", "Ask every time")
        self.focus_cue.setText(f"REVIEWED ACTIVITY • {tone} • Visual-result policy: {visual_preference}")
        self.output.append(f"You: {request}")
        self.output.append(f"Arthur: {plan.summary}")
        self.execute_plan.setEnabled(plan.allowed and plan.requires_confirmation)
        execute_labels = {
            "whatsapp_message_draft": "Prepare WhatsApp draft",
            "open_spatial_workspace": "Review & unlock Spatial room",
        }
        self.execute_plan.setText(execute_labels.get(plan.intent, "Approve & run reviewed action"))
        if plan.intent == "language_switch":
            language = language_switch_target(request)
            if language:
                self.config.setdefault("profile", {})["native_language"] = language
                self.config["profile"]["active_conversation_language"] = language
                self.save_callback()
                confirmation = {
                    "English": "Certainly. I will reply in English.",
                    "Kinyarwanda": "Yego. Ubu ndagusubiza mu Kinyarwanda.",
                    "French": "Bien entendu. Je répondrai en français.",
                    "Kiswahili": "Sawa. Sasa nitajibu kwa Kiswahili.",
                }.get(language, f"Certainly. I will use {language} as your selected conversation preference. Arthur will ask for an approved local pack or provider before attempting speech, translation, or research in that language.")
                self.output.append(f"Arthur: {confirmation}")
                if self.config.get("privacy", {}).get("spoken_only", True):
                    self.voice_runtime.speak(confirmation)
                self.command_result.setText(f"LANGUAGE PREFERENCE UPDATED\n{plan.summary}\nNo provider call was made. Full spoken transcription still requires an approved speech-to-text room.")
            self.execute_plan.setEnabled(False)
        elif plan.risk in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            advisory = "This action can affect another application or your session. I will not continue until you approve the exact reviewed route."
            self.output.append(f"Arthur advisory: {advisory}")
            if self.config.get("privacy", {}).get("spoken_only", True):
                self.voice_runtime.speak(advisory)
        if self.config.get("privacy", {}).get("spoken_only", True):
            self.voice_runtime.speak(plan.summary)
        self.command.clear()

    def execute_current_plan(self):
        plan = self.current_plan
        if plan is None or self.current_planner is None or not plan.allowed or not plan.requires_confirmation:
            return
        if plan.intent == "whatsapp_message_draft":
            draft = MessageDraftDialog(self)
            if draft.exec() != QDialog.DialogCode.Accepted:
                return
            recipient = draft.recipient.text().strip()
            message = draft.message.toPlainText().strip()
            choice = QMessageBox.question(
                self,
                "Confirm message draft",
                f"Arthur will copy this draft for {recipient}. It will not send it or contact WhatsApp.\n\n{message}\n\nCopy the draft now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if choice == QMessageBox.StandardButton.Yes:
                QApplication.clipboard().setText(message)
                self.output.append(f"Arthur: Prepared a WhatsApp draft for {recipient}; the text is copied for your manual review and send.")
                self.command_result.setText("MESSAGE DRAFT PREPARED\nThe text was copied locally. Arthur did not open WhatsApp, select a contact, or send a message.")
            return
        if plan.intent == "open_spatial_workspace":
            choice = QMessageBox.question(
                self,
                "Open protected Spatial room?",
                "Arthur will open only its own protected Spatial workspace. You must still verify local access with your password or configured Windows Hello method. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if choice != QMessageBox.StandardButton.Yes:
                self.output.append("Arthur: The protected Spatial room was not opened.")
                return
            if self.spatial_room_callback():
                self.output.append("Arthur: The protected Spatial room is open for this local session.")
                self.command_result.setText("SPATIAL ROOM OPEN\nLocal access verification succeeded. Touch and optional local gesture controls remain limited to Arthur’s workspace.")
            else:
                self.output.append("Arthur: The protected Spatial room remains locked.")
                self.command_result.setText("SPATIAL ROOM LOCKED\nArthur did not open the workspace because local access verification was not completed.")
            self.execute_plan.setEnabled(False)
            return
        choice = QMessageBox.question(
            self,
            "Approve reviewed action",
            f"Arthur will now perform this exact reviewed action:\n\n{plan.preview()}\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if choice != QMessageBox.StandardButton.Yes:
            self.output.append("Arthur: The reviewed action was not approved.")
            return
        try:
            _code, stdout, stderr = self.current_planner.execute(plan, approved=True)
            detail = stdout.strip() or stderr.strip() or "The reviewed action finished without additional output."
            self.output.append(f"Arthur: {detail}")
            self.command_result.setText(f"APPROVED ACTION COMPLETED\n{plan.summary}\n{detail}")
        except (OSError, PermissionError, subprocess.SubprocessError) as error:
            self.output.append(f"Arthur: The approved action did not complete: {error}")
            self.command_result.setText(f"ACTION NOT COMPLETED\n{error}")
        finally:
            self.execute_plan.setEnabled(False)


class SystemSensorsPage(QWidget):
    """Visible, local-only diagnostics. No readings are retained or uploaded."""

    SENSOR_LABELS = (
        ("cpu", "CPU usage"),
        ("memory", "Memory"),
        ("storage", "System storage"),
        ("battery", "Battery"),
        ("network", "Network adapter"),
        ("temperature", "Thermal zone"),
        ("gpu", "GPU telemetry"),
    )

    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self.cards = {}
        layout = QVBoxLayout(self)
        title = QLabel("Local system sensors")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        note = QLabel("Arthur reads these on this Windows PC only after you enable them. It does not send readings to a provider, store historical telemetry, install a hardware-monitoring service, or collect readings while this workspace is closed.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.enabled = QCheckBox("Enable local sensor readings while this workspace is open")
        self.enabled.setChecked(config.setdefault("sensors", {}).get("enabled", False))
        self.enabled.toggled.connect(self.set_enabled)
        layout.addWidget(self.enabled)
        controls = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh local readings")
        self.refresh_button.setObjectName("primaryButton")
        self.refresh_button.clicked.connect(self.refresh)
        controls.addWidget(self.refresh_button)
        controls.addStretch()
        layout.addLayout(controls)
        self.status = QLabel()
        self.status.setObjectName("safetyBoundary")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        grid = QGridLayout()
        grid.setSpacing(14)
        for index, (key, label) in enumerate(self.SENSOR_LABELS):
            card = QFrame()
            card.setObjectName("metricCard")
            card_layout = QVBoxLayout(card)
            heading = QLabel(label.upper())
            heading.setObjectName("metricLabel")
            value = QLabel("Permission off")
            value.setObjectName("metricValue")
            detail = QLabel("No local reading requested.")
            detail.setObjectName("muted")
            detail.setWordWrap(True)
            card_layout.addWidget(heading)
            card_layout.addWidget(value)
            card_layout.addWidget(detail)
            self.cards[key] = (value, detail)
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)
        layout.addStretch()
        self.refresh()

    def set_enabled(self, enabled):
        self.config.setdefault("sensors", {})["enabled"] = bool(enabled)
        self.save_callback()
        self.refresh()

    def refresh(self):
        if not self.enabled.isChecked():
            self.refresh_button.setEnabled(False)
            self.status.setText("Local sensor diagnostics are off. Enable the visible permission above to request transient readings on this device.")
            for value, detail in self.cards.values():
                value.setText("Permission off")
                detail.setText("No local reading requested.")
            return
        self.refresh_button.setEnabled(True)
        snapshot = collect_snapshot()
        for key, (value, detail) in self.cards.items():
            reading = snapshot[key]
            value.setText(reading["value"])
            detail.setText(reading["detail"])
        unavailable = [key for key, reading in snapshot.items() if reading["state"] == "unavailable"]
        suffix = " Some readings are unavailable; this is expected on hardware Windows does not expose." if unavailable else ""
        self.status.setText("Fresh local readings displayed. Arthur did not save or transmit them." + suffix)


class ToolsRoutingPage(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Tools & routing", "Transparent routes for local tasks, information, voice, applications, and approved automations."))
        grid = QGridLayout()
        routes = [
            ("Local diagnostics", "Reviewed templates only", "LOW RISK"),
            ("Information research", "Requires an approved API room", "RESOURCE GATED"),
            ("Voice response", "Provider-selected output", "CONSENT FIRST"),
            ("Application control", "Windows adapter not connected", "DESKTOP ADAPTER"),
            ("Automations", "Pause-all control applies", "REVIEW REQUIRED"),
            ("Visual results", "Show only when your preference allows", "PRIVACY LOCK"),
        ]
        for index, (title, note, state) in enumerate(routes):
            grid.addWidget(info_card(title, note, state), index // 2, index % 2)
        layout.addLayout(grid)
        boundary = QLabel("Arthur does not route requests into intrusion, credential collection, bypasses, network scanning, exploitation, malware, weapon, or arbitrary shell capabilities.")
        boundary.setObjectName("safetyBoundary")
        boundary.setWordWrap(True)
        layout.addWidget(boundary)
        layout.addStretch()


class SpatialPasswordDialog(QDialog):
    """Ask for a protected-room password without keeping it in widget state after close."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unlock Spatial workspace")
        self.setModal(True)
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter the local Spatial-room password. Arthur stores only a salted verifier in Windows Credential Manager; it never saves the password in its configuration file."))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Spatial-room password")
        layout.addWidget(self.password)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.password.text():
            QMessageBox.warning(self, "Password required", "Enter the protected Spatial-room password or cancel.")
            return
        super().accept()


class SpatialPasswordSetupDialog(QDialog):
    """Set a new password; no password value is retained after this dialog closes."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Spatial-room password")
        self.setModal(True)
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        note = QLabel("Set a local password with at least 10 characters. Arthur stores only a salted verifier in Windows Credential Manager. It is a separate access method; selecting Windows Hello or local camera face access can remove this verifier.")
        note.setObjectName("safetyBoundary")
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmation = QLineEdit()
        self.confirmation.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("New password:", self.password)
        form.addRow("Confirm password:", self.confirmation)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if self.password.text() != self.confirmation.text():
            QMessageBox.warning(self, "Passwords differ", "Enter the same password in both fields.")
            return
        if len(self.password.text()) < 10:
            QMessageBox.warning(self, "Password too short", "Choose a Spatial-room password with at least 10 characters.")
            return
        super().accept()


class FaceAccessSetupDialog(QDialog):
    """Collect explicit consent before the optional visible local face enrolment."""

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set up local camera face access")
        self.setModal(True)
        self.setMinimumWidth(560)
        layout = QVBoxLayout(self)
        notice = QLabel("Experimental local face access is not Windows Hello. Arthur will open the selected camera only after this setup is confirmed. It processes enrolment frames in memory and stores only an encrypted local recognition model—never a raw image or video. No face data leaves this PC.")
        notice.setObjectName("safetyBoundary")
        notice.setWordWrap(True)
        layout.addWidget(notice)
        form = QFormLayout()
        self.camera = QSpinBox()
        self.camera.setRange(0, 8)
        self.camera.setValue(camera_index)
        self.recovery = QLineEdit()
        self.recovery.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirmation = QLineEdit()
        self.confirmation.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Camera index:", self.camera)
        form.addRow("Recovery secret (12+ characters):", self.recovery)
        form.addRow("Confirm recovery secret:", self.confirmation)
        layout.addLayout(form)
        self.consent = QCheckBox("I approve visible local camera enrolment and understand this experimental method is not equivalent to Windows Hello.")
        self.consent.setWordWrap(True)
        layout.addWidget(self.consent)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.consent.isChecked():
            QMessageBox.warning(self, "Consent required", "Confirm the visible local-camera enrolment notice before Arthur can request the selected camera.")
            return
        if self.recovery.text() != self.confirmation.text():
            QMessageBox.warning(self, "Recovery secrets differ", "Enter the same recovery secret twice.")
            return
        if len(self.recovery.text()) < 12:
            QMessageBox.warning(self, "Recovery secret too short", "Choose a recovery secret with at least 12 characters.")
            return
        super().accept()


class FaceRecoveryDialog(QDialog):
    """Ask for the recovery secret only to erase a failed local face enrolment."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recover local face access")
        self.setModal(True)
        self.setMinimumWidth(480)
        layout = QVBoxLayout(self)
        note = QLabel("Enter the recovery secret to erase the encrypted local face template. This does not unlock the room; after deletion, choose and configure a new access method.")
        note.setObjectName("safetyBoundary")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.recovery = QLineEdit()
        self.recovery.setEchoMode(QLineEdit.EchoMode.Password)
        self.recovery.setPlaceholderText("Recovery secret")
        layout.addWidget(self.recovery)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.recovery.text():
            QMessageBox.warning(self, "Recovery secret required", "Enter the recovery secret or cancel.")
            return
        super().accept()


class SpatialWorkspacePage(QWidget):
    """Touch-first Arthur workspace with an optional, local-only air-gesture adapter."""

    gesture_detected = Signal(object)
    gesture_status = Signal(str)

    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self.listener = None
        self.last_removed = None
        self.session_unlocked = False
        self.face_lockout_timer = QTimer(self)
        self.face_lockout_timer.setInterval(1000)
        self.face_lockout_timer.timeout.connect(self.update_access_state)
        self.face_lockout_timer.start()
        self.grabGesture(Qt.GestureType.SwipeGesture)
        self.grabGesture(Qt.GestureType.PinchGesture)
        self.gesture_detected.connect(self.handle_gesture)
        self.gesture_status.connect(self.set_gesture_status)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Spatial workspace", "Use your touch screen to arrange Arthur’s own cards: swipe horizontally, pinch to change scale, drag a card, or remove it with an undo path."))

        overview = QLabel("Touch controls work in Arthur’s window only. They never inject gestures into another application, move the Windows pointer, or control a device. Camera-based air gestures remain off unless you explicitly enable them below.")
        overview.setObjectName("safetyBoundary")
        overview.setWordWrap(True)
        layout.addWidget(overview)

        access = QGroupBox("Protected Spatial room")
        access_layout = QFormLayout(access)
        self.access_status = QLabel("Locked for this session. Choose one access method before entering this room.")
        self.access_status.setObjectName("safetyBoundary")
        self.access_status.setWordWrap(True)
        access_layout.addRow("Access state:", self.access_status)
        self.access_setup_button = QPushButton("Choose room access method")
        self.access_setup_button.setObjectName("secondaryButton")
        self.access_setup_button.clicked.connect(self.configure_access)
        self.access_unlock_button = QPushButton("Unlock room")
        self.access_unlock_button.setObjectName("primaryButton")
        self.access_unlock_button.clicked.connect(self.request_access)
        self.access_lock_button = QPushButton("Lock room now")
        self.access_lock_button.clicked.connect(self.lock_room)
        access_buttons = QHBoxLayout()
        for button in [self.access_setup_button, self.access_unlock_button, self.access_lock_button]:
            access_buttons.addWidget(button)
        access_button_holder = QWidget()
        access_button_holder.setLayout(access_buttons)
        access_layout.addRow("Local access:", access_button_holder)
        _hello_ok, hello_detail = windows_hello_availability()
        self.access_method_detail = QLabel("No method selected. Choose local password, Windows Hello, or experimental local camera face access.")
        self.access_method_detail.setObjectName("muted")
        self.access_method_detail.setWordWrap(True)
        self.hello_detail = QLabel(hello_detail)
        self.hello_detail.setObjectName("muted")
        self.hello_detail.setWordWrap(True)
        self.hello_install_button = QPushButton("Copy optional Windows Hello install command")
        self.hello_install_button.setObjectName("secondaryButton")
        self.hello_install_button.clicked.connect(lambda: self.copy_optional_install("requirements-hello-optional.txt"))
        self.hello_setup_button = QPushButton("Open Windows Hello sign-in settings")
        self.hello_setup_button.setObjectName("secondaryButton")
        self.hello_setup_button.clicked.connect(self.open_windows_hello_settings)
        face_ready, face_detail = face_dependency_status()
        self.face_status = QLabel(face_detail)
        self.face_status.setObjectName("muted")
        self.face_status.setWordWrap(True)
        self.face_install_button = QPushButton("Copy optional local face-access install command")
        self.face_install_button.setObjectName("secondaryButton")
        self.face_install_button.clicked.connect(lambda: self.copy_optional_install("requirements-face-access-optional.txt"))
        self.face_recovery_button = QPushButton("Recover / erase local face access")
        self.face_recovery_button.setObjectName("secondaryButton")
        self.face_recovery_button.clicked.connect(self.recover_face_access)
        self.face_test_button = QPushButton("Run visible local camera readiness test")
        self.face_test_button.setObjectName("secondaryButton")
        self.face_test_button.clicked.connect(self.run_face_camera_test)
        self.face_audio_cue = QCheckBox("Play a local system tone for camera activation and verification results")
        self.face_audio_cue.setChecked(config.get("interaction", {}).get("spatial_room_face_audio_cues", False))
        self.face_audio_cue.toggled.connect(self.save_face_audio_cue_preference)
        self.face_lockout_label = QLabel("No recent local face-check failures.")
        self.face_lockout_label.setObjectName("muted")
        self.face_lockout_label.setWordWrap(True)
        access_layout.addRow("Selected access method:", self.access_method_detail)
        access_layout.addRow("Windows Hello status:", self.hello_detail)
        access_layout.addRow("Face or PIN enrolment:", self.hello_setup_button)
        access_layout.addRow("Optional adapter:", self.hello_install_button)
        access_layout.addRow("Local camera face status:", self.face_status)
        access_layout.addRow("Local camera adapter:", self.face_install_button)
        access_layout.addRow("Camera acceptance test:", self.face_test_button)
        access_layout.addRow("Accessibility audio cue:", self.face_audio_cue)
        access_layout.addRow("Face-check cooldown:", self.face_lockout_label)
        access_layout.addRow("Face recovery:", self.face_recovery_button)
        self.hello_privacy_note = QLabel("Choose exactly one method: a local room password, OS-managed Windows Hello, or experimental local camera face access. Windows Hello uses Windows’ camera flow. Local camera face access starts only after separate consent and enrolment, shows a camera-active preview, stores no raw image or video (including no failed frame), and keeps only an encrypted local model. Neither method uploads face data. Local camera face access is not equivalent to Windows Hello, requires a recovery secret for reset, and applies a short local cooldown after repeated non-matches.")
        self.hello_privacy_note.setObjectName("muted")
        self.hello_privacy_note.setWordWrap(True)
        access_layout.addRow(self.hello_privacy_note)
        layout.addWidget(access)

        controls = QGroupBox("Touch canvas controls")
        controls_layout = QFormLayout(controls)
        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(70, 150)
        self.zoom.setValue(100)
        self.zoom.valueChanged.connect(self.update_scale)
        controls_layout.addRow("Canvas scale:", self.zoom)
        self.card_list = QListWidget()
        self.card_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.card_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.card_list.addItems(["Research field", "System diagnostics", "Private note", "Voice signal", "Smart-home review"])
        controls_layout.addRow("Touch & drag cards:", self.card_list)
        action_row = QHBoxLayout()
        self.previous_card = QPushButton("← Previous")
        self.next_card = QPushButton("Next →")
        discard = QPushButton("Discard selected…")
        self.undo_discard = QPushButton("Undo discard")
        self.undo_discard.setEnabled(False)
        self.previous_card.clicked.connect(lambda: self.move_selection(-1))
        self.next_card.clicked.connect(lambda: self.move_selection(1))
        discard.clicked.connect(self.request_discard)
        self.undo_discard.clicked.connect(self.undo_last_discard)
        for button in [self.previous_card, self.next_card, discard, self.undo_discard]:
            action_row.addWidget(button)
        action_holder = QWidget()
        action_holder.setLayout(action_row)
        controls_layout.addRow("Reviewed card action:", action_holder)
        layout.addWidget(controls)
        self.touch_controls = controls

        air = QGroupBox("Optional local air gestures")
        air_layout = QFormLayout(air)
        self.air_gestures = QCheckBox("I understand that enabling air gestures opens my selected camera locally")
        self.air_gestures.setChecked(config.get("interaction", {}).get("air_gestures_approved", False))
        self.camera_choice = QSpinBox()
        self.camera_choice.setRange(0, 8)
        self.camera_choice.setValue(config.get("interaction", {}).get("gesture_camera_index", 0))
        self.gesture_status_label = QLabel("Disabled by default. No camera, video, hand landmark, or biometric template is retained.")
        self.gesture_status_label.setObjectName("muted")
        self.gesture_status_label.setWordWrap(True)
        self.gesture_button = QPushButton("Enable local air gestures")
        self.gesture_button.setObjectName("secondaryButton")
        self.gesture_button.clicked.connect(self.toggle_air_gestures)
        package_ok, package_detail = optional_dependency_status()
        dependency = QLabel(("Ready to request consent. " if package_ok else "Optional package missing. ") + package_detail)
        dependency.setObjectName("muted")
        dependency.setWordWrap(True)
        air_layout.addRow("Consent:", self.air_gestures)
        air_layout.addRow("Selected camera index:", self.camera_choice)
        air_layout.addRow("Optional adapter:", dependency)
        self.gesture_install_button = QPushButton("Copy optional gesture install command")
        self.gesture_install_button.setObjectName("secondaryButton")
        self.gesture_install_button.clicked.connect(lambda: self.copy_optional_install("requirements-gesture-optional.txt"))
        air_layout.addRow("Manual installation:", self.gesture_install_button)
        air_layout.addRow("Camera status:", self.gesture_status_label)
        air_layout.addRow("Control:", self.gesture_button)
        layout.addWidget(air)
        self.air_controls = air
        layout.addWidget(QLabel("Recognised gestures are intentionally limited: a sideways hand motion selects the previous or next Arthur card; a pinch changes this canvas scale; a deliberate open palm asks before discarding the selected card. Air gestures never execute PC actions without a separate reviewed confirmation."))
        self.update_access_state()
        layout.addStretch()

    def copy_optional_install(self, requirement_file):
        command = f"pip install -r {requirement_file}"
        QApplication.clipboard().setText(command)
        QMessageBox.information(self, "Installation command copied", f"Arthur did not run an installation. Review and run this optional command yourself from the Arthur source folder:\n\n{command}")

    def open_windows_hello_settings(self):
        """Open the user-initiated Windows screen that owns face/PIN enrolment."""
        opened = QDesktopServices.openUrl(QUrl("ms-settings:signinoptions"))
        if not opened:
            QMessageBox.information(self, "Windows Hello setup", "Open Windows Settings → Accounts → Sign-in options to enrol face or PIN. Arthur does not open or scan a camera for this setup.")

    def save_face_audio_cue_preference(self, enabled):
        self.config.setdefault("interaction", {})["spatial_room_face_audio_cues"] = bool(enabled)
        self.save_callback()

    def play_face_access_cue(self, outcome):
        """Use only the local system beep; never speak or disclose biometric details."""
        if not self.face_audio_cue.isChecked():
            return
        count = {"camera_active": 1, "verified": 2, "not_verified": 3}.get(outcome, 1)
        for index in range(count):
            QTimer.singleShot(index * 160, QApplication.beep)

    def run_face_camera_test(self):
        face_ready, detail = face_dependency_status()
        if not face_ready:
            QMessageBox.warning(self, "Local camera adapter unavailable", f"{detail}\n\nArthur did not open a camera. Review the optional local requirement, install it manually if you choose, then retry.")
            return
        camera_index = self.config.get("interaction", {}).get("spatial_room_face_camera_index", 0)
        approval = QMessageBox.question(self, "Run visible local camera readiness test?", "Arthur will open only your selected local camera for a short, visible readiness test. The preview labels the camera as active. No enrolment occurs and no image, video, model, failed frame, or log is kept. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if approval != QMessageBox.StandardButton.Yes:
            return
        self.play_face_access_cue("camera_active")
        ok, detail = camera_acceptance_test(camera_index)
        self.play_face_access_cue("verified" if ok else "not_verified")
        if ok:
            QMessageBox.information(self, "Local camera readiness confirmed", detail)
        else:
            QMessageBox.warning(self, "Local camera readiness not confirmed", detail)

    def configure_access(self, preferred_method=None):
        if self.selected_access_method() and not self.session_unlocked:
            QMessageBox.information(self, "Unlock before changing access", "Verify the current room method before changing it. This prevents someone nearby from replacing your protected-room access method.")
            return
        choice = preferred_method if preferred_method in {"password", "windows_hello", "local_camera_face"} else ""
        if not choice:
            chooser = QMessageBox(self)
            chooser.setWindowTitle("Choose Spatial-room access")
            chooser.setText("Choose one access method. Arthur will never silently activate a camera or enrol a face.")
            chooser.setInformativeText("Windows Hello is verified by Windows with face or PIN. Password access stores only a salted verifier in Windows Credential Manager.")
            hello_button = chooser.addButton("Use Windows Hello only", QMessageBox.ButtonRole.ActionRole)
            face_button = chooser.addButton("Use local camera face access", QMessageBox.ButtonRole.ActionRole)
            password_button = chooser.addButton("Use local password only", QMessageBox.ButtonRole.ActionRole)
            chooser.addButton(QMessageBox.StandardButton.Cancel)
            chooser.exec()
            if chooser.clickedButton() == hello_button:
                choice = "windows_hello"
            elif chooser.clickedButton() == face_button:
                choice = "local_camera_face"
            elif chooser.clickedButton() == password_button:
                choice = "password"
            else:
                return

        if choice == "windows_hello":
            hello_ok, detail = windows_hello_availability()
            if not hello_ok:
                QMessageBox.warning(self, "Windows Hello is not ready", f"{detail}\n\nInstall the optional adapter, configure face or PIN in Windows Settings, then choose Windows Hello again.")
                return
            if spatial_password_is_configured() and QMessageBox.question(self, "Remove unused password?", "Selecting Windows Hello-only access removes Arthur’s existing Spatial-room password verifier. You will verify with Windows Hello to enter this room. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            clear_spatial_password()
            if self.selected_access_method() == "local_camera_face":
                delete_face_enrollment()
            self.config.setdefault("interaction", {})["spatial_room_access_method"] = "windows_hello"
            self.config["interaction"]["spatial_room_hello_enabled"] = True
            self.save_callback()
            QMessageBox.information(self, "Windows Hello selected", "Windows Hello is now required for the protected Spatial room. Arthur did not collect face data and no room password is required.")
            self.update_access_state()
            return

        if choice == "local_camera_face":
            face_ready, detail = face_dependency_status()
            if not face_ready:
                QMessageBox.warning(self, "Local camera face adapter unavailable", f"{detail}\n\nArthur did not install anything. Use the copy button to review and run the optional local requirement yourself, then retry.")
                return
            setup = FaceAccessSetupDialog(self.config.get("interaction", {}).get("spatial_room_face_camera_index", 0), self)
            if setup.exec() != QDialog.DialogCode.Accepted:
                return
            prior_method = self.selected_access_method()
            if prior_method == "password" and spatial_password_is_configured():
                choice = QMessageBox.question(self, "Replace password access?", "Local camera face access replaces the existing Spatial-room password method. The password verifier will be removed only after face enrolment succeeds. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if choice != QMessageBox.StandardButton.Yes:
                    return
            if prior_method == "local_camera_face" and face_is_configured():
                choice = QMessageBox.question(self, "Replace local face access?", "This will erase the current encrypted local face model after new enrolment succeeds. Continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if choice != QMessageBox.StandardButton.Yes:
                    return
            recovery_secret = setup.recovery.text()
            camera_index = setup.camera.value()
            setup.recovery.clear()
            setup.confirmation.clear()
            replacing_existing_face = prior_method == "local_camera_face" and face_is_configured()
            if replacing_existing_face:
                ok, detail = enroll_face(camera_index)
                if not ok:
                    QMessageBox.warning(self, "Local face enrolment was not completed", f"{detail}\n\nYour existing local face-access enrolment was retained.")
                    return
                recovery_ok, recovery_detail = set_face_recovery_secret(recovery_secret)
                if not recovery_ok:
                    QMessageBox.warning(self, "Recovery secret was not changed", f"{recovery_detail}\n\nThe new encrypted face model is active; your existing recovery secret remains in place.")
            else:
                ok, detail = set_face_recovery_secret(recovery_secret)
                if not ok:
                    QMessageBox.warning(self, "Recovery secret not saved", detail)
                    return
                ok, detail = enroll_face(camera_index)
                if not ok:
                    delete_face_enrollment()
                    QMessageBox.warning(self, "Local face enrolment was not completed", detail)
                    return
            if prior_method == "password":
                clear_spatial_password()
            self.config.setdefault("interaction", {})["spatial_room_access_method"] = "local_camera_face"
            self.config["interaction"]["spatial_room_face_camera_index"] = camera_index
            self.config["interaction"]["spatial_room_hello_enabled"] = False
            self.save_callback()
            QMessageBox.information(self, "Local camera face access selected", detail)
            self.update_access_state()
            return

        dialog = SpatialPasswordSetupDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        ok, detail = set_spatial_password(dialog.password.text())
        dialog.password.clear()
        dialog.confirmation.clear()
        if not ok:
            QMessageBox.warning(self, "Password not saved", detail)
            return
        if self.selected_access_method() == "local_camera_face":
            delete_face_enrollment()
        self.config.setdefault("interaction", {})["spatial_room_access_method"] = "password"
        self.config["interaction"]["spatial_room_hello_enabled"] = False
        self.save_callback()
        QMessageBox.information(self, "Password access selected", detail)
        self.update_access_state()
        if preferred_method == "password":
            self.unlock_room("Local password created and verified for this Arthur session.")

    def request_access(self):
        if self.session_unlocked:
            return True
        method = self.selected_access_method()
        if not method:
            installer_method = self.installer_selected_access_method()
            if installer_method:
                display_name = {
                    "password": "local password",
                    "windows_hello": "Windows Hello",
                    "local_camera_face": "local camera face access",
                }[installer_method]
                QMessageBox.information(self, "Complete Spatial Room setup", f"During installation, you selected {display_name} for the protected Spatial Room. Arthur will now guide you through the required local setup. Nothing is enabled until you complete it.")
                self.configure_access(preferred_method=installer_method)
                return self.session_unlocked
            QMessageBox.information(self, "Choose access first", "Choose local password, Windows Hello, or experimental local camera face access before opening this protected room.")
            return False
        if method == "windows_hello":
            hello_ok, detail = windows_hello_availability()
            if not hello_ok:
                QMessageBox.warning(self, "Windows Hello required", f"{detail}\n\nThis room is configured for Windows Hello only. Configure Windows Hello and retry; Arthur will not substitute a password.")
                return False
            ok, detail = verify_windows_hello()
            if not ok:
                QMessageBox.warning(self, "Windows Hello did not verify", detail)
                return False
            self.unlock_room(detail)
            return True
        if method == "local_camera_face":
            if not face_is_configured():
                QMessageBox.warning(self, "Local face enrolment required", "This room is configured for local camera face access, but its encrypted local model is unavailable. Use Recover / erase local face access, then choose and enrol an access method again.")
                return False
            remaining, _attempts = face_lockout_status()
            if remaining:
                QMessageBox.warning(self, "Local face access temporarily locked", f"Repeated non-matches have paused local camera face access for {remaining} more seconds. Wait for the visible cooldown to finish, or use Recover / erase local face access with your recovery secret. No frame was retained.")
                self.update_access_state()
                return False
            camera_index = self.config.get("interaction", {}).get("spatial_room_face_camera_index", 0)
            self.play_face_access_cue("camera_active")
            ok, detail = verify_face(camera_index)
            if not ok:
                if detail.startswith("Local camera face check did not verify"):
                    attempts, cooldown = register_face_failure()
                    self.play_face_access_cue("not_verified")
                    if cooldown:
                        detail = f"{detail}\n\nArthur has temporarily locked local face access for {cooldown} seconds after {attempts} non-matches. Wait for the cooldown or use Recover / erase local face access with your recovery secret."
                    else:
                        detail = f"{detail}\n\nAttempt {attempts} of {3}; a short cooldown begins after the next non-match."
                    self.update_access_state()
                QMessageBox.warning(self, "Local camera face check did not verify", detail)
                return False
            clear_face_failures()
            self.play_face_access_cue("verified")
            self.unlock_room(detail)
            return True
        if method != "password" or not spatial_password_is_configured():
            QMessageBox.warning(self, "Password setup incomplete", "This room is marked for local password access, but no password verifier is stored. Choose room access method to create a new local password before opening the room.")
            return False
        dialog = SpatialPasswordDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        verified = verify_spatial_password(dialog.password.text())
        dialog.password.clear()
        if not verified:
            QMessageBox.warning(self, "Access not verified", "That password did not unlock the Spatial room. Try again.")
            return False
        self.unlock_room("Local password verified for this session.")
        return True

    def unlock_room(self, detail):
        self.session_unlocked = True
        self.access_status.setText(f"Unlocked for this Arthur session. {detail}")
        self.update_access_state()

    def lock_room(self):
        self.stop_local_gestures()
        self.session_unlocked = False
        self.access_status.setText("Locked. Touch, air gestures, and layout controls are unavailable until you verify local access again.")
        self.update_access_state()

    def update_access_state(self):
        method = self.selected_access_method()
        configured = (method == "windows_hello") or (method == "password" and spatial_password_is_configured()) or (method == "local_camera_face" and face_is_configured())
        remaining, attempts = face_lockout_status()
        access_available = method != "local_camera_face" or not remaining
        self.access_unlock_button.setEnabled(configured and access_available and not self.session_unlocked)
        self.access_lock_button.setEnabled(self.session_unlocked)
        self.touch_controls.setEnabled(self.session_unlocked)
        self.air_controls.setEnabled(self.session_unlocked)
        if method == "windows_hello":
            self.access_method_detail.setText("Windows Hello only. Arthur does not request or retain a Spatial-room password.")
        elif method == "local_camera_face":
            self.access_method_detail.setText("Experimental local camera face access only. A recovery secret can erase the encrypted local model; Arthur stores no raw camera image or video.")
        elif method == "password":
            self.access_method_detail.setText("Local password only. Windows Hello is not used for this room.")
        elif self.installer_selected_access_method() == "password":
            self.access_method_detail.setText("Local password was selected during installation but still needs to be created. Open the Spatial workspace to complete setup.")
        elif self.installer_selected_access_method() == "windows_hello":
            self.access_method_detail.setText("Windows Hello was selected during installation but still needs Windows verification. Open the Spatial workspace to complete setup.")
        elif self.installer_selected_access_method() == "local_camera_face":
            self.access_method_detail.setText("Local camera face access was selected during installation but still needs visible local enrolment. Open the Spatial workspace to complete setup.")
        else:
            self.access_method_detail.setText("No method selected. Choose local password, Windows Hello, or local camera face access.")
        self.face_recovery_button.setVisible(method == "local_camera_face")
        if remaining:
            self.face_lockout_label.setText(f"Temporarily locked after {attempts} non-matches. Try local face access again in about {remaining} seconds, or use the recovery secret to erase the local model.")
        elif attempts:
            self.face_lockout_label.setText(f"{attempts} local face non-match{'es' if attempts != 1 else ''} recorded for this short safeguard window. No frame was retained.")
        else:
            self.face_lockout_label.setText("No recent local face-check failures. Arthur stores no failed frames; only a short local counter/timer is used if a non-match occurs.")
        if not configured and not self.session_unlocked:
            self.access_status.setText("Locked for this session. Choose one access method before entering this room.")
        elif remaining and not self.session_unlocked:
            self.access_status.setText(f"Locked for this session. Local face access is temporarily paused for about {remaining} more seconds after repeated non-matches.")

    def selected_access_method(self):
        method = self.config.get("interaction", {}).get("spatial_room_access_method", "")
        return method if method in {"password", "windows_hello", "local_camera_face"} else ""

    def installer_selected_access_method(self):
        """Return only the local first-run protection intent written by the installer."""
        method = self.config.get("interaction", {}).get("installer_spatial_room_protection", "")
        return method if method in {"password", "windows_hello", "local_camera_face"} else ""

    def recover_face_access(self):
        if self.selected_access_method() != "local_camera_face":
            QMessageBox.information(self, "Face recovery unavailable", "Local camera face access is not the selected room method.")
            return
        dialog = FaceRecoveryDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        verified = verify_face_recovery_secret(dialog.recovery.text())
        dialog.recovery.clear()
        if not verified:
            QMessageBox.warning(self, "Recovery secret did not verify", "The encrypted local face model was not erased.")
            return
        delete_face_enrollment()
        self.config.setdefault("interaction", {})["spatial_room_access_method"] = ""
        self.config["interaction"]["spatial_room_hello_enabled"] = False
        self.session_unlocked = False
        self.save_callback()
        QMessageBox.information(self, "Local face access erased", "The encrypted local face model, encryption key, and recovery-secret verifier were erased. Choose a new room access method before entering the Spatial room.")
        self.update_access_state()

    def event(self, event):
        if not self.session_unlocked:
            return super().event(event)
        if event.type() == QEvent.Type.Gesture:
            swipe = event.gesture(Qt.GestureType.SwipeGesture)
            pinch = event.gesture(Qt.GestureType.PinchGesture)
            if swipe:
                direction = swipe.horizontalDirection()
                if direction == QSwipeGesture.SwipeDirection.Left:
                    self.move_selection(1)
                elif direction == QSwipeGesture.SwipeDirection.Right:
                    self.move_selection(-1)
                return True
            if pinch:
                scale = pinch.totalScaleFactor()
                self.zoom.setValue(max(self.zoom.minimum(), min(self.zoom.maximum(), int(self.zoom.value() * scale))))
                return True
        return super().event(event)

    def update_scale(self, value):
        if not self.session_unlocked:
            return
        font = self.card_list.font()
        font.setPointSize(max(9, round(10 * value / 100)))
        self.card_list.setFont(font)
        self.gesture_status_label.setText(f"Canvas scale is {value}%. Pinch gestures and the slider affect only this workspace.")

    def move_selection(self, delta):
        if not self.session_unlocked:
            return
        if not self.card_list.count():
            return
        current = self.card_list.currentRow()
        current = 0 if current < 0 else current
        target = (current + delta) % self.card_list.count()
        self.card_list.setCurrentRow(target)
        self.gesture_status_label.setText(f"Selected Arthur card: {self.card_list.item(target).text()}.")

    def request_discard(self):
        if not self.session_unlocked:
            return
        current = self.card_list.currentRow()
        if current < 0:
            QMessageBox.information(self, "Select a card", "Select one Arthur workspace card before asking to discard it.")
            return
        label = self.card_list.item(current).text()
        choice = QMessageBox.question(self, "Discard Arthur card?", f"Remove “{label}” from this workspace? This affects only the current layout and can be undone during this session.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            self.last_removed = (current, self.card_list.takeItem(current).text())
            self.undo_discard.setEnabled(True)
            self.gesture_status_label.setText("Card removed from the current Arthur workspace. Undo remains available.")

    def undo_last_discard(self):
        if not self.last_removed:
            return
        index, label = self.last_removed
        self.card_list.insertItem(min(index, self.card_list.count()), label)
        self.card_list.setCurrentRow(min(index, self.card_list.count() - 1))
        self.last_removed = None
        self.undo_discard.setEnabled(False)
        self.gesture_status_label.setText("The discarded Arthur card was restored.")

    def toggle_air_gestures(self):
        if not self.session_unlocked:
            QMessageBox.information(self, "Protected room locked", "Unlock the Spatial room with your local password or configured Windows Hello method before enabling local air gestures.")
            return
        if self.listener and self.listener.running:
            self.stop_local_gestures()
            return
        if not self.air_gestures.isChecked():
            QMessageBox.information(self, "Consent required", "Confirm that you want local camera-based hand tracking before Arthur can request access to the selected camera.")
            return
        choice = QMessageBox.question(self, "Enable local air gestures", "Arthur will open only the selected local camera and process hand landmarks in memory. It will not save video, images, landmarks, or biometric templates. Gestures affect Arthur’s workspace only, and any consequential PC action still needs its own confirmation. Enable now?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if choice != QMessageBox.StandardButton.Yes:
            return
        interaction = self.config.setdefault("interaction", {})
        interaction["air_gestures_approved"] = True
        interaction["gesture_camera_index"] = self.camera_choice.value()
        self.save_callback()
        self.listener = GestureListener(lambda event: self.gesture_detected.emit(event), lambda status: self.gesture_status.emit(status), self.camera_choice.value())
        ok, detail = self.listener.start()
        self.set_gesture_status(detail)
        self.gesture_button.setText("Stop local air gestures" if ok else "Enable local air gestures")

    def handle_gesture(self, event):
        if not self.session_unlocked:
            return
        if not isinstance(event, GestureEvent):
            return
        if event.name == "swipe_left":
            self.move_selection(1)
        elif event.name == "swipe_right":
            self.move_selection(-1)
        elif event.name == "pinch":
            adjustment = 10 if event.value > 0.45 else -7
            self.zoom.setValue(max(self.zoom.minimum(), min(self.zoom.maximum(), self.zoom.value() + adjustment)))
        elif event.name == "discard_request":
            self.request_discard()

    def set_gesture_status(self, detail):
        self.gesture_status_label.setText(detail)

    def stop_local_gestures(self):
        if self.listener:
            self.listener.stop()
        self.listener = None
        self.gesture_button.setText("Enable local air gestures")


class SymptomSupportPage(QWidget):
    """Guided care-seeking support; explicitly not disease diagnosis."""

    def __init__(self, voice_runtime, parent=None):
        super().__init__(parent)
        self.voice_runtime = voice_runtime
        self.current_guidance = None
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Symptom support", "Describe how you feel and Arthur will provide cautious health information and care-seeking prompts. It cannot diagnose diseases or replace a clinician."))
        warning = QLabel("If there is severe chest pain, difficulty breathing, stroke-like symptoms, severe allergic reaction, loss of consciousness, severe bleeding, or an immediate safety concern, contact local emergency services now. Do not wait for Arthur to respond.")
        warning.setObjectName("safetyBoundary")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        group = QGroupBox("Private symptom note — not saved unless you choose to add it to Private notes")
        form = QVBoxLayout(group)
        self.symptoms = QTextEdit()
        self.symptoms.setPlaceholderText("For example: what you feel, when it began, whether it is worsening, and anything you think is relevant. Do not enter passwords, account details, or anything you do not wish to share.")
        self.symptoms.setMinimumHeight(150)
        form.addWidget(self.symptoms)
        actions = QHBoxLayout()
        prepare = QPushButton("Prepare cautious guidance")
        prepare.setObjectName("primaryButton")
        prepare.clicked.connect(self.prepare_guidance)
        self.speak = QPushButton("Speak guidance locally")
        self.speak.setEnabled(False)
        self.speak.clicked.connect(self.speak_guidance)
        actions.addWidget(prepare)
        actions.addWidget(self.speak)
        actions.addStretch()
        form.addLayout(actions)
        layout.addWidget(group)
        self.result = QLabel("Arthur is waiting for your voluntary description. It will not label a disease or make a medical decision.")
        self.result.setObjectName("muted")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)

        references = QGroupBox("Learn about a condition — source-linked, not a diagnosis")
        reference_form = QVBoxLayout(references)
        reference_prompt = QLabel("Enter the name of a condition you want to understand. Arthur will offer a reviewed public-health article; it will not infer a disease from your symptom note.")
        reference_prompt.setWordWrap(True)
        reference_form.addWidget(reference_prompt)
        lookup_row = QHBoxLayout()
        self.condition_query = QLineEdit()
        self.condition_query.setPlaceholderText("For example: asthma, malaria, diabetes, or migraine")
        self.condition_lookup_button = QPushButton("Find reviewed source")
        self.condition_lookup_button.clicked.connect(self.find_condition_info)
        lookup_row.addWidget(self.condition_query, 1)
        lookup_row.addWidget(self.condition_lookup_button)
        reference_form.addLayout(lookup_row)
        self.condition_reference = QLabel("Arthur has not selected a condition article. Opening any source link is your choice.")
        self.condition_reference.setObjectName("muted")
        self.condition_reference.setWordWrap(True)
        self.condition_reference.setTextFormat(Qt.TextFormat.RichText)
        self.condition_reference.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.condition_reference.setOpenExternalLinks(True)
        reference_form.addWidget(self.condition_reference)

        excerpt_prompt = QLabel("To get a short explanation, paste an article passage and its direct MedlinePlus, NHS, WHO, or CDC URL. Arthur summarizes only pasted text; it does not open, download, or send the article.")
        excerpt_prompt.setWordWrap(True)
        reference_form.addWidget(excerpt_prompt)
        self.article_source_url = QLineEdit()
        self.article_source_url.setPlaceholderText("https://medlineplus.gov/... or another supported public-health article URL")
        reference_form.addWidget(self.article_source_url)
        self.article_excerpt = QTextEdit()
        self.article_excerpt.setPlaceholderText("Paste a paragraph from the source article here for a short local reading note.")
        self.article_excerpt.setMinimumHeight(110)
        reference_form.addWidget(self.article_excerpt)
        self.article_summary_button = QPushButton("Create short local reading note")
        self.article_summary_button.clicked.connect(self.create_article_note)
        reference_form.addWidget(self.article_summary_button)
        self.article_note = QLabel("No article text has been summarized. Arthur will keep the source link visible and will not diagnose or recommend treatment.")
        self.article_note.setObjectName("muted")
        self.article_note.setWordWrap(True)
        reference_form.addWidget(self.article_note)
        layout.addWidget(references)
        layout.addStretch()

    def prepare_guidance(self):
        self.current_guidance = prepare_symptom_guidance(self.symptoms.toPlainText())
        guidance = self.current_guidance
        self.result.setText(f"{guidance.heading}\n\n{guidance.summary}\n\nNext step: {guidance.next_step}")
        self.speak.setEnabled(True)
        if guidance.emergency:
            QMessageBox.warning(self, "Seek emergency help", guidance.next_step)

    def speak_guidance(self):
        if self.current_guidance:
            self.voice_runtime.speak(f"{self.current_guidance.heading}. {self.current_guidance.next_step}")

    def find_condition_info(self):
        reference = find_condition_reference(self.condition_query.text())
        if not reference.source_url:
            self.condition_reference.setText(reference.notice)
            return
        self.condition_reference.setText(
            f"<b>{reference.heading}</b> · {reference.source_name}<br>"
            f"{reference.notice}<br>"
            f"<a href=\"{reference.source_url}\">Open the reviewed source article</a>"
        )

    def create_article_note(self):
        note = summarise_article_excerpt(self.article_source_url.text(), self.article_excerpt.toPlainText())
        if not note.summary:
            self.article_note.setText(note.notice)
            return
        self.article_note.setText(
            f"<b>Short local reading note · {note.source_name}</b><br>{note.summary}<br><br>{note.notice}"
        )


class VoiceSignalPage(QWidget):
    """A local visual response surface; it displays level only and never records audio."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.level = 0.08
        self.active = False
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Voice signal", "A local command-mode visualizer. It reacts to transient microphone level only while listening is enabled; it does not record or upload sound."))
        self.signal = QFrame()
        self.signal.setObjectName("voiceSignal")
        signal_layout = QVBoxLayout(self.signal)
        signal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orb = QLabel("ARTHUR\nREADY")
        self.orb.setObjectName("voiceOrb")
        self.orb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signal_layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignCenter)
        self.readout = QLabel("STANDBY • Start a command or explicitly enable local listening to animate this local signal.")
        self.readout.setObjectName("muted")
        self.readout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.readout.setWordWrap(True)
        signal_layout.addWidget(self.readout)
        layout.addWidget(self.signal, 1)
        boundary = QLabel("This visualizer receives an amplitude number only. It keeps no raw audio, waveform recording, or cloud connection.")
        boundary.setObjectName("safetyBoundary")
        boundary.setWordWrap(True)
        layout.addWidget(boundary)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(90)

    def activate(self, message="Command session active"):
        self.active = True
        self.orb.setText("ARTHUR\nACTIVE")
        self.readout.setText(f"{message} • Visual signal is local and transient.")

    def set_level(self, level):
        self.level = max(0.0, min(float(level), 1.0))
        if self.level > 0.02:
            self.active = True
            self.orb.setText("ARTHUR\nLISTENING")
            self.readout.setText("LOCAL LISTENING • Microphone level is visualized, never recorded.")

    def tick(self):
        if not self.active:
            return
        span = 150 + int(min(1.0, self.level * 7 + 0.12) * 45)
        self.orb.setMinimumSize(span, span)
        self.orb.setMaximumSize(span, span)
        self.level *= 0.78


class VoiceStudioPage(QWidget):
    wake_word_detected = Signal(str)
    audio_level = Signal(float)

    def __init__(self, config, save_callback, voice_runtime, theme_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self.voice_runtime = voice_runtime
        self.theme_callback = theme_callback
        self.listener = None
        self.wake_word_detected.connect(self.on_wake_word_detected)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Voice studio", "Test local speech, inspect wake-word readiness, and explicitly choose whether Arthur may listen."))
        signal = QFrame()
        signal.setObjectName("voiceSignal")
        signal_layout = QVBoxLayout(signal)
        orb = QLabel("ARTHUR\nVOICE LINK")
        orb.setObjectName("voiceOrb")
        orb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signal_layout.addWidget(orb)
        self.status = QLabel("Standby. Arthur cannot listen until a verified model is selected and you explicitly enable this local listener.")
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        signal_layout.addWidget(self.status)
        layout.addWidget(signal)

        group = QGroupBox("Expression controls")
        form = QFormLayout(group)
        self.voice = QComboBox()
        self.voice.addItems(["Refined British (provider dependent)", "Calm neutral", "Direct concise", "Warm conversational"])
        self.voice.setCurrentText(config.get("appearance", {}).get("voice_style", "Refined British (provider dependent)"))
        self.mode = QComboBox()
        self.mode.addItems(["Voice first", "Voice + transcript", "Transcript only"])
        self.mode.setCurrentText("Voice first" if config.get("privacy", {}).get("spoken_only", True) else "Voice + transcript")
        self.arrival_greeting = QCheckBox("Speak a brief local greeting when Arthur opens or returns from the tray")
        self.arrival_greeting.setChecked(config.get("voice", {}).get("arrival_greeting_enabled", False))
        self.first_interaction_greeting = QCheckBox("Introduce Arthur after first-run setup")
        self.first_interaction_greeting.setChecked(config.get("voice", {}).get("first_interaction_greeting_enabled", True))
        self.wake_greeting = QCheckBox("Acknowledge a deliberately detected local wake word")
        self.wake_greeting.setChecked(config.get("voice", {}).get("wake_greeting_enabled", True))
        self.greeting_script_kind = QComboBox()
        self.greeting_script_kind.addItem("Opening greeting", "opening")
        self.greeting_script_kind.addItem("First interaction", "introduction")
        self.greeting_script_kind.addItem("Wake acknowledgement", "wake")
        self._greeting_scripts = dict(DEFAULT_GREETING_SCRIPTS)
        self._greeting_scripts.update(config.get("voice", {}).get("greeting_scripts", {}))
        self.greeting_script = QTextEdit()
        self.greeting_script.setAcceptRichText(False)
        self.greeting_script.setMaximumHeight(76)
        self.greeting_script.setPlaceholderText("Use {recipient} and {time_of_day}; plain local text only.")
        self.greeting_script.setPlainText(self._greeting_scripts["opening"])
        self.greeting_script_kind.currentIndexChanged.connect(self.change_greeting_script_kind)
        self.restore_greeting_script_button = QPushButton("Restore selected safe default")
        self.restore_greeting_script_button.clicked.connect(self.restore_selected_greeting_script)
        self.time_of_day_greetings = QCheckBox("Use morning, afternoon, or evening wording when Arthur is opened or deliberately awakened")
        self.time_of_day_greetings.setChecked(config.get("voice", {}).get("time_of_day_greetings_enabled", False))
        self.do_not_disturb = QCheckBox("Suppress non-essential greetings during local Do Not Disturb hours")
        self.do_not_disturb.setChecked(config.get("voice", {}).get("do_not_disturb_enabled", False))
        self.do_not_disturb_start = QTimeEdit()
        self.do_not_disturb_start.setDisplayFormat("HH:mm")
        self.do_not_disturb_start.setTime(QTime.fromString(config.get("voice", {}).get("do_not_disturb_start", "22:00"), "HH:mm"))
        self.do_not_disturb_end = QTimeEdit()
        self.do_not_disturb_end.setDisplayFormat("HH:mm")
        self.do_not_disturb_end.setTime(QTime.fromString(config.get("voice", {}).get("do_not_disturb_end", "07:00"), "HH:mm"))
        self.quiet_hours_status = QLabel()
        self.quiet_hours_status.setObjectName("muted")
        self.quiet_hours_status.setWordWrap(True)
        self.update_quiet_hours_status()
        self.do_not_disturb.toggled.connect(lambda _checked: self.update_quiet_hours_status())
        self.do_not_disturb_start.timeChanged.connect(lambda _time: self.update_quiet_hours_status())
        self.do_not_disturb_end.timeChanged.connect(lambda _time: self.update_quiet_hours_status())
        self.workspace_colour = QComboBox()
        self.workspace_colour.addItems(["Cobalt", "Tide", "Amber"])
        self.workspace_colour.setCurrentText(config.get("appearance", {}).get("color_mode", "Cobalt"))
        self.local_voice = QComboBox()
        self.local_voice.addItem("Windows default voice", "")
        saved_voice = config.get("voice", {}).get("local_voice_id", "")
        for voice_id, voice_name in self.voice_runtime.available_voices():
            self.local_voice.addItem(voice_name, voice_id)
            if voice_id == saved_voice:
                self.local_voice.setCurrentIndex(self.local_voice.count() - 1)
        self.rate = QSpinBox()
        self.rate.setRange(100, 260)
        self.rate.setSuffix(" words/min")
        self.rate.setValue(config.get("voice", {}).get("rate", 175))
        self.volume = QSpinBox()
        self.volume.setRange(0, 100)
        self.volume.setSuffix(" %")
        self.volume.setValue(config.get("voice", {}).get("volume", 100))
        self.pitch = QSpinBox()
        self.pitch.setRange(-10, 10)
        self.pitch.setValue(config.get("voice", {}).get("pitch", 0))
        self.pitch.setToolTip("Best effort only: the installed Windows voice may not expose pitch through its local driver.")
        form.addRow("Preferred voice style:", self.voice)
        form.addRow("Workspace colour (all pages):", self.workspace_colour)
        form.addRow("Installed local voice:", self.local_voice)
        form.addRow("Speech rate:", self.rate)
        form.addRow("Volume:", self.volume)
        form.addRow("Pitch preference:", self.pitch)
        form.addRow("Reply format:", self.mode)
        form.addRow("Arrival cue:", self.arrival_greeting)
        form.addRow("First interaction:", self.first_interaction_greeting)
        form.addRow("Wake acknowledgement:", self.wake_greeting)
        layout.addWidget(group)

        greeting_group = QGroupBox("Local greeting wording & quiet hours")
        greeting_form = QFormLayout(greeting_group)
        greeting_form.addRow("Edit greeting:", self.greeting_script_kind)
        greeting_form.addRow("Plain local script:", self.greeting_script)
        greeting_form.addRow("Script safety:", self.restore_greeting_script_button)
        greeting_form.addRow("Time-of-day wording:", self.time_of_day_greetings)
        greeting_form.addRow("Do Not Disturb:", self.do_not_disturb)
        greeting_form.addRow("Quiet hours start:", self.do_not_disturb_start)
        greeting_form.addRow("Quiet hours end:", self.do_not_disturb_end)
        greeting_form.addRow("Schedule state:", self.quiet_hours_status)
        layout.addWidget(greeting_group)

        diagnostics = QGroupBox("Local voice diagnostics")
        diagnostic_layout = QFormLayout(diagnostics)
        self.model_path = QLineEdit(config.get("voice", {}).get("wake_word_model", ""))
        self.model_path.setPlaceholderText("Select an approved local .onnx or .tflite wake-word model")
        browse = QPushButton("Choose model")
        browse.clicked.connect(self.choose_model)
        model_row = QHBoxLayout()
        model_row.addWidget(self.model_path, 1)
        model_row.addWidget(browse)
        model_holder = QWidget()
        model_holder.setLayout(model_row)
        diagnostic_layout.addRow("Wake-word model:", model_holder)
        route_id = str(config.get("voice", {}).get("speech_recognition_route", ""))
        route = SPEECH_RECOGNITION_ROUTES.get(route_id)
        self.speech_route_status = QLabel(
            f"Selected route: {route['label']}. {route['detail']}" if route else "Speech-recognition route is not selected. Complete first-run setup before Arthur can understand spoken commands."
        )
        self.speech_route_status.setObjectName("muted")
        self.speech_route_status.setWordWrap(True)
        diagnostic_layout.addRow("Spoken commands:", self.speech_route_status)
        self.microphone = QComboBox()
        self.refresh_microphone_devices()
        microphone_row = QHBoxLayout()
        microphone_row.addWidget(self.microphone, 1)
        refresh_microphones = QPushButton("Refresh inputs")
        refresh_microphones.clicked.connect(self.refresh_microphone_devices)
        microphone_row.addWidget(refresh_microphones)
        microphone_holder = QWidget()
        microphone_holder.setLayout(microphone_row)
        diagnostic_layout.addRow("Local microphone:", microphone_holder)
        actions = QHBoxLayout()
        speech_test = QPushButton("Test Arthur's voice")
        speech_test.clicked.connect(self.test_speech)
        self.introduction_test_button = QPushButton("Replay Arthur's introduction")
        self.introduction_test_button.clicked.connect(self.replay_introduction)
        microphone_test = QPushButton("Test microphone activity (3 sec)")
        microphone_test.clicked.connect(self.test_microphone_activity)
        microphone_check = QPushButton("Check microphone readiness")
        microphone_check.clicked.connect(self.check_microphone_readiness)
        wake_check = QPushButton("Check wake-word readiness")
        wake_check.clicked.connect(self.check_wake_word)
        actions.addWidget(speech_test)
        actions.addWidget(self.introduction_test_button)
        actions.addWidget(microphone_test)
        actions.addWidget(microphone_check)
        actions.addWidget(wake_check)
        action_holder = QWidget()
        action_holder.setLayout(actions)
        diagnostic_layout.addRow("Diagnostics:", action_holder)
        self.listener_button = QPushButton("Enable local wake-word listener")
        self.listener_button.setObjectName("secondaryButton")
        self.listener_button.clicked.connect(self.toggle_listener)
        diagnostic_layout.addRow("Listening:", self.listener_button)
        microphone_privacy = QPushButton("Open Windows microphone privacy settings")
        microphone_privacy.clicked.connect(self.open_microphone_privacy_settings)
        diagnostic_layout.addRow("Windows permission:", microphone_privacy)
        layout.addWidget(diagnostics)

        save = QPushButton("Save voice preference")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save)
        layout.addWidget(save)
        layout.addStretch()

    def choose_model(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select wake-word model",
            str(BASE_DIR),
            "Wake-word model (*.onnx *.tflite)",
        )
        if path:
            self.model_path.setText(path)
            self.check_wake_word()

    def test_speech(self):
        self.apply_voice_preferences()
        result = self.voice_runtime.speak("Arthur voice link confirmed. Local speech is available.")
        self.status.setText(f"{result.headline}. {result.detail}")
        if not result.ready:
            QMessageBox.warning(self, "Voice test unavailable", f"{result.headline}\n\n{result.detail}")

    def introduction_text(self):
        preview_config = json.loads(json.dumps(self.config))
        preview_config.setdefault("voice", {})["greeting_scripts"] = dict(self._greeting_scripts)
        return render_greeting_script(preview_config, "introduction")

    def change_greeting_script_kind(self):
        previous = getattr(self, "_selected_greeting_kind", "opening")
        self._greeting_scripts[previous] = self.greeting_script.toPlainText().strip()[:240] or DEFAULT_GREETING_SCRIPTS[previous]
        selected = str(self.greeting_script_kind.currentData())
        self._selected_greeting_kind = selected
        self.greeting_script.blockSignals(True)
        self.greeting_script.setPlainText(self._greeting_scripts.get(selected, DEFAULT_GREETING_SCRIPTS[selected]))
        self.greeting_script.blockSignals(False)

    def restore_selected_greeting_script(self):
        selected = str(self.greeting_script_kind.currentData())
        self._greeting_scripts[selected] = DEFAULT_GREETING_SCRIPTS[selected]
        self.greeting_script.setPlainText(DEFAULT_GREETING_SCRIPTS[selected])
        self.status.setText("Selected greeting restored to Arthur's safe local default. Save to keep it.")

    def update_quiet_hours_status(self):
        start = self.do_not_disturb_start.time().toString("HH:mm")
        end = self.do_not_disturb_end.time().toString("HH:mm")
        if not self.do_not_disturb.isChecked():
            self.quiet_hours_status.setText("Do Not Disturb is off. Automatic greetings stay governed by their individual voice preferences.")
            return
        active = is_time_in_window(datetime.now().strftime("%H:%M"), start, end)
        suffix = "It is active now; an explicit Replay action still remains your choice." if active else "It is configured but not active now."
        self.quiet_hours_status.setText(f"Local quiet hours: {start}–{end}. {suffix}")

    def replay_introduction(self):
        """Speak only after the user explicitly presses the replay control."""
        self.apply_voice_preferences()
        result = self.voice_runtime.speak(self.introduction_text())
        self.status.setText(f"{result.headline}. {result.detail}")
        if not result.ready:
            QMessageBox.warning(self, "Voice test unavailable", f"{result.headline}\n\n{result.detail}")

    def test_microphone_activity(self):
        consent = QMessageBox.question(
            self,
            "Test local microphone activity?",
            "Arthur will open the selected microphone for about 3 seconds to measure sound level only. It will not record, transcribe, retain, or upload speech. Start this one-time test?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if consent != QMessageBox.StandardButton.Yes:
            self.status.setText("Microphone activity test cancelled. Arthur did not open the microphone.")
            return
        self.status.setText("Testing local microphone activity for about 3 seconds. Arthur is not recording or transcribing speech.")
        QApplication.processEvents()
        result = test_microphone_activity(device=self.selected_microphone())
        self.status.setText(f"{result.headline}. {result.detail}")
        if not result.ready:
            QMessageBox.warning(self, "Microphone activity test", f"{result.headline}\n\n{result.detail}")

    def check_wake_word(self):
        result = diagnose_wake_word(self.model_path.text())
        self.status.setText(f"{result.headline}. {result.detail}")
        return result

    def refresh_microphone_devices(self):
        saved = self.config.get("voice", {}).get("input_device")
        self.microphone.clear()
        self.microphone.addItem("Windows default microphone", None)
        for index, name in available_input_devices():
            self.microphone.addItem(f"{index}: {name}", index)
            if saved == index:
                self.microphone.setCurrentIndex(self.microphone.count() - 1)

    def selected_microphone(self):
        value = self.microphone.currentData()
        return int(value) if isinstance(value, int) else None

    def check_microphone_readiness(self):
        result = microphone_readiness(device=self.selected_microphone())
        self.status.setText(f"{result.headline}. {result.detail}")
        if not result.ready:
            QMessageBox.warning(self, "Microphone readiness", f"{result.headline}\n\n{result.detail}")
        return result

    def open_microphone_privacy_settings(self):
        if not QDesktopServices.openUrl(QUrl("ms-settings:privacy-microphone")):
            QMessageBox.information(self, "Windows microphone privacy", "Open Windows Settings > Privacy & security > Microphone, then enable microphone access and allow desktop apps to use your microphone.")

    def toggle_listener(self):
        if self.listener is not None and self.listener.running:
            self.listener.stop()
            self.listener = None
            self.config.setdefault("voice", {})["wake_word_listener_approved"] = False
            self.config.setdefault("privacy", {})["wake_word_background_enabled"] = False
            self.listener_button.setText("Enable local wake-word listener")
            self.status.setText("Wake-word listening stopped. Arthur remains on standby.")
            self.save_callback()
            return

        result = self.check_wake_word()
        if not result.ready:
            QMessageBox.warning(self, "Wake-word not ready", f"{result.headline}\n\n{result.detail}")
            return
        microphone = self.check_microphone_readiness()
        if not microphone.ready:
            return
        consent = QMessageBox.question(
            self,
            "Enable local wake-word listening?",
            "Arthur will open the selected local microphone only while this session is active. Audio is not sent to a cloud provider. Enable listening now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if consent != QMessageBox.StandardButton.Yes:
            return
        try:
            self.listener = WakeWordListener(model_path=self.model_path.text(), wake_word=self.config.get("profile", {}).get("wake_word", "Arthur"), input_device=self.selected_microphone())
            self.listener.on_detected = self.wake_word_detected.emit
            self.listener.on_audio_level = self.audio_level.emit
            self.listener.start()
            self.config.setdefault("voice", {})["wake_word_listener_approved"] = True
            self.config.setdefault("privacy", {})["wake_word_background_enabled"] = True
            self.listener_button.setText("Stop local wake-word listener")
            self.status.setText("Listening locally. Say Arthur near the selected microphone. Use Stop at any time to pause it.")
            self.save_callback()
        except Exception as exc:
            self.listener = None
            self.status.setText(f"Wake-word listener could not start: {exc}")
            QMessageBox.warning(self, "Wake-word listener unavailable", str(exc))

    def on_wake_word_detected(self, wake_word):
        route_id = str(self.config.get("voice", {}).get("speech_recognition_route", ""))
        route = SPEECH_RECOGNITION_ROUTES.get(route_id)
        route_message = route["label"] if route else "a selected speech-recognition route"
        self.status.setText(f"Wake word detected: {wake_word}. Arthur is ready. Spoken command understanding still requires {route_message} to be separately ready; wake-word detection alone does not transcribe or perform a command.")
        if self.config.get("privacy", {}).get("spoken_only", True) and self.config.get("voice", {}).get("wake_greeting_enabled", True):
            if greeting_is_quiet(self.config):
                self.status.setText("Wake word detected. Local Do Not Disturb is active, so Arthur will wait silently for your reviewed command.")
                return
            self.apply_voice_preferences()
            self.voice_runtime.speak(render_greeting_script(self.config, "wake"))

    def stop_listener(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def pause_listener(self, persist=True):
        """Stop local listening immediately without changing the selected model path."""
        was_running = self.listener is not None and self.listener.running
        self.stop_listener()
        if persist:
            self.config.setdefault("voice", {})["wake_word_listener_approved"] = False
            self.config.setdefault("privacy", {})["wake_word_background_enabled"] = False
            self.listener_button.setText("Enable local wake-word listener")
            self.status.setText("Wake-word listening paused. Arthur is on standby until you explicitly enable it again.")
            self.save_callback()
        return was_running

    def save(self):
        self.config.setdefault("appearance", {})["voice_style"] = self.voice.currentText()
        self.config["appearance"]["color_mode"] = self.workspace_colour.currentText()
        self.config.setdefault("privacy", {})["spoken_only"] = self.mode.currentText() == "Voice first"
        voice = self.config.setdefault("voice", {})
        voice["wake_word_model"] = self.model_path.text().strip()
        voice["input_device"] = self.selected_microphone()
        voice["arrival_greeting_enabled"] = self.arrival_greeting.isChecked()
        voice["first_interaction_greeting_enabled"] = self.first_interaction_greeting.isChecked()
        voice["wake_greeting_enabled"] = self.wake_greeting.isChecked()
        selected = getattr(self, "_selected_greeting_kind", "opening")
        self._greeting_scripts[selected] = self.greeting_script.toPlainText().strip()[:240] or DEFAULT_GREETING_SCRIPTS[selected]
        voice["greeting_scripts"] = dict(self._greeting_scripts)
        voice["time_of_day_greetings_enabled"] = self.time_of_day_greetings.isChecked()
        voice["do_not_disturb_enabled"] = self.do_not_disturb.isChecked()
        voice["do_not_disturb_start"] = self.do_not_disturb_start.time().toString("HH:mm")
        voice["do_not_disturb_end"] = self.do_not_disturb_end.time().toString("HH:mm")
        voice["local_voice_id"] = str(self.local_voice.currentData() or "")
        voice["rate"] = self.rate.value()
        voice["volume"] = self.volume.value()
        voice["pitch"] = self.pitch.value()
        self.apply_voice_preferences()
        self.save_callback()
        self.theme_callback(self.config["appearance"])
        QMessageBox.information(self, "Voice preference saved", "Arthur saved the local voice and app-wide colour preferences. A separate action is still required to enable wake-word listening.")

    def apply_voice_preferences(self):
        self.voice_runtime.configure(
            voice_id=str(self.local_voice.currentData() or ""),
            rate=self.rate.value(),
            volume=self.volume.value() / 100,
            pitch=self.pitch.value(),
        )


class PrivateNotesPage(QWidget):
    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Private notes", "Keep personal context under review. Arthur never studies a note unless you approve that exact choice."))
        editor = QGroupBox("Personal note")
        editor_layout = QVBoxLayout(editor)
        self.note = QTextEdit()
        self.note.setPlaceholderText("Write a note about yourself, a preference, or an item you want Arthur to remember later…")
        self.note.setFixedHeight(145)
        self.study = QCheckBox("Allow Arthur to study this note as a reviewed preference")
        self.voice_edit = QCheckBox("Use voice editing when a speech-to-text provider is connected")
        button = QPushButton("Save reviewed note")
        button.setObjectName("primaryButton")
        button.clicked.connect(self.save_note)
        editor_layout.addWidget(self.note)
        editor_layout.addWidget(self.study)
        editor_layout.addWidget(self.voice_edit)
        editor_layout.addWidget(button)
        layout.addWidget(editor)
        self.ledger = QLabel(self.note_summary())
        self.ledger.setObjectName("commandResult")
        self.ledger.setWordWrap(True)
        layout.addWidget(self.ledger)
        layout.addStretch()

    def note_summary(self):
        count = len(self.config.get("notes", []))
        return f"PRIVATE LEDGER • {count} reviewed note{'s' if count != 1 else ''} stored locally. Raw note text is never added to an action log."

    def save_note(self):
        text = self.note.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Add a note", "Write or dictate a note before saving it.")
            return
        self.config.setdefault("notes", []).append({"text": text, "study_approved": self.study.isChecked()})
        self.save_callback()
        self.note.clear()
        self.ledger.setText(self.note_summary())
        QMessageBox.information(self, "Private note saved", "Arthur will only use this note for learning when its reviewed-study permission is enabled.")


class AutonomyChangePage(QWidget):
    def __init__(self, config, save_callback, theme_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self.theme_callback = theme_callback
        autonomy = config.setdefault("autonomy", json.loads(json.dumps(DEFAULT_CONFIG["autonomy"])))
        appearance = config.setdefault("appearance", json.loads(json.dumps(DEFAULT_CONFIG["appearance"])))
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addWidget(workspace_heading("Autonomy & change", "Arthur can propose change, but it never applies a provider, code, or permission change without your review."))

        consent = QGroupBox("Consent-first background model")
        consent_layout = QVBoxLayout(consent)
        self.background_ready = QCheckBox("Allow Arthur to remain ready in the system tray")
        self.background_ready.setChecked(autonomy.get("background_ready", False))
        self.local_listening = QCheckBox("Allow local listening after wake-word installation and calibration")
        self.local_listening.setChecked(autonomy.get("local_listening", False))
        self.execution_consent = QCheckBox("Keep action execution consent required")
        self.execution_consent.setChecked(autonomy.get("execution_consent", True))
        self.pause_all = QCheckBox("Pause all automations and provider actions")
        self.pause_all.setChecked(autonomy.get("pause_all", False))
        self.visual = QComboBox()
        self.visual.addItems(["Ask every time", "Always show approved results", "Voice summary only"])
        self.visual.setCurrentText(autonomy.get("visual_results", "Ask every time"))
        for control in [self.background_ready, self.local_listening, self.execution_consent, self.pause_all]:
            consent_layout.addWidget(control)
        consent_layout.addWidget(QLabel("Visual result preference:"))
        consent_layout.addWidget(self.visual)
        layout.addWidget(consent)

        change = QGroupBox("Review-first self-customisation")
        change_layout = QVBoxLayout(change)
        self.request = QTextEdit()
        self.request.setFixedHeight(72)
        self.request.setPlaceholderText("For example: use a tide colour scheme with larger compact writing, or propose a calendar capability")
        review = QPushButton("Draft change proposal")
        review.clicked.connect(self.draft_proposal)
        self.proposal = QLabel("No proposal drafted. Arthur may identify a change, affected areas, validation, and rollback point—but does not change itself automatically.")
        self.proposal.setObjectName("commandResult")
        self.proposal.setWordWrap(True)
        change_layout.addWidget(self.request)
        change_layout.addWidget(review)
        change_layout.addWidget(self.proposal)
        layout.addWidget(change)

        format_group = QGroupBox("Personal format controls")
        form = QFormLayout(format_group)
        self.colour = QComboBox()
        self.colour.addItems(["Cobalt", "Tide", "Amber"])
        self.colour.setCurrentText(appearance.get("color_mode", "Cobalt"))
        self.type_scale = QComboBox()
        self.type_scale.addItems(["Standard", "Large", "Extra large"])
        self.type_scale.setCurrentText(appearance.get("type_scale", "Standard"))
        self.reduced_motion = QCheckBox("Reduce non-essential motion")
        self.reduced_motion.setChecked(appearance.get("motion_reduced", False))
        form.addRow("Workspace colour:", self.colour)
        form.addRow("Type scale:", self.type_scale)
        form.addRow(self.reduced_motion)
        save = QPushButton("Save approved local format")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save)
        form.addRow(save)
        layout.addWidget(format_group)
        layout.addStretch()

    def draft_proposal(self):
        request = self.request.toPlainText().strip()
        if not request:
            return
        normalized = request.casefold()
        if any(word in normalized for word in ["colour", "color", "font", "type", "layout", "format"]):
            scope = "LOCAL APPEARANCE"
            validation = "Preview the change, then retain a rollback to the previous local format."
        elif any(word in normalized for word in ["api", "provider", "integration", "calendar", "voice"]):
            scope = "PROVIDER OR CAPABILITY"
            validation = "Identify the required API room and create a reviewed integration proposal; no credential or provider call is made here."
        else:
            scope = "REVIEW REQUIRED"
            validation = "Clarify the affected feature, validate tests, and present a rollback point before implementation."
        self.proposal.setText(f"{scope} • Proposed outcome: {request}\nValidation: {validation}\nStatus: awaiting your explicit approval; no change has been applied.")

    def save(self):
        autonomy = self.config.setdefault("autonomy", {})
        autonomy.update({
            "background_ready": self.background_ready.isChecked(),
            "local_listening": self.local_listening.isChecked(),
            "execution_consent": self.execution_consent.isChecked(),
            "pause_all": self.pause_all.isChecked(),
            "visual_results": self.visual.currentText(),
        })
        appearance = self.config.setdefault("appearance", {})
        appearance.update({"color_mode": self.colour.currentText(), "type_scale": self.type_scale.currentText(), "motion_reduced": self.reduced_motion.isChecked()})
        self.save_callback()
        self.theme_callback(appearance)
        QMessageBox.information(self, "Local format saved", "The approved appearance preferences are active. Capability and provider changes still require a separate reviewed proposal.")


def workspace_heading(title, subtitle):
    frame = QFrame()
    frame.setObjectName("workspaceHeading")
    layout = QVBoxLayout(frame)
    eyebrow = QLabel("ARTHUR / WORKSPACE")
    eyebrow.setObjectName("eyebrow")
    heading = QLabel(title)
    heading.setObjectName("pageTitle")
    note = QLabel(subtitle)
    note.setObjectName("muted")
    note.setWordWrap(True)
    layout.addWidget(eyebrow)
    layout.addWidget(heading)
    layout.addWidget(note)
    return frame


def info_card(title, note, state):
    card = QFrame()
    card.setObjectName("routeCard")
    layout = QVBoxLayout(card)
    label = QLabel(state)
    label.setObjectName("routeState")
    heading = QLabel(title)
    heading.setObjectName("cardTitle")
    detail = QLabel(note)
    detail.setObjectName("muted")
    detail.setWordWrap(True)
    layout.addWidget(label)
    layout.addWidget(heading)
    layout.addWidget(detail)
    return card


class LanguageLibraryPage(QWidget):
    """A descriptive local catalogue; it never downloads a pack or sends text."""

    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        profile = self.config.setdefault("profile", {})
        profile.setdefault("language_favourites", ["English", "Kinyarwanda", "French", "Kiswahili"])
        profile.setdefault("active_conversation_language", profile.get("native_language", "English"))
        profile.setdefault("colloquial_drafts", [])
        profile.setdefault("source_confirmation_previews", [])
        profile.setdefault("imported_language_catalogue", [])
        self.imported_catalogue = restore_imported_catalogue(profile["imported_language_catalogue"])
        self.catalogue = merged_catalogue(self.imported_catalogue)

        layout = QVBoxLayout(self)
        title = QLabel("Language library")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        note = QLabel(
            "Browse a broad local catalogue by name, ISO code, native label, or writing system. "
            "English, Kinyarwanda, French, and Kiswahili are profile-ready; other entries describe a language and may need an approved local pack or provider for speech, translation, or research. "
            "Arthur never installs a pack, records speech, translates text, or starts a web search from this page."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        active = QGroupBox("Active conversation language")
        active_layout = QVBoxLayout(active)
        self.active_label = QLabel()
        self.active_label.setObjectName("safetyBoundary")
        active_layout.addWidget(self.active_label)
        layout.addWidget(active)

        import_group = QGroupBox("All-language identifier coverage")
        import_layout = QVBoxLayout(import_group)
        import_note = QLabel(
            "Arthur bundles a discovery catalogue. To stage a broader known-language list, choose an official ISO 639-3 tab-separated table yourself. "
            "Arthur reads it locally, stores only accepted identifiers in this profile, and never uploads the table or treats it as a pack, translation, or slang source."
        )
        import_note.setObjectName("muted")
        import_note.setWordWrap(True)
        self.import_identifier_table_button = QPushButton("Choose local ISO 639-3 table")
        self.import_identifier_table_button.clicked.connect(self.import_identifier_table)
        self.import_identifier_status = QLabel()
        self.import_identifier_status.setObjectName("safetyBoundary")
        self.import_identifier_status.setWordWrap(True)
        import_layout.addWidget(import_note)
        import_layout.addWidget(self.import_identifier_table_button)
        import_layout.addWidget(self.import_identifier_status)
        layout.addWidget(import_group)

        library = QGroupBox("Searchable local language catalogue")
        library_layout = QVBoxLayout(library)
        self.catalogue_search = QLineEdit()
        self.catalogue_search.setPlaceholderText("Search language, ISO code, native label, or writing system")
        self.catalogue_search.textChanged.connect(self.refresh_catalogue)
        self.catalogue_list = QListWidget()
        self.catalogue_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.catalogue_list.currentItemChanged.connect(self.update_selection_detail)
        self.catalogue_detail = QLabel("Choose a language to inspect its local readiness.")
        self.catalogue_detail.setWordWrap(True)
        self.catalogue_detail.setObjectName("muted")
        actions = QHBoxLayout()
        self.set_active_button = QPushButton("Use for conversation")
        self.set_active_button.clicked.connect(self.set_active_language)
        self.favourite_button = QPushButton("Add to favourites")
        self.favourite_button.clicked.connect(self.toggle_favourite)
        actions.addWidget(self.set_active_button)
        actions.addWidget(self.favourite_button)
        actions.addStretch()
        library_layout.addWidget(self.catalogue_search)
        library_layout.addWidget(self.catalogue_list, 1)
        library_layout.addWidget(self.catalogue_detail)
        library_layout.addLayout(actions)
        layout.addWidget(library, 2)

        community = QGroupBox("Community-reviewed colloquial library")
        community_layout = QVBoxLayout(community)
        community_note = QLabel(
            "Arthur does not bundle or invent slang. Colloquial language varies by community, region, generation, and context. "
            "A source-confirmed record retains named evidence, region or dialect, and use context. It is still not community review, publication permission, or approval for automatic speech, translation, search, or replies."
        )
        community_note.setObjectName("muted")
        community_note.setWordWrap(True)
        community_form = QFormLayout()
        self.colloquial_expression_input = QLineEdit()
        self.colloquial_expression_input.setMaxLength(120)
        self.colloquial_expression_input.setPlaceholderText("Expression (private draft, 120 characters)")
        self.colloquial_context_input = QLineEdit()
        self.colloquial_context_input.setMaxLength(160)
        self.colloquial_context_input.setPlaceholderText("Region or context (required)")
        self.colloquial_meaning_input = QLineEdit()
        self.colloquial_meaning_input.setMaxLength(240)
        self.colloquial_meaning_input.setPlaceholderText("Plain-language meaning (required for review)")
        self.colloquial_sensitivity_input = QLineEdit()
        self.colloquial_sensitivity_input.setMaxLength(180)
        self.colloquial_sensitivity_input.setPlaceholderText("Sensitivity or use note (required for review)")
        self.colloquial_source_input = QTextEdit()
        self.colloquial_source_input.setFixedHeight(58)
        self.colloquial_source_input.setPlaceholderText("Community source or review note (required, 240 characters)")
        community_form.addRow("Expression", self.colloquial_expression_input)
        community_form.addRow("Context", self.colloquial_context_input)
        community_form.addRow("Meaning", self.colloquial_meaning_input)
        community_form.addRow("Sensitivity / use", self.colloquial_sensitivity_input)
        community_form.addRow("Source / review note", self.colloquial_source_input)
        self.save_colloquial_draft_button = QPushButton("Save private local draft")
        self.save_colloquial_draft_button.clicked.connect(self.save_colloquial_draft)
        self.preview_colloquial_review_button = QPushButton("Prepare review preview")
        self.preview_colloquial_review_button.clicked.connect(self.prepare_colloquial_review)
        self.colloquial_status = QLabel()
        self.colloquial_status.setObjectName("safetyBoundary")
        self.colloquial_status.setWordWrap(True)
        community_layout.addWidget(community_note)
        self.source_confirmed_examples = QLabel()
        self.source_confirmed_examples.setObjectName("safetyBoundary")
        self.source_confirmed_examples.setWordWrap(True)
        community_layout.addWidget(self.source_confirmed_examples)
        community_layout.addLayout(community_form)
        community_layout.addWidget(self.save_colloquial_draft_button)
        community_layout.addWidget(self.preview_colloquial_review_button)
        community_layout.addWidget(self.colloquial_status)

        confirmation = QGroupBox("Reviewer-attested source confirmation")
        confirmation_layout = QFormLayout(confirmation)
        confirmation_note = QLabel(
            "Use this only after a human reviewer has checked a recognised community, government, educational, or archival source. "
            "Arthur stores a local evidence preview and cannot convert it into community-reviewed content."
        )
        confirmation_note.setObjectName("muted")
        confirmation_note.setWordWrap(True)
        self.source_use_context_input = QLineEdit()
        self.source_use_context_input.setMaxLength(180)
        self.source_use_context_input.setPlaceholderText("For example: greeting listed by source")
        self.source_evidence_kind = QComboBox()
        self.source_evidence_kind.addItem("Community language programme", "community-language-program")
        self.source_evidence_kind.addItem("Government or cultural resource", "government-cultural-resource")
        self.source_evidence_kind.addItem("Educational or archival resource", "educational-or-archival-resource")
        self.source_evidence_title_input = QLineEdit()
        self.source_evidence_title_input.setMaxLength(180)
        self.source_evidence_title_input.setPlaceholderText("Named publisher and resource")
        self.source_evidence_url_input = QLineEdit()
        self.source_evidence_url_input.setMaxLength(500)
        self.source_evidence_url_input.setPlaceholderText("https://…")
        self.source_evidence_reviewed = QCheckBox(
            "I checked the source, language or dialect, regional context, and intended use. I understand this is not community review."
        )
        self.preview_source_confirmation_button = QPushButton("Prepare source-confirmed preview")
        self.preview_source_confirmation_button.setObjectName("primaryButton")
        self.preview_source_confirmation_button.clicked.connect(self.prepare_source_confirmation)
        self.source_confirmation_status = QLabel("No source-confirmed preview prepared.")
        self.source_confirmation_status.setObjectName("safetyBoundary")
        self.source_confirmation_status.setWordWrap(True)
        confirmation_layout.addRow(confirmation_note)
        confirmation_layout.addRow("Use context", self.source_use_context_input)
        confirmation_layout.addRow("Evidence source type", self.source_evidence_kind)
        confirmation_layout.addRow("Evidence title", self.source_evidence_title_input)
        confirmation_layout.addRow("HTTPS evidence URL", self.source_evidence_url_input)
        confirmation_layout.addRow(self.source_evidence_reviewed)
        confirmation_layout.addRow(self.preview_source_confirmation_button)
        confirmation_layout.addRow(self.source_confirmation_status)
        community_layout.addWidget(confirmation)
        layout.addWidget(community)

        prepare = QGroupBox("Multilingual research preparation")
        prepare_layout = QVBoxLayout(prepare)
        prepare_note = QLabel("Arthur keeps this question exactly as written in the selected language. It only prepares a review; it does not translate, copy to a provider, or fetch search results.")
        prepare_note.setWordWrap(True)
        prepare_note.setObjectName("muted")
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Type a question in the active conversation language")
        self.query_input.setFixedHeight(78)
        prepare_button = QPushButton("Prepare multilingual research review")
        prepare_button.setObjectName("primaryButton")
        prepare_button.clicked.connect(self.prepare_query)
        self.query_result = QLabel("No research request prepared.")
        self.query_result.setWordWrap(True)
        self.query_result.setObjectName("safetyBoundary")
        prepare_layout.addWidget(prepare_note)
        prepare_layout.addWidget(self.query_input)
        prepare_layout.addWidget(prepare_button)
        prepare_layout.addWidget(self.query_result)
        layout.addWidget(prepare)

        self.refresh_catalogue()
        self.refresh_active_label()
        self.refresh_import_status()
        self.refresh_colloquial_status()
        self.refresh_source_confirmed_examples()

    def current_entry(self):
        item = self.catalogue_list.currentItem()
        return find_language(item.data(Qt.ItemDataRole.UserRole), self.catalogue) if item else None

    def refresh_catalogue(self):
        selected_name = self.current_entry().name if self.current_entry() else self.config["profile"].get("active_conversation_language", "English")
        self.catalogue_list.blockSignals(True)
        self.catalogue_list.clear()
        for entry in search_languages(self.catalogue_search.text(), self.catalogue):
            item = QListWidgetItem(f"{entry.name}  ·  {entry.native_label}  ·  {entry.code.upper()}")
            item.setData(Qt.ItemDataRole.UserRole, entry.name)
            self.catalogue_list.addItem(item)
            if entry.name == selected_name:
                self.catalogue_list.setCurrentItem(item)
        self.catalogue_list.blockSignals(False)
        if self.catalogue_list.currentItem() is None and self.catalogue_list.count():
            self.catalogue_list.setCurrentRow(0)
        self.update_selection_detail()

    def update_selection_detail(self, *_):
        entry = self.current_entry()
        if entry is None:
            self.catalogue_detail.setText("No matching language is in the staged local catalogue. You may choose an official identifier table later; no package is installed here.")
            self.set_active_button.setEnabled(False)
            self.favourite_button.setEnabled(False)
            return
        favourites = set(self.config["profile"].get("language_favourites", []))
        self.catalogue_detail.setText(
            f"{entry.name} / {entry.native_label} · ISO {entry.code.upper()} · {entry.script} writing system · {entry.readiness}.\n"
            f"Community review: {entry.community_review}.\nVitality context: {entry.vitality_context}.\n"
            f"Colloquial content: {entry.colloquial_status}.\nNo speech, translation, search, or provider request is made by selecting it."
        )
        self.set_active_button.setEnabled(True)
        self.favourite_button.setEnabled(True)
        self.favourite_button.setText("Remove from favourites" if entry.name in favourites else "Add to favourites")
        self.refresh_source_confirmed_examples()

    def refresh_active_label(self):
        active = self.config["profile"].get("active_conversation_language", "English")
        entry = find_language(active, self.catalogue)
        readiness = entry.readiness if entry else "custom profile label"
        favourites = ", ".join(self.config["profile"].get("language_favourites", [])) or "None selected"
        self.active_label.setText(f"Selected: {active} ({readiness}). Favourites: {favourites}.")

    def set_active_language(self):
        entry = self.current_entry()
        if entry is None:
            return
        self.config["profile"]["active_conversation_language"] = entry.name
        self.save_callback()
        self.refresh_active_label()
        QMessageBox.information(self, "Language selected", f"Arthur will prepare conversation and research review in {entry.name}. Configure any required language pack or approved provider separately.")

    def toggle_favourite(self):
        entry = self.current_entry()
        if entry is None:
            return
        current = self.config["profile"].get("language_favourites", [])
        requested = [name for name in current if name != entry.name] if entry.name in current else [*current, entry.name]
        self.config["profile"]["language_favourites"] = normalise_favourites(requested, self.catalogue)
        self.save_callback()
        self.refresh_active_label()
        self.update_selection_detail()

    def refresh_colloquial_status(self):
        drafts = self.config["profile"].get("colloquial_drafts", [])
        self.colloquial_status.setText(
            f"{len(drafts)} private local draft(s) saved. A draft is not community reviewed and will not be used for speech, translation, search, or responses automatically."
        )

    def refresh_source_confirmed_examples(self):
        entry = self.current_entry()
        if entry is None or not hasattr(self, "source_confirmed_examples"):
            return
        records = source_confirmed_expressions(entry.name, self.catalogue)
        if not records:
            self.source_confirmed_examples.setText(
                "No bundled source-confirmed example is available for this selected language. A local draft still requires named evidence, region or dialect, and use context before a reviewer can prepare a source-confirmed preview."
            )
            return
        formatted = []
        for record in records:
            formatted.append(
                f"{record['review_status']}: {record['expression']} — {record['meaning']}\n"
                f"Region / dialect: {record['regional_context']}\nUse: {record['use_context']}\n"
                f"Evidence: {record['evidence_title']} ({record['evidence_url']})\n{record['sensitivity_note']}"
            )
        self.source_confirmed_examples.setText(
            "Source-confirmed examples retain the cited region, dialect, and use context. Community review remains separate.\n\n"
            + "\n\n".join(formatted)
        )

    def refresh_import_status(self):
        self.import_identifier_status.setText(
            f"{len(self.imported_catalogue):,} additional ISO identifiers staged locally; {len(self.catalogue):,} catalogue entries available for selection. "
            "Staging does not add language packs, provider access, or verified colloquial content."
        )

    def import_identifier_table(self):
        selected, _ = QFileDialog.getOpenFileName(self, "Choose an official ISO 639-3 table", str(Path.home()), "Tab-separated tables (*.tab *.tsv);;Text files (*.txt);;All files (*)")
        if not selected:
            return
        try:
            contents = Path(selected).read_text(encoding="utf-8-sig")
            parsed = parse_iso6393_table(contents)
            if not parsed:
                raise ValueError("No new ISO 639-3 identifiers were found in this table.")
        except (OSError, UnicodeError, ValueError) as error:
            QMessageBox.warning(self, "Identifier table not staged", str(error))
            return
        self.imported_catalogue = parsed
        self.catalogue = merged_catalogue(self.imported_catalogue)
        self.config["profile"]["imported_language_catalogue"] = serialise_imported_catalogue(self.imported_catalogue)
        self.save_callback()
        self.refresh_catalogue()
        self.refresh_active_label()
        self.refresh_import_status()
        QMessageBox.information(self, "Identifiers staged locally", f"Arthur staged {len(parsed):,} ISO identifiers locally. It did not upload the table, install a language pack, or add verified colloquial content.")

    def save_colloquial_draft(self):
        entry = self.current_entry()
        if entry is None:
            QMessageBox.warning(self, "Choose a language", "Choose a language from the local catalogue before saving a private draft.")
            return
        try:
            draft = create_colloquial_draft(
                entry.name,
                self.colloquial_expression_input.text(),
                self.colloquial_context_input.text(),
                self.colloquial_source_input.toPlainText(),
                self.catalogue,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Private draft needs context", str(error))
            return
        drafts = list(self.config["profile"].get("colloquial_drafts", []))
        drafts.append(draft)
        self.config["profile"]["colloquial_drafts"] = drafts[-40:]
        self.save_callback()
        self.colloquial_expression_input.clear()
        self.colloquial_context_input.clear()
        self.colloquial_source_input.clear()
        self.refresh_colloquial_status()
        QMessageBox.information(self, "Private local draft saved", "Arthur saved this private draft locally. It is not verified community content and will not be used automatically.")

    def prepare_colloquial_review(self):
        entry = self.current_entry()
        if entry is None:
            QMessageBox.warning(self, "Choose a language", "Choose a language from the local catalogue before preparing a review preview.")
            return
        try:
            preview = prepare_colloquial_entry_review(
                entry.name,
                self.colloquial_expression_input.text(),
                self.colloquial_meaning_input.text(),
                self.colloquial_context_input.text(),
                self.colloquial_source_input.toPlainText(),
                self.colloquial_sensitivity_input.text(),
                self.catalogue,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Review preview needs context", str(error))
            return
        self.colloquial_status.setText(
            f"{preview['review_status']}: {preview['language']} · {preview['regional_context']}. "
            "The preview remains local, unpublished, unverified, and unavailable to speech, translation, search, or responses."
        )

    def prepare_source_confirmation(self):
        entry = self.current_entry()
        if entry is None:
            QMessageBox.warning(self, "Choose a language", "Choose a language from the local catalogue before preparing a source-confirmed preview.")
            return
        try:
            preview = prepare_source_confirmed_expression(
                entry.name,
                self.colloquial_expression_input.text(),
                self.colloquial_meaning_input.text(),
                self.colloquial_context_input.text(),
                self.source_use_context_input.text(),
                self.colloquial_sensitivity_input.text(),
                str(self.source_evidence_kind.currentData()),
                self.source_evidence_title_input.text(),
                self.source_evidence_url_input.text(),
                self.source_evidence_reviewed.isChecked(),
                self.catalogue,
            )
        except ValueError as error:
            QMessageBox.warning(self, "Source confirmation needs evidence", str(error))
            return
        previews = list(self.config["profile"].get("source_confirmation_previews", []))
        previews.append(preview)
        self.config["profile"]["source_confirmation_previews"] = previews[-40:]
        self.save_callback()
        self.source_confirmation_status.setText(
            f"{preview['review_status']}: {preview['language']} · {preview['regional_context']}. "
            f"Evidence: {preview['evidence_title']}. {preview['verification_note']}"
        )

    def prepare_query(self):
        active = self.config["profile"].get("active_conversation_language", "English")
        prepared = prepare_search_query(self.query_input.toPlainText(), active, self.catalogue)
        if not prepared["ready"]:
            self.query_result.setText(str(prepared["reason"]))
            return
        self.query_result.setText(f"Prepared only — {prepared['language']} ({prepared['code'].upper()}): “{prepared['query']}”\n{prepared['reason']}")


class ProfilePage(QWidget):
    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        layout = QVBoxLayout(self)
        title = QLabel("User profile")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        form = QFormLayout()
        profile = config["profile"]
        self.name = QLineEdit(profile.get("display_name", ""))
        self.pronunciation = QLineEdit(profile.get("pronunciation", ""))
        self.native = QComboBox()
        configure_primary_language_combo(self.native, profile.get("native_language", ""))
        self.additional = QLineEdit(", ".join(profile.get("additional_languages", [])))
        self.wake = QLineEdit(profile.get("wake_word", "Arthur"))
        self.title_field = QLineEdit(profile.get("title", "Sir"))
        form.addRow("Name:", self.name)
        form.addRow("Pronunciation:", self.pronunciation)
        form.addRow("Primary system language (required):", self.native)
        form.addRow("Additional languages:", self.additional)
        form.addRow("Wake word:", self.wake)
        form.addRow("Title:", self.title_field)
        layout.addLayout(form)
        save = QPushButton("Save profile")
        save.clicked.connect(self.save)
        layout.addWidget(save)
        layout.addStretch()

    def save(self):
        primary_language = selected_primary_language(self.native)
        if not primary_language:
            QMessageBox.warning(self, "Language required", "Choose the primary system language Arthur should use for typed and voice interactions.")
            return
        self.config["profile"].update({
            "display_name": self.name.text().strip(),
            "pronunciation": self.pronunciation.text().strip(),
            "native_language": primary_language,
            "active_conversation_language": primary_language,
            "additional_languages": [x.strip() for x in self.additional.text().split(",") if x.strip()],
            "wake_word": self.wake.text().strip() or "Arthur",
            "title": self.title_field.text().strip() or "Sir",
        })
        self.save_callback()
        QMessageBox.information(self, "Profile saved", f"Arthur will use {primary_language} for typed and voice interactions. This does not enable microphone access.")


class ConductMemoryPage(QWidget):
    """User-controlled tone, adaptive-learning, and protective-monitoring settings."""

    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        conduct = config.setdefault("conduct", json.loads(json.dumps(DEFAULT_CONFIG["conduct"])))
        layout = QVBoxLayout(self)
        title = QLabel("Conduct and reviewed memory")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        note = QLabel(
            "Arthur may be calm, direct, and lightly witty, but its behavior is always user-configured. "
            "Routines and personal preferences are proposed for review; they are never silently turned into permanent instructions."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        demeanor = QGroupBox("Voice and demeanor")
        demeanor_layout = QVBoxLayout(demeanor)
        self.british = QCheckBox("Use the refined British delivery style when the selected voice supports it")
        self.british.setChecked(conduct.get("refined_british_style", True))
        self.calm = QCheckBox("Keep responses direct, composed, and honest")
        self.calm.setChecked(conduct.get("direct_calm_responses", True))
        self.wit = QCheckBox("Permit occasional dry wit; never ridicule or shame the user")
        self.wit.setChecked(conduct.get("dry_wit", True))
        self.title_protocol = QCheckBox("Use the profile’s preferred title when appropriate")
        self.title_protocol.setChecked(conduct.get("use_preferred_title", True))
        for item in [self.british, self.calm, self.wit, self.title_protocol]:
            demeanor_layout.addWidget(item)
        layout.addWidget(demeanor)

        memory = QGroupBox("Adaptive preferences and routine suggestions")
        memory_layout = QVBoxLayout(memory)
        self.propose_routines = QCheckBox("Suggest repeatable routines from user-approved activity patterns")
        self.propose_routines.setChecked(conduct.get("propose_routines", False))
        self.review_learning = QCheckBox("Require approval before Arthur saves a preference, saying, pronunciation, or routine")
        self.review_learning.setChecked(conduct.get("review_before_learning", True))
        self.retention = QSpinBox()
        self.retention.setRange(1, 365)
        self.retention.setValue(int(conduct.get("memory_retention_days", 30)))
        self.retention.setSuffix(" days")
        memory_layout.addWidget(self.propose_routines)
        memory_layout.addWidget(self.review_learning)
        memory_layout.addWidget(QLabel("Default retention period for reviewed preference records:"))
        memory_layout.addWidget(self.retention)
        layout.addWidget(memory)

        personalisation = QGroupBox("Learn my style — local, optional, and reviewable")
        personalisation_layout = QVBoxLayout(personalisation)
        personalisation_note = QLabel(
            "Arthur will not collect ‘every’ camera or microphone detail. It can retain only a file you deliberately choose, "
            "after separate permission, so a future configured local or developer-approved service may prepare a style-learning proposal. "
            "No sample is uploaded, analysed, or used to imitate another person through this prototype."
        )
        personalisation_note.setObjectName("muted")
        personalisation_note.setWordWrap(True)
        personalisation_layout.addWidget(personalisation_note)
        self.camera_style = QCheckBox("Allow me to import one camera/photo style sample chosen by the user")
        self.camera_style.setChecked(conduct.get("camera_style_learning_enabled", False))
        self.microphone_style = QCheckBox("Allow me to import one short own-voice sample chosen by the user")
        self.microphone_style.setChecked(conduct.get("microphone_style_learning_enabled", False))
        self.voice_clone_requests = QCheckBox("Allow preparation of an own-voice cloning request after a fresh confirmation")
        self.voice_clone_requests.setChecked(conduct.get("own_voice_cloning_requests_enabled", False))
        self.style_retention = QSpinBox()
        self.style_retention.setRange(1, 30)
        self.style_retention.setValue(int(conduct.get("style_sample_retention_days", 7)))
        self.style_retention.setSuffix(" days")
        import_photo = QPushButton("Import reviewed local photo sample")
        import_photo.clicked.connect(self.import_photo_style_sample)
        import_voice = QPushButton("Import reviewed own-voice sample")
        import_voice.clicked.connect(self.import_voice_style_sample)
        prepare_clone = QPushButton("Prepare own-voice cloning consent request")
        prepare_clone.clicked.connect(self.prepare_voice_clone_request)
        for item in [self.camera_style, self.microphone_style, self.voice_clone_requests]:
            personalisation_layout.addWidget(item)
        personalisation_layout.addWidget(QLabel("Maximum local retention for these optional sample files:"))
        personalisation_layout.addWidget(self.style_retention)
        personalisation_layout.addWidget(import_photo)
        personalisation_layout.addWidget(import_voice)
        personalisation_layout.addWidget(prepare_clone)
        layout.addWidget(personalisation)

        protection = QGroupBox("Authorized protective monitoring")
        protection_layout = QVBoxLayout(protection)
        self.health = QCheckBox("Monitor local CPU, memory, available storage, and reported temperature sensors")
        self.health.setChecked(conduct.get("health_monitoring", True))
        self.schedule = QCheckBox("Offer calendar and schedule assistance only after an approved integration is connected")
        self.schedule.setChecked(conduct.get("schedule_assistance", False))
        protection_layout.addWidget(self.health)
        protection_layout.addWidget(self.schedule)
        protection_note = QLabel(
            "Arthur does not perform intrusion, credential harvesting, surveillance, security bypasses, or weapon/combat functions. "
            "It may report local health signals and recommend approved actions."
        )
        protection_note.setObjectName("muted")
        protection_note.setWordWrap(True)
        protection_layout.addWidget(protection_note)
        layout.addWidget(protection)

        save = QPushButton("Save conduct and memory policy")
        save.clicked.connect(self.save)
        layout.addWidget(save)
        layout.addStretch()

    def save(self):
        self.config["conduct"].update({
            "refined_british_style": self.british.isChecked(),
            "direct_calm_responses": self.calm.isChecked(),
            "dry_wit": self.wit.isChecked(),
            "use_preferred_title": self.title_protocol.isChecked(),
            "propose_routines": self.propose_routines.isChecked(),
            "review_before_learning": self.review_learning.isChecked(),
            "memory_retention_days": self.retention.value(),
            "health_monitoring": self.health.isChecked(),
            "schedule_assistance": self.schedule.isChecked(),
            "camera_style_learning_enabled": self.camera_style.isChecked(),
            "microphone_style_learning_enabled": self.microphone_style.isChecked(),
            "own_voice_cloning_requests_enabled": self.voice_clone_requests.isChecked(),
            "style_sample_retention_days": self.style_retention.value(),
        })
        self.save_callback()
        QMessageBox.information(self, "Conduct policy saved", "Arthur will follow the updated tone, reviewed-learning, and monitoring boundaries.")

    def _import_local_style_sample(self, *, kind: str, enabled: bool, extensions: str, description: str):
        if not enabled:
            QMessageBox.warning(self, "Permission required", f"Enable the local {kind} sample permission and save the conduct policy before importing a file.")
            return
        approval = QMessageBox.question(
            self,
            f"Review {kind} sample import",
            f"Arthur will copy one {description} that you choose into its local data folder. It will not open a camera or microphone, upload the file, analyse it, or create a voice clone. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if approval != QMessageBox.StandardButton.Yes:
            return
        source, _ = QFileDialog.getOpenFileName(self, f"Choose reviewed {kind} sample", str(Path.home()), extensions)
        if not source:
            return
        sample_dir = DATA_DIR / "style_samples"
        sample_dir.mkdir(parents=True, exist_ok=True)
        source_path = Path(source)
        destination = sample_dir / f"{kind.replace(' ', '_')}_reviewed{source_path.suffix.lower()}"
        try:
            shutil.copy2(source_path, destination)
        except OSError as error:
            QMessageBox.warning(self, "Import unavailable", f"Arthur could not retain the selected local sample: {error}")
            return
        self.config["conduct"][f"{kind.replace(' ', '_')}_sample_path"] = str(destination)
        self.save_callback()
        QMessageBox.information(self, "Local sample retained", f"Arthur retained one reviewed {kind} sample locally at the configured retention setting. It was not uploaded or used for imitation.")

    def import_photo_style_sample(self):
        self._import_local_style_sample(kind="camera style", enabled=self.camera_style.isChecked(), extensions="Images (*.png *.jpg *.jpeg *.webp)", description="photo or still image")

    def import_voice_style_sample(self):
        self._import_local_style_sample(kind="own voice", enabled=self.microphone_style.isChecked(), extensions="Audio (*.wav *.mp3 *.m4a *.ogg)", description="short voice recording")

    def prepare_voice_clone_request(self):
        if not self.voice_clone_requests.isChecked() or not self.microphone_style.isChecked():
            QMessageBox.warning(self, "Consent required", "Enable both own-voice sample and own-voice cloning-request permissions, then save the conduct policy before preparing a request.")
            return
        if not self.config["conduct"].get("own_voice_sample_path"):
            QMessageBox.information(self, "Own-voice sample required", "Import a reviewed own-voice sample first. Arthur will not record a microphone or clone any voice automatically.")
            return
        approval = QMessageBox.question(
            self,
            "Prepare own-voice cloning proposal",
            "This records a local proposal only. A configured developer-controlled voice service, its data terms, the exact sample, and a separate final approval must be reviewed before any upload or voice generation. Prepare that proposal?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if approval == QMessageBox.StandardButton.Yes:
            self.config["conduct"]["own_voice_cloning_proposal_ready"] = True
            self.save_callback()
            QMessageBox.information(self, "Proposal prepared", "Arthur prepared no upload and no clone. Connect and review a developer-controlled voice-cloning provider in the API Vault to continue.")


class ReviewedCommandsPage(QWidget):
    """Natural-language planner for an explicit local-administration allowlist only."""

    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self.current_plan = None
        policy = config.setdefault("command_policy", json.loads(json.dumps(DEFAULT_CONFIG["command_policy"])))

        layout = QVBoxLayout(self)
        title = QLabel("Reviewed command planner")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        note = QLabel(
            "Say or type an approved computer task in ordinary language. Arthur translates it into a fixed, reviewable command template; "
            "it never sends AI-generated text directly to Command Prompt, PowerShell, WSL, or Kali."
        )
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        setup = QGroupBox("Local command policy")
        setup_layout = QFormLayout(setup)
        self.wsl_distro = QLineEdit(policy.get("wsl_distro", ""))
        self.wsl_distro.setPlaceholderText("For example, kali-linux (optional, local WSL only)")
        self.allow_read_only = QCheckBox("Allow Arthur to run reviewed read-only local diagnostics after planning")
        self.allow_read_only.setChecked(policy.get("allow_read_only_execution", False))
        self.paused = QCheckBox("Pause all command execution; planning remains visible")
        self.paused.setChecked(policy.get("automation_paused", False))
        setup_layout.addRow("Approved WSL distribution:", self.wsl_distro)
        setup_layout.addRow(self.allow_read_only)
        setup_layout.addRow(self.paused)
        layout.addWidget(setup)

        request_group = QGroupBox("Ask Arthur in your own words")
        request_layout = QVBoxLayout(request_group)
        self.request = QTextEdit()
        self.request.setPlaceholderText("Examples: ‘show my disk space’, ‘check my internet’, ‘show Kali WSL memory’")
        self.request.setFixedHeight(74)
        request_layout.addWidget(self.request)
        row = QHBoxLayout()
        plan_button = QPushButton("Prepare reviewed command")
        plan_button.clicked.connect(self.prepare)
        run_button = QPushButton("Run approved plan")
        run_button.clicked.connect(self.run_current_plan)
        row.addWidget(plan_button)
        row.addWidget(run_button)
        request_layout.addLayout(row)
        layout.addWidget(request_group)

        self.result = QLabel("No command prepared. Arthur can plan low-risk local diagnostics, and confirmation-gated local actions such as locking this Windows session.")
        self.result.setObjectName("muted")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)
        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        self.command_preview.setPlaceholderText("The exact reviewed command will appear here. Raw or generated shell text is never accepted.")
        self.command_preview.setFixedHeight(86)
        layout.addWidget(self.command_preview)
        boundary = QLabel(
            "Allowed: local Windows and configured WSL diagnostics from a small template registry. Not allowed: security bypasses, credential access, scanning, exploitation, malware, remote attacks, or arbitrary commands."
        )
        boundary.setObjectName("muted")
        boundary.setWordWrap(True)
        layout.addWidget(boundary)
        layout.addStretch()

    def planner(self):
        return CommandPlanner(wsl_distro=self.wsl_distro.text(), approved_directories=[])

    def save_policy(self):
        self.config["command_policy"].update({
            "wsl_distro": self.wsl_distro.text().strip(),
            "allow_read_only_execution": self.allow_read_only.isChecked(),
            "automation_paused": self.paused.isChecked(),
        })
        self.save_callback()

    def prepare(self):
        self.save_policy()
        self.current_plan = self.planner().plan(self.request.toPlainText())
        plan = self.current_plan
        self.result.setText(f"{plan.risk.value.upper()} • {plan.summary}" + (f"\nReason: {plan.reason}" if plan.reason else ""))
        self.command_preview.setPlainText(plan.preview())

    def run_current_plan(self):
        self.save_policy()
        if self.current_plan is None:
            QMessageBox.information(self, "Prepare a command first", "Ask Arthur for an approved task, then inspect the generated command before attempting to run it.")
            return
        plan = self.current_plan
        if not plan.allowed:
            QMessageBox.warning(self, "Command blocked", plan.reason)
            return
        if self.paused.isChecked():
            QMessageBox.information(self, "Automation paused", "Command execution is paused. Arthur may continue to prepare transparent plans.")
            return
        if not self.allow_read_only.isChecked() and plan.risk == RiskLevel.LOW:
            QMessageBox.information(self, "Execution disabled", "Enable reviewed read-only diagnostics in Local command policy before Arthur can run a low-risk plan.")
            return
        if os.name != "nt":
            QMessageBox.information(self, "Windows execution only", "This prototype only executes reviewed command templates on Windows. The preview remains available on other systems.")
            return
        approval = True
        if plan.requires_confirmation:
            approval = QMessageBox.question(
                self,
                "Confirm local action",
                f"Arthur will run this local command:\n\n{plan.preview()}\n\nProceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            ) == QMessageBox.StandardButton.Yes
        if not approval:
            return
        try:
            code, stdout, stderr = self.planner().execute(plan, approved=approval)
        except (OSError, PermissionError, TimeoutError) as error:
            QMessageBox.warning(self, "Command was not completed", str(error))
            return
        output = stdout.strip() or stderr.strip() or "No text output returned."
        self.command_preview.setPlainText(output[:8000])
        self.result.setText(f"{plan.risk.value.upper()} • Completed with exit code {code}. Arthur recorded the intent and outcome without saving the raw request text.")


class PermissionsPage(QWidget):
    def __init__(self, config, save_callback, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        layout = QVBoxLayout(self)
        title = QLabel("Permissions and safety")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        note = QLabel("Arthur can perform broad PC tasks only when enabled. Risky actions remain confirmation-gated.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)
        privacy = config["privacy"]
        self.background = QCheckBox("Keep Arthur in the Windows system tray when its window is closed")
        self.background.setChecked(privacy.get("background_enabled", True))
        self.wake_background = QCheckBox("Keep approved wake-word listening active while Arthur is in the tray")
        self.wake_background.setChecked(privacy.get("wake_word_background_enabled", False))
        self.spoken = QCheckBox("Use spoken replies by default")
        self.spoken.setChecked(privacy.get("spoken_only", True))
        self.confirm = QCheckBox("Always confirm destructive, private, financial, communication, and administrator actions")
        self.confirm.setChecked(privacy.get("confirm_risky", True))
        self.screen = QCheckBox("Allow screen analysis when requested")
        self.screen.setChecked(privacy.get("allow_screen_analysis", False))
        self.broad = QCheckBox("Allow broad PC access (still confirmation-gated for risky actions)")
        self.broad.setChecked(privacy.get("allow_broad_pc_access", False))
        self.local_sensors = QCheckBox("Allow local hardware sensor readings only while Arthur's Sensor workspace is open")
        self.local_sensors.setChecked(config.setdefault("sensors", {}).get("enabled", False))
        self.sensor_note = QLabel("Temperature appears only when Windows exposes a thermal zone. CPU/GPU temperature otherwise requires a separately approved compatible local adapter; Arthur does not install one and never uploads telemetry.")
        self.sensor_note.setObjectName("muted")
        self.sensor_note.setWordWrap(True)
        for item in [self.background, self.wake_background, self.spoken, self.confirm, self.screen, self.broad, self.local_sensors, self.sensor_note]:
            layout.addWidget(item)
        install_wake_word = QPushButton("Install openWakeWord after approval…")
        install_wake_word.clicked.connect(self.install_openwakeword)
        layout.addWidget(install_wake_word)
        save = QPushButton("Save permissions")
        save.clicked.connect(self.save)
        layout.addWidget(save)
        layout.addStretch()

    def save(self):
        self.config["privacy"].update({
            "background_enabled": self.background.isChecked(),
            "wake_word_background_enabled": self.wake_background.isChecked(),
            "spoken_only": self.spoken.isChecked(),
            "confirm_risky": self.confirm.isChecked(),
            "allow_screen_analysis": self.screen.isChecked(),
            "allow_broad_pc_access": self.broad.isChecked(),
        })
        self.config.setdefault("sensors", {})["enabled"] = self.local_sensors.isChecked()
        self.save_callback()
        QMessageBox.information(self, "Permissions saved", "Arthur’s permission policy has been updated.")

    def install_openwakeword(self):
        script = BASE_DIR / "install_openwakeword.bat"
        if not script.exists():
            QMessageBox.warning(self, "Installer unavailable", "The openWakeWord setup script was not found.")
            return
        choice = QMessageBox.question(
            self,
            "Approve optional wake-word installation",
            "Arthur will open Command Prompt and run the visible optional dependency installer.\n\n"
            "Command: pip install openwakeword sounddevice\n\n"
            "Continue only if you approve this installation.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if choice == QMessageBox.StandardButton.Yes:
            os.startfile(script)


class CustomIntegrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add custom API integration")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        title = QLabel("Add a developer-approved API")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)
        note = QLabel("The provider is added as disabled and unverified. Enter its key later through protected credential storage, then test it deliberately.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("For example, Calendar service")
        self.endpoint = QLineEdit()
        self.endpoint.setPlaceholderText("https://api.example.com")
        self.auth = QComboBox()
        self.auth.addItems(["API key", "OAuth 2.0", "Bearer token", "Local network token"])
        form.addRow("Integration name:", self.name)
        form.addRow("HTTPS base URL:", self.endpoint)
        form.addRow("Authentication:", self.auth)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        if not self.name.text().strip() or not self.endpoint.text().strip().startswith("https://"):
            QMessageBox.warning(self, "Details required", "Enter an integration name and an HTTPS base URL.")
            return
        super().accept()


class UpdatesPage(QWidget):
    """Manual GitHub release metadata checks; never background polling or downloading."""

    def __init__(self, config, save_callback, tutorial_callback=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.save_callback = save_callback
        self.tutorial_callback = tutorial_callback
        layout = QVBoxLayout(self)
        title = QLabel("Updates")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        note = QLabel("Arthur never polls GitHub in the background. It contacts GitHub only after you choose a manual release check, then asks again before any future download or installer launch.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)

        settings = config.setdefault("updates", {})
        release_group = QGroupBox("Manual GitHub Releases check")
        release_layout = QFormLayout(release_group)
        self.repository = QLineEdit(settings.get("github_repository", "bryagisubizo-bit/arthur"))
        self.repository.setPlaceholderText("owner/repository")
        release_layout.addRow("Repository:", self.repository)
        self.github_token = QLineEdit(get_secret("Updates"))
        self.github_token.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_token.setPlaceholderText("Optional: scoped token for a private repository")
        release_layout.addRow("Optional private token:", self.github_token)
        self.manual_only = QCheckBox("Manual check only — no background polling")
        self.manual_only.setChecked(True)
        self.manual_only.setEnabled(False)
        release_layout.addRow(self.manual_only)
        self.release_record = None
        self.asset_choice = QComboBox()
        self.asset_choice.setEnabled(False)
        release_layout.addRow("Release asset:", self.asset_choice)
        self.download_button = QPushButton("Approve selected download")
        self.download_button.setEnabled(False)
        self.download_button.clicked.connect(self.download_selected_asset)
        release_layout.addRow("Verified download:", self.download_button)
        self.check_status = QLabel("No release metadata checked during this session.")
        self.check_status.setObjectName("safetyBoundary")
        self.check_status.setWordWrap(True)
        release_layout.addRow(self.check_status)
        layout.addWidget(release_group)

        actions = QHBoxLayout()
        save_button = QPushButton("Save update source")
        save_button.clicked.connect(self.save)
        check_button = QPushButton("Check GitHub Releases now")
        check_button.setObjectName("primaryButton")
        check_button.clicked.connect(self.check_now)
        tutorial_button = QPushButton("Show first-run tutorial")
        tutorial_button.clicked.connect(self.show_tutorial)
        actions.addWidget(save_button)
        actions.addWidget(check_button)
        actions.addStretch()
        actions.addWidget(tutorial_button)
        layout.addLayout(actions)
        layout.addStretch()

    def show_tutorial(self):
        if self.tutorial_callback is not None:
            self.tutorial_callback()

    def save(self, show_notice=True):
        try:
            repository = validate_repository(self.repository.text())
        except ValueError as error:
            QMessageBox.warning(self, "Repository required", str(error))
            return False
        token = self.github_token.text().strip()
        if token and not set_secret("Updates", token):
            QMessageBox.warning(self, "Secure storage unavailable", "Arthur could not store the GitHub token in Windows Credential Manager.")
            return False
        self.config.setdefault("updates", {}).update({
            "github_repository": repository,
            "manual_check_only": True,
        })
        self.config["integrations"]["Updates"] = {
            "provider": "GitHub Releases",
            "enabled": True,
            "manual_check_only": True,
            "repository": repository,
        }
        self.save_callback()
        if show_notice:
            QMessageBox.information(self, "Updates saved", "Arthur will check GitHub only when the user selects the manual check button. No download or installation is enabled.")
        return True

    def check_now(self):
        if not self.save(show_notice=False):
            return
        choice = QMessageBox.question(
            self,
            "Confirm manual GitHub check",
            "Arthur will make one HTTPS request to GitHub for release metadata only. It will not download an asset, install software, or schedule a retry. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if choice != QMessageBox.StandardButton.Yes:
            return
        result = fetch_latest_release(self.repository.text(), get_secret("Updates"))
        if not result.get("ok"):
            self.check_status.setText(result.get("message", "Arthur could not read release metadata. No update was downloaded."))
            return
        release = result["release"]
        self.release_record = release
        self.asset_choice.clear()
        asset_lines = []
        for asset in release["assets"][:4]:
            size_mb = asset["size"] / (1024 * 1024)
            digest_note = "SHA-256 available" if str(asset.get("digest", "")).startswith("sha256:") else "SHA-256 unavailable — download blocked"
            asset_lines.append(f"• {asset['name']} ({size_mb:.1f} MB) — {digest_note}")
        for asset in release["assets"]:
            size_mb = asset["size"] / (1024 * 1024)
            self.asset_choice.addItem(f"{asset['name']} ({size_mb:.1f} MB)", asset["name"])
        self.asset_choice.setEnabled(bool(release["assets"]))
        self.download_button.setEnabled(bool(release["assets"]))
        assets = "\n".join(asset_lines) or "No installer assets are attached to this release."
        self.config.setdefault("updates", {})["last_checked_release"] = release["tag"]
        self.save_callback()
        self.check_status.setText(f"Release metadata read for {release['tag']}. Arthur did not download or run anything.")
        QMessageBox.information(
            self,
            "GitHub Release found",
            f"{release['name']}\nVersion: {release['tag']}\nPublished: {release['published_at']}\n\nAssets:\n{assets}\n\nNo asset was downloaded. Select an asset and approve its download separately; Arthur verifies GitHub's SHA-256 digest before it can offer a separate Windows installer handoff.",
        )

    def download_selected_asset(self):
        if not self.release_record:
            QMessageBox.warning(self, "Check releases first", "Read one release record before selecting an asset. Arthur will not guess an update URL.")
            return
        asset_name = self.asset_choice.currentData()
        if not asset_name:
            QMessageBox.warning(self, "Asset required", "Select one release asset to continue.")
            return
        download_choice = QMessageBox.question(
            self,
            "Approve release download",
            f"Arthur will download only this asset:\n\n{asset_name}\n\nIt will verify the SHA-256 digest supplied in the GitHub release metadata. It will not launch or install anything yet. Download now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if download_choice != QMessageBox.StandardButton.Yes:
            self.check_status.setText("Selected release asset was not downloaded.")
            return
        self.check_status.setText("Downloading the selected release asset and verifying SHA-256. Arthur will not launch it automatically.")
        QApplication.processEvents()
        result = download_release_asset(self.release_record, str(asset_name), approved=True)
        if not result.get("ok"):
            self.check_status.setText(result.get("message", "The selected update was not downloaded."))
            QMessageBox.warning(self, "Update download not completed", self.check_status.text())
            return
        verified_path = result["path"]
        self.check_status.setText(f"Verified download ready: {verified_path}. Arthur has not run it.")
        handoff_choice = QMessageBox.question(
            self,
            "Approve installer handoff",
            f"The SHA-256-verified file is ready:\n\n{verified_path}\n\nAsk Windows to open it now? The installer may show its own prompts, and Arthur will not elevate, accept, or answer them.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if handoff_choice != QMessageBox.StandardButton.Yes:
            self.check_status.setText(f"Verified installer retained locally without launch: {verified_path}")
            return
        handoff = handoff_verified_installer(verified_path, approved=True)
        self.check_status.setText(handoff.get("message", "Installer handoff did not complete."))
        if not handoff.get("ok"):
            QMessageBox.warning(self, "Installer not opened", self.check_status.text())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.cards = {}
        self.tray = None
        self.voice_runtime = VoiceRuntime()
        saved_voice = self.config.get("voice", {})
        self.voice_runtime.configure(
            voice_id=saved_voice.get("local_voice_id", ""),
            rate=saved_voice.get("rate", 175),
            volume=saved_voice.get("volume", 100) / 100,
            pitch=saved_voice.get("pitch", 0),
        )
        self.voice_studio = None
        self.setWindowTitle("Arthur — Desktop AI Assistant")
        self.setWindowIcon(QIcon(str(bundled_path("assets/arthur_hawk.ico"))))
        self.setMinimumSize(1240, 800)
        self.build_ui()
        self.apply_appearance(self.config.get("appearance", {}))
        self.build_tray()
        if not self.config.get("setup_complete") or not self.config.get("profile", {}).get("native_language") or not self.config.get("voice", {}).get("speech_recognition_route"):
            QTimer.singleShot(250, self.show_first_run)
        elif self.config.get("privacy", {}).get("spoken_only", True) and self.config.get("voice", {}).get("arrival_greeting_enabled", False):
            QTimer.singleShot(650, self.play_arrival_greeting)

    def build_ui(self):
        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(central)

        nav = QFrame()
        nav.setObjectName("nav")
        nav.setFixedWidth(258)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(20, 24, 16, 18)
        nav_layout.setSpacing(7)
        brand_row = QHBoxLayout()
        hawk_mark = QLabel()
        hawk_mark.setPixmap(QPixmap(str(bundled_path("assets/arthur_hawk.svg"))).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        hawk_mark.setObjectName("hawkMark")
        brand = QLabel("ARTHUR")
        brand.setObjectName("brand")
        brand_row.addWidget(hawk_mark)
        brand_row.addWidget(brand)
        brand_row.addStretch()
        subtitle = QLabel("ORBITAL COMMAND ATELIER")
        subtitle.setObjectName("brandSub")
        rail_state = QLabel("● WINDOWS DESKTOP / LOCAL-FIRST")
        rail_state.setObjectName("railState")
        nav_layout.addLayout(brand_row)
        nav_layout.addWidget(subtitle)
        nav_layout.addWidget(rail_state)
        nav_layout.addSpacing(22)
        self.nav_list = QListWidget()
        self.nav_labels = [
            "Command desk", "Tools & routing", "Spatial workspace", "Symptom support", "Reviewed commands", "Voice studio", "Voice signal", "Conduct & memory",
            "Private notes", "Autonomy & change", "Language library", "API vault", "System sensors", "Permissions", "Updates", "Profile",
        ]
        for item in self.nav_labels:
            self.nav_list.addItem(QListWidgetItem(item))
        self.nav_list.currentRowChanged.connect(self.change_page)
        nav_layout.addWidget(self.nav_list, 1)
        footer = QLabel("WINDOWS 11 // CONSENT-FIRST\nLOCAL SESSIONS // REVIEWED ACTIONS")
        footer.setObjectName("muted")
        footer.setWordWrap(True)
        nav_layout.addWidget(footer)
        root.addWidget(nav)

        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 20, 30, 26)
        content_layout.setSpacing(18)
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(0, 0, 0, 12)
        topbar_copy = QVBoxLayout()
        self.workspace_eyebrow = QLabel("ARTHUR / LOCAL WORKSPACE")
        self.workspace_eyebrow.setObjectName("eyebrow")
        self.workspace_title = QLabel("Command desk")
        self.workspace_title.setObjectName("topbarTitle")
        topbar_copy.addWidget(self.workspace_eyebrow)
        topbar_copy.addWidget(self.workspace_title)
        topbar_layout.addLayout(topbar_copy)
        topbar_layout.addStretch()
        readiness = QLabel("● CONSENT GATES ACTIVE")
        readiness.setObjectName("topbarStatus")
        topbar_layout.addWidget(readiness)
        content_layout.addWidget(topbar)
        self.pages = QStackedWidget()
        self.dashboard = Dashboard(self.config, self.voice_runtime, self.save_all, self.open_voice_signal, self.open_spatial_room)
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(ToolsRoutingPage(self.config))
        self.spatial_page = SpatialWorkspacePage(self.config, self.save_all)
        self.pages.addWidget(self.spatial_page)
        self.symptom_support_page = SymptomSupportPage(self.voice_runtime)
        self.pages.addWidget(self.symptom_support_page)
        self.commands_page = ReviewedCommandsPage(self.config, self.save_all)
        self.pages.addWidget(self.commands_page)
        self.voice_studio = VoiceStudioPage(self.config, self.save_all, self.voice_runtime, self.apply_appearance)
        self.pages.addWidget(self.voice_studio)
        self.voice_signal_page = VoiceSignalPage(self.config)
        self.pages.addWidget(self.voice_signal_page)
        self.voice_studio.wake_word_detected.connect(self.open_voice_signal_from_wake_word)
        self.voice_studio.audio_level.connect(self.voice_signal_page.set_level)
        self.conduct_page = ConductMemoryPage(self.config, self.save_all)
        self.pages.addWidget(self.conduct_page)
        self.pages.addWidget(PrivateNotesPage(self.config, self.save_all))
        self.pages.addWidget(AutonomyChangePage(self.config, self.save_all, self.apply_appearance))
        self.language_library_page = LanguageLibraryPage(self.config, self.save_all)
        self.pages.addWidget(self.language_library_page)
        self.integration_page = self.build_integrations_page()
        self.pages.addWidget(self.integration_page)
        self.sensors_page = SystemSensorsPage(self.config, self.save_all)
        self.pages.addWidget(self.sensors_page)
        self.permissions_page = PermissionsPage(self.config, self.save_all)
        self.pages.addWidget(self.permissions_page)
        self.updates_page = UpdatesPage(self.config, self.save_all, self.show_tutorial)
        self.pages.addWidget(self.updates_page)
        self.profile_page = ProfilePage(self.config, self.save_all)
        self.pages.addWidget(self.profile_page)
        self.page_scroll = QScrollArea()
        self.page_scroll.setWidgetResizable(True)
        # Only SpatialWorkspacePage owns horizontal swipe and pinch semantics.
        # Other rooms retain conventional vertical scrolling and never expose a
        # horizontal workspace scrollbar that could be mistaken for navigation.
        self.page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.page_scroll.setObjectName("workspaceScroll")
        self.page_scroll.setWidget(self.pages)
        content_layout.addWidget(self.page_scroll, 1)
        root.addWidget(content, 1)
        self.nav_list.setCurrentRow(0)

    def build_integrations_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        heading = QHBoxLayout()
        title = QLabel("API Vault")
        title.setObjectName("pageTitle")
        heading.addWidget(title)
        heading.addStretch()
        save_all = QPushButton("Save all integrations")
        save_all.clicked.connect(self.save_integrations)
        heading.addWidget(save_all)
        outer.addLayout(heading)
        note = QLabel("Developer-managed capability rooms. Arthur stores approved desktop credentials through the operating-system credential manager and does not invent a provider when a required resource is missing. Security and high-impact rooms remain review-required.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        outer.addWidget(note)
        defensive_gate = QGroupBox("Defensive intelligence lookup gate")
        defensive_layout = QVBoxLayout(defensive_gate)
        self.defensive_lookup_enabled = QCheckBox("Enable passive defensive context lookups only")
        self.defensive_lookup_enabled.setChecked(self.config.setdefault("security", {}).get("defensive_lookup_enabled", False))
        self.defensive_lookup_enabled.toggled.connect(self.set_defensive_lookup_enabled)
        defensive_note = QLabel("When enabled, Arthur may only prepare a single user-requested enrichment lookup after you approve that exact item. Active scans, exploitation, credential testing, malware handling, and automatic actions remain unavailable.")
        defensive_note.setWordWrap(True)
        defensive_note.setObjectName("safetyBoundary")
        defensive_layout.addWidget(self.defensive_lookup_enabled)
        defensive_layout.addWidget(defensive_note)
        outer.addWidget(defensive_gate)
        add_custom = QPushButton("Add reviewed provider room")
        add_custom.setObjectName("primaryButton")
        add_custom.clicked.connect(self.add_custom_integration)
        outer.addWidget(add_custom)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        self.integration_grid = grid
        grid.setSpacing(16)
        saved = self.config.get("integrations", {})
        for index, (label, providers) in enumerate(PROVIDER_OPTIONS.items()):
            card = IntegrationCard(label, providers, saved.get(label, {}))
            card.changed.connect(lambda data, name=label: self.integration_changed(name, data))
            self.cards[label] = card
            grid.addWidget(card, index // 2, index % 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        scroll.setWidget(container)
        outer.addWidget(scroll, 1)
        return page

    def add_custom_integration(self):
        dialog = CustomIntegrationDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        label = f"Custom · {dialog.name.text().strip()}"
        if label in self.cards:
            QMessageBox.warning(self, "Already added", "An integration with this name already exists.")
            return
        saved = {"provider": "Custom API", "endpoint": dialog.endpoint.text().strip(), "model": dialog.auth.currentText(), "enabled": False}
        card = IntegrationCard(label, ["Select provider", "Custom API", "Custom MCP / HTTP"], saved)
        card.changed.connect(lambda data, name=label: self.integration_changed(name, data))
        self.cards[label] = card
        index = len(self.cards) - 1
        self.integration_grid.addWidget(card, index // 2, index % 2)
        self.config["integrations"][label] = saved
        save_config(self.config)

    def integration_changed(self, name, data):
        self.config["integrations"][name] = data
        save_config(self.config)

    def save_integrations(self):
        for name, card in self.cards.items():
            self.config["integrations"][name] = card.payload()
        save_config(self.config)
        QMessageBox.information(self, "Integrations saved", "Developer integration settings have been saved.")

    def set_defensive_lookup_enabled(self, enabled):
        self.config.setdefault("security", {})["defensive_lookup_enabled"] = enabled
        save_config(self.config)

    def save_all(self):
        save_config(self.config)

    def change_page(self, index):
        if index >= 0:
            if self.nav_labels[index] == "Spatial workspace" and not self.spatial_page.request_access():
                current = self.pages.currentIndex()
                self.nav_list.blockSignals(True)
                self.nav_list.setCurrentRow(current)
                self.nav_list.blockSignals(False)
                return
            self.pages.setCurrentIndex(index)
            self.workspace_title.setText(self.nav_labels[index])

    def open_spatial_room(self):
        """Open the protected room after an explicit command review and local verification."""
        if not self.spatial_page.request_access():
            return False
        spatial_index = self.nav_labels.index("Spatial workspace")
        self.nav_list.setCurrentRow(spatial_index)
        return True

    def open_voice_signal(self, message="Command session active"):
        """Show the local visualizer as an explicit command-session response."""
        self.voice_signal_page.activate(message)
        signal_index = self.nav_labels.index("Voice signal")
        self.nav_list.setCurrentRow(signal_index)

    def open_voice_signal_from_wake_word(self, wake_word):
        self.open_voice_signal(f"Wake word detected: {wake_word}")

    def show_first_run(self):
        dialog = FirstRunDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            result = dialog.completed
            # Signal has already delivered the data only to connected listeners; read fields directly.
            self.config["profile"].update({
                "display_name": dialog.name.text().strip(),
                "pronunciation": dialog.pronunciation.text().strip(),
                "native_language": selected_primary_language(dialog.native_language),
                "additional_languages": [x.strip() for x in dialog.additional.text().split(",") if x.strip()],
                "active_conversation_language": selected_primary_language(dialog.native_language),
                "music_source": dialog.music.currentText(),
                "wake_word": dialog.wake_word.text().strip() or "Arthur",
                "title": dialog.title.text().strip() or "Sir",
            })
            self.config["privacy"]["spoken_only"] = dialog.spoken_only.isChecked()
            self.config.setdefault("voice", {})["speech_recognition_route"] = selected_speech_recognition_route(dialog.speech_route)
            self.config["setup_complete"] = True
            self.save_all()
            route = SPEECH_RECOGNITION_ROUTES[self.config["voice"]["speech_recognition_route"]]["label"]
            QMessageBox.information(self, "Arthur profile configured", f"Welcome, {self.config['profile']['display_name']}. Arthur is configured for {self.config['profile']['native_language']} with {route}. Complete its separate readiness and listening approvals before Arthur can understand a spoken command.")
            self.show_tutorial()
            if self.config.get("privacy", {}).get("spoken_only", True) and self.config.get("voice", {}).get("first_interaction_greeting_enabled", True):
                QTimer.singleShot(300, self.play_first_interaction_introduction)
        else:
            self.config["setup_complete"] = False
            self.save_all()

    def show_tutorial(self):
        FirstRunTutorialDialog(self).exec()

    def play_arrival_greeting(self):
        """Deliver one optional local greeting; never starts the listener or contacts a provider."""
        if greeting_is_quiet(self.config):
            self.dashboard.output.append("Arthur: Local Do Not Disturb is active; optional arrival greeting suppressed.")
            return
        result = self.voice_runtime.speak(render_greeting_script(self.config, "opening"))
        if result.ready:
            self.dashboard.output.append("Arthur: Optional local arrival greeting delivered.")

    def play_first_interaction_introduction(self):
        """Introduce Arthur after completed setup without activating the microphone or any provider."""
        if greeting_is_quiet(self.config):
            self.dashboard.output.append("Arthur: Local Do Not Disturb is active; first-interaction introduction suppressed.")
            return
        result = self.voice_runtime.speak(render_greeting_script(self.config, "introduction"))
        if result.ready:
            self.dashboard.output.append("Arthur: Optional first-interaction introduction delivered.")

    def build_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon(str(bundled_path("assets/arthur_hawk.ico"))))
        self.tray.setToolTip("Arthur — desktop intelligence")
        menu = QMenu(self)
        show_action = QAction("Show Arthur", self)
        show_action.triggered.connect(self.restore_from_tray)
        pause_action = QAction("Pause local listeners", self)
        pause_action.triggered.connect(self.pause_wake_word_listener)
        exit_action = QAction("Exit Arthur", self)
        exit_action.triggered.connect(self.exit_arthur)
        menu.addAction(show_action)
        menu.addAction(pause_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.restore_from_tray() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

    def restore_from_tray(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()
        if self.config.get("privacy", {}).get("spoken_only", True) and self.config.get("voice", {}).get("arrival_greeting_enabled", True):
            QTimer.singleShot(300, self.play_arrival_greeting)

    def pause_wake_word_listener(self):
        was_running = self.voice_studio.pause_listener(persist=True)
        self.spatial_page.stop_local_gestures()
        message = "Local wake-word listening and air gestures have been paused." if was_running else "Local listeners are paused."
        if self.tray is not None:
            self.tray.showMessage("Arthur listening", message)
        QMessageBox.information(self, "Wake-word listening", message)

    def exit_arthur(self):
        self.voice_studio.stop_listener()
        self.spatial_page.stop_local_gestures()
        if self.tray is not None:
            self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        self.spatial_page.stop_local_gestures()
        if self.config.get("autonomy", {}).get("background_ready", False) and self.tray is not None:
            event.ignore()
            self.hide()
            listening = self.voice_studio.listener is not None and self.voice_studio.listener.running
            detail = "Local wake-word listening remains active because you explicitly enabled it for this session." if listening else "Wake-word listening is paused."
            self.tray.showMessage("Arthur is in the tray", f"Use the tray menu to restore Arthur, pause listening, or exit it. {detail}")
            return
        self.voice_studio.stop_listener()
        event.accept()

    def apply_appearance(self, appearance):
        apply_theme(QApplication.instance(), appearance)


def apply_theme(app, appearance=None):
    appearance = appearance or {}
    mode = appearance.get("color_mode", "Cobalt")
    palette = {
        "Cobalt": ("#2f6bff", "#55d9ff", "#10244a"),
        "Tide": ("#12a89b", "#62e7da", "#103f43"),
        "Amber": ("#d9871b", "#ffd276", "#483016"),
    }
    accent, glow, accent_surface = palette.get(mode, palette["Cobalt"])
    font_size = {"Standard": "13px", "Large": "15px", "Extra large": "17px"}.get(appearance.get("type_scale", "Standard"), "13px")
    app.setStyleSheet(f"""
        QWidget {{ background: #050b18; color: #e5f1ff; font-family: 'Segoe UI'; font-size: {font_size}; }}
        QMainWindow {{ background: #050b18; }}
        #nav {{ background: #070f1f; border-right: 1px solid #1b3455; }}
        #content {{ background: #050b18; }}
        #brand {{ color: {glow}; font-size: 32px; font-weight: 800; letter-spacing: 7px; }}
        #brandSub, #eyebrow, #metricLabel, #metricTag, #routeState {{ color: #7496b8; font-size: 10px; font-weight: 700; letter-spacing: 2px; }}
        #railState {{ color: {glow}; font-size: 10px; margin-top: 7px; }}
        #pageTitle {{ color: #f3f8ff; font-size: 28px; font-weight: 700; }}
        #topbarTitle {{ color: #eff7ff; font-size: 19px; font-weight: 700; }}
        #topbar {{ border-bottom: 1px solid #173151; }}
        #topbarStatus {{ color: #74e5ad; background: #0d2926; border: 1px solid #1f655b; border-radius: 12px; padding: 6px 10px; font-size: 10px; font-weight: 700; }}
        #dialogTitle {{ color: #a8e7ff; font-size: 20px; font-weight: 600; }}
        #muted {{ color: #8aa6c1; }}
        QListWidget {{ background: transparent; border: none; outline: none; }}
        QListWidget::item {{ padding: 11px 12px; margin: 2px 0; color: #8aa6c1; border-radius: 7px; }}
        QListWidget::item:hover {{ background: #0d1c32; color: #cbe9ff; }}
        QListWidget::item:selected {{ background: {accent_surface}; color: #ffffff; border-left: 3px solid {glow}; padding-left: 9px; }}
        QLineEdit, QComboBox, QTextEdit, QSpinBox {{ background: #09172b; border: 1px solid #1c4267; border-radius: 7px; padding: 10px; color: #e5f1ff; selection-background-color: {accent}; }}
        QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{ border: 1px solid {glow}; }}
        #commandInput {{ min-height: 26px; font-size: 14px; }}
        QPushButton {{ background: #102a48; border: 1px solid #2c5f8c; border-radius: 7px; padding: 9px 14px; color: #e8f6ff; font-weight: 600; }}
        QPushButton:hover {{ background: #193e66; border-color: {glow}; }}
        QPushButton:pressed {{ background: #0d2239; }}
        #primaryButton {{ background: {accent}; border-color: {accent}; color: white; }}
        #primaryButton:hover {{ background: {glow}; color: #04101f; }}
        QCheckBox {{ spacing: 8px; padding: 5px 0; }}
        QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid #2c5f8c; border-radius: 3px; background: #09172b; }}
        QCheckBox::indicator:checked {{ background: {accent}; border-color: {glow}; }}
        QGroupBox {{ background: #081425; border: 1px solid #1a3b5d; border-radius: 10px; margin-top: 13px; padding: 18px 15px 15px 15px; color: {glow}; font-weight: 700; }}
        QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; }}
        #heroPanel {{ background: #091a33; border: 1px solid #24518a; border-radius: 13px; padding: 18px; }}
        #heroTitle {{ color: #ffffff; font-size: 26px; font-weight: 700; }}
        #metricCard, #routeCard, #integrationCard, #ledgerPanel, #voiceSignal, #workspaceHeading {{ background: #081525; border: 1px solid #1a3c61; border-radius: 10px; }}
        #metricCard {{ min-height: 105px; padding: 7px; }}
        #metricValue {{ color: {glow}; font-size: 30px; font-weight: 700; }}
        #metricTag {{ color: #527ba0; }}
        #routeCard {{ min-height: 105px; padding: 8px; }}
        #routeState {{ color: {glow}; }}
        #integrationCard {{ padding: 7px; }}
        #cardTitle {{ color: #d9f0ff; font-size: 15px; font-weight: 700; }}
        #ledgerPanel {{ padding: 10px; }}
        #ledgerOutput {{ background: #06101e; border: 1px solid #14375a; }}
        #commandResult, #safetyBoundary {{ background: #0a1b2f; border-left: 3px solid {accent}; color: #c7ddf1; padding: 10px; border-radius: 5px; }}
        #safetyBoundary {{ border-left-color: #ffc663; color: #ffe2ae; }}
        #voiceSignal {{ min-height: 210px; padding: 14px; }}
        #voiceOrb {{ color: {glow}; border: 2px solid {accent}; border-radius: 78px; min-width: 150px; max-width: 150px; min-height: 150px; max-height: 150px; font-size: 17px; font-weight: 700; letter-spacing: 2px; background: #071426; }}
        #workspaceHeading {{ padding: 12px; }}
        #statusOn {{ color: #70e6a6; font-weight: 700; }}
        #statusOff {{ color: #7b94aa; }}
        #statusWarn {{ color: #ffc76b; font-weight: 700; }}
        QScrollArea, #workspaceScroll {{ border: none; background: transparent; }}
        QScrollBar:vertical {{ background: #07111f; width: 10px; margin: 0; }}
        QScrollBar::handle:vertical {{ background: #234a70; min-height: 30px; border-radius: 5px; }}
    """)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    apply_theme(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
