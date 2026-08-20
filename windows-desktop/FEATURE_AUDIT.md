# Arthur Capability Audit

## Reading This Register

This register maps the supplied 63-part advanced-assistant brief to the **Arthur** project as it exists today. It deliberately separates an implemented Windows-prototype behavior from an interactive browser-preview surface and from a capability that still requires a provider or a native adapter. Arthur is a Windows-first, voice-oriented assistant designed around limited tool plans, explicit consent, and protected local credential storage.

| Status | Meaning |
|---|---|
| **Implemented** | Present in the Python/PySide6 prototype or its tested supporting modules. |
| **Previewed** | Present as an interactive browser interface or policy demonstration; it does not invoke devices, providers, or the operating system. |
| **Scaffolded** | A documented adapter or extension boundary exists, but a live provider or native implementation is not connected. |
| **Planned** | A required feature identified in the brief but not yet implemented. |
| **Excluded** | Deliberately unavailable because it conflicts with Arthur’s safety boundary. |

## 63-Category Implementation Register

| # | Capability from the brief | Status | Current Arthur coverage and boundary |
|---:|---|---|---|
| 1 | Arthur identity and product framing | **Implemented** | The Windows prototype and browser preview are named Arthur, not JARVIS. |
| 2 | Windows 11 as primary platform | **Implemented** | Desktop prototype targets Windows behavior and includes Windows-specific reviewed diagnostics. |
| 3 | 8 GB RAM / modest CPU practicality | **Scaffolded** | The prototype is intentionally modular; real local-model and provider choices still need performance testing on the target machine. |
| 4 | First-run authorisation | **Implemented** | The preview and desktop flow collect identity, language, pronunciation, and consent choices. |
| 5 | Preferred name and title | **Implemented** | Profile controls support a name, title, and pronunciation note. |
| 6 | Direct, calm, respectful conduct | **Implemented** | Demeanor controls and the conduct policy describe directness without hostility. |
| 7 | Dry British-style wit | **Previewed** | A separately switchable, restrained wit preference is represented; live generation requires an AI provider. |
| 8 | Multilingual preference | **Implemented** | Kinyarwanda, English, French, and Kiswahili are selectable profile languages. |
| 9 | Natural language switching | **Scaffolded** | The routing/UI is present; live recognition and response quality depend on selected speech and AI providers. |
| 10 | Learning additional language or sayings | **Previewed** | Opt-in language and phrasing memory controls are visible and reviewable. |
| 11 | Conversation intelligence | **Scaffolded** | Provider cards cover main and secondary reasoning; no provider credential is embedded. |
| 12 | Voice-first interaction | **Previewed** | The browser UI models voice-first interactions and spoken replies; it does not capture audio. |
| 13 | Refined spoken voice | **Scaffolded** | Voice-provider configuration is represented; synthesis is not yet connected. |
| 14 | Microphone selection and calibration | **Previewed** | Voice Studio now shows a device-consent switch and a five-call calibration placeholder. |
| 15 | Speaker/output selection | **Previewed** | Voice Studio exposes a spoken-replies device control as a desktop-only placeholder. |
| 16 | Wake word “Arthur” | **Implemented** | A consent-first local openWakeWord service is included in the desktop prototype. |
| 17 | User-approved wake-word installation | **Implemented** | Installation asks for consent before the desktop installer may run `pip install openwakeword`. |
| 18 | Background/tray listening | **Implemented** | The desktop design specifies hide-to-tray behavior and visible pause/stop states. |
| 19 | Listening accuracy controls | **Scaffolded** | The browser flow describes signal indication and calibration; empirical device tuning is still required. |
| 20 | Spoken-only response by default | **Previewed** | The command desk presents spoken responses as default and asks before visual panels. |
| 21 | Visual/holographic workspace | **Previewed** | The browser preview includes the Holographic Data Workspace; it does not render or upload private content. |
| 22 | Visual analytics | **Previewed** | Original orbital telemetry and dashboard shapes are available as illustrative interface surfaces. |
| 23 | CPU, memory, disk, and local network checks | **Implemented** | Reviewed diagnostic templates and available local telemetry cover selected safe readings. |
| 24 | GPU and temperature awareness | **Planned** | Arthur does not fabricate unsupported GPU or temperature readings; native sensor adapters need validation. |
| 25 | Plain-language bottleneck explanation | **Scaffolded** | The UI and conduct model support explanations; live diagnosis needs actual telemetry and an AI provider. |
| 26 | Natural-language PC task planning | **Implemented** | `command_planner.py` maps recognised intents to fixed reviewed command templates. |
| 27 | Windows diagnostic commands | **Implemented** | Selected `systeminfo`, `whoami`, `ipconfig`, `tasklist`, disk, and connectivity templates are available. |
| 28 | WSL/Linux diagnostic support | **Implemented** | Benign commands are constrained to an approved local WSL distribution. |
| 29 | Kali/Linux command knowledge | **Excluded** | Arthur only supports benign local WSL diagnostics; it does not provide attack, scanning, exploitation, or evasion workflows. |
| 30 | Raw natural language to shell | **Excluded** | Arthur never passes raw generated text to a shell or command interpreter. |
| 31 | Command risk tiers | **Implemented** | Low-risk diagnostics, confirmation-gated actions, and blocked requests are modelled and tested. |
| 32 | Exact pre-execution command preview | **Implemented** | The plan may display the fixed command and its risk before a desktop action proceeds. |
| 33 | Application launch/focus/close/restart | **Previewed** | Tools & Routing provides desktop-only placeholders; native allowlisted adapters and foreground checks remain required. |
| 34 | Scrolling and desktop manipulation | **Planned** | Requires a carefully permissioned Windows input adapter and visible target verification. |
| 35 | Clipboard control | **Planned** | Requires a local, user-approved adapter and sensitive-data rules. |
| 36 | File organisation and local search | **Planned** | Requires file-scope selection, local indexing, and confirmation for consequential changes. |
| 37 | Document understanding/OCR | **Previewed** | File-analysis consent is visible; a local or provider-backed analysis adapter is still required. |
| 38 | Screen analysis | **Previewed** | Screen-analysis consent is visible; no screen capture occurs in the browser preview. |
| 39 | Camera or facial verification | **Scaffolded** | Luxand is offered as an optional provider; camera use and identity processing must remain separately authorised. |
| 40 | Internet research without opening a browser | **Scaffolded** | A research provider can be configured; the preview explains returned spoken summaries without performing searches. |
| 41 | Parallel research and large-document summaries | **Planned** | Requires provider quotas, source disclosure, user-selected inputs, and a bounded task runner. |
| 42 | Calendar briefing and conflict detection | **Previewed** | A safe day-brief request and collision examples are visible; calendar OAuth is not connected. |
| 43 | Email and message operations | **Planned** | Requires provider OAuth, scope minimisation, drafts, and confirmation before sending. |
| 44 | User accounts and browser registration | **Scaffolded** | Supabase Project URL and Publishable Key fields are documented; no production backend is connected. |
| 45 | Protected API-key storage | **Implemented** | `secure_store.py` uses OS credential-manager integration; no credentials ship in source or preview. |
| 46 | Developer-controlled provider vault | **Implemented** | Parallel provider configuration, a custom HTTPS integration flow, and an acquisition guide are included. |
| 47 | Custom API integrations | **Scaffolded** | Plug-in/custom API shapes exist; real endpoints require a reviewed provider configuration and scope. |
| 48 | Plug-in permissions | **Implemented** | The plug-in API requires a declared manifest and permissions before extension registration. |
| 49 | Visible tool-routing architecture | **Previewed** | Tools & Routing now exposes conversation, PC control, files/screen, web, vision, automations, and sensitive-action paths. |
| 50 | Global privacy lock | **Previewed** | One switch visibly blocks microphone, camera, cloud AI, web, memory, and screen analysis in preview state. |
| 51 | Permission register | **Implemented** | Interactive controls explain automation, health, research, and smart-home consent; consequential actions stay confirmation-gated. |
| 52 | Self-diagnostics | **Previewed** | A readiness dashboard separates desktop-adapter requirements from safe, configured boundaries. |
| 53 | Command history/audit | **Previewed** | The preview contains a clearable local-audit shape with intent, result, and deferral metadata. |
| 54 | Automation registry | **Previewed** | Named workflow rows show trigger, owner, scope, last state, individual pause, and pause-all controls. |
| 55 | Scheduled reminders/workflows | **Planned** | A real local scheduler still needs to enforce owner, trigger, permission, pause, and audit constraints. |
| 56 | Proactive lifestyle learning | **Previewed** | Opt-in routines, phrasing, and schedule signals are represented; no silent collection is implemented. |
| 57 | Safe long-term memory management | **Previewed** | The interface states review, edit, export, erase, and secret-exclusion requirements; storage implementation needs completion. |
| 58 | Smart-home/Home Assistant control | **Scaffolded** | Optional discovery and consent gates are represented; a real adapter needs a homeowner-created token and scoped controls. |
| 59 | Music request distinction: Play vs Sing | **Scaffolded** | The music adapter distinguishes provider-backed playback; original-song generation requires a separately approved music model/provider. |
| 60 | Update checks and install approval | **Implemented** | Update settings require signed releases and explicit approval before download or installation. |
| 61 | Cloud-managed update channel | **Planned** | A signed release feed and version verification service have not been connected. |
| 62 | Installer and source distribution | **Implemented** | Inno Setup configuration, build scripts, and a credential-free source bundle are included. |
| 63 | Intrusion, malware, weapon, credential, or bypass capability | **Excluded** | Arthur refuses security bypassing, network scanning, credential extraction, malware, destructive disk activity, weapons, and arbitrary shell execution. |

## Non-Negotiable Safety Boundary

> **Design rule:** User intent is translated into a limited, transparent tool plan. Arthur never passes generated text directly to a command interpreter.

Arthur does not provide unauthorized access, credential harvesting, cookie or session theft, security-control evasion, public/private network scanning, exploitation, malware, ransomware, phishing, destructive disk activity, weapon control, or arbitrary shell execution.

## Current Safe Build Order

1. Connect regenerated AI, speech-to-text, text-to-speech, and research credentials only through protected adapters.
2. Add allowlisted Windows-native tools for applications, file selection, clipboard use, screen analysis, and accessibility actions with foreground and confirmation controls.
3. Build the local task scheduler behind the visible automation registry, including owner, trigger, scope, pause, and audit enforcement.
4. Add selected-file and selected-screen analysis only after clear transfer notices and local-first/provider-specific privacy controls are tested.
5. Expand the command registry only with dedicated regression tests for fixed templates, risk tiers, and blocked language.
