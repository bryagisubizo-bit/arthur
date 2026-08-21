# Arthur Application Bridge Architecture

> **Purpose.** Arthur’s application bridge is a local Windows accessibility client for a user-approved app. It is not a screen recorder, keylogger, password reader, security-prompt bypass, browser-login bypass, background agent, or remote-control service.

## Component tree

```text
Arthur Spatial Workspace (visible review controls)
├── Approval ledger (per app, expiring, locally stored preference)
├── Application bridge (dormant until a visible user action)
│   ├── Window discovery (approved app only, one manual sample)
│   ├── Accessible-tree summary (named controls only)
│   ├── Navigation-plan builder (read-only preview)
│   ├── Action confirmation gate (one action at a time)
│   └── Emergency stop / local activity record
└── Optional Windows UI Automation adapter
    └── `pywinauto` UIA backend or an equivalent native UIA client
```

## Consent and execution boundary

Arthur starts with an empty approval ledger. A user must select a visible application, review its identity, and approve a narrow scope before Arthur may take a one-time accessibility-tree summary. The summary includes only control name, control type, availability, and bounded identifiers required for a navigation plan. It deliberately excludes password values, clipboard contents, typed content, screen pixels, audio, camera frames, security prompts, and controls outside the approved app.

Each consequential operation has its own confirmation. Reading an accessible-control summary, selecting a control, invoking a button, typing text, selecting a file, using the clipboard, sending communication, or sharing data are separate scopes. The initial implementation ends at **execution readiness**; it does not invoke controls or type into apps. A visible emergency stop clears all active session approvals and cancels the pending plan.

## Lightweight Windows implementation

Microsoft describes a UI Automation client as an application that accesses accessible UI-element information or controls an application through the UI Automation tree. Its guidance also notes that retrieving properties individually can create separate interprocess calls, while caching a small set of properties reduces that overhead.[1]

Arthur therefore performs no continuous event subscription or desktop-wide scan. It uses one user-requested sample, limits the tree depth and control count, requests only the small property set needed for a plan, and immediately discards the adapter object after the review. A future event mode must be independently approved, time-limited, and disabled under Arthur’s low-resource guardrail.

| Stage | Local action | Default state | Explicitly excluded |
|---|---|---:|---|
| App selection | User chooses one visible application | Required | Background process discovery |
| Interface summary | Read accessible-control metadata for the approved app | Off | Screen capture, text/value retrieval, password controls |
| Plan preview | Build a local sequence of named controls | Off | Clicking, typing, file selection, communications |
| Action execution | Future one-action executor after confirmation | Not implemented | Automation rules, background execution, privilege elevation |

## Cloud boundary

The application bridge is **local-only**. It sends no interface summary, user content, accessibility data, or action plan to a cloud service. If an owner later requests cloud interpretation, Arthur must show the exact selected fields, destination, retention policy, provider, and per-request confirmation before a separate approved cloud gateway is used.

## References

[1]: https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-clientsoverview "Microsoft Learn — UI Automation Clients Overview"
