# Arthur Provider Update Checks

Arthur’s provider registry treats **availability**, **health**, and **vendor version changes** as separate signals. The browser preview intentionally performs no network checks and stores no provider credentials.

## Required implementation boundary

Automatic checks may be enabled only after a developer has connected a specific provider and declared its approved health or version endpoint. A server-side scheduled job must then:

1. run under an owner-controlled schedule with a per-provider interval and backoff policy;
2. use a server-held credential only where the provider explicitly requires it;
3. call only an allowlisted HTTPS endpoint with a strict timeout and rate limit;
4. record the check time, outcome, endpoint label, and sanitised error category in an audit record;
5. never copy credentials, request content, or sensitive response bodies into a log;
6. notify the developer only for a material version, deprecation, outage, or authentication change; and
7. require a review before changing a provider implementation, credential scope, command route, or user permission.

## Current preview state

| Capability room | Provider connected | Automatic update checks |
|---|---:|---:|
| All browser-preview rooms | No | Disabled |
| Private notes database | Internal application service | Not applicable |
| Local Windows adapter | Desktop prototype boundary | Desktop-managed, not browser-polled |

> **No provider is assumed to exist merely because it appears in the catalogue.** When a room is unavailable, Arthur must explain the missing approved resource and stop rather than manufacture an integration or silently fall back to an unsafe route.
