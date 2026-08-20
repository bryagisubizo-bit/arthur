# Arthur by Bogitech — Developer API Acquisition Guide

This guide identifies the values Arthur needs and where the developer obtains them. Enter only regenerated credentials locally through Arthur’s administrator settings or a protected server secret manager. Never paste a secret into chat, a browser preview, source code, a public ZIP, or a desktop client distributed to users.

## OpenAI: primary conversation, research, and voice

Create an application API key from the OpenAI API-key dashboard. The official quickstart specifies that the key should be created in the dashboard and loaded through an environment variable such as `OPENAI_API_KEY`; the reference also states that API keys must not be exposed in browser or application client code.[1][2]

| Arthur field | Developer enters | Where to obtain it | Where it belongs |
|---|---|---|---|
| Provider | `OpenAI` | Arthur API vault | Arthur configuration |
| API key | Regenerated OpenAI project API key | [OpenAI API keys](https://platform.openai.com/api-keys) | Protected backend or OS credential manager during development only |
| Model | The supported model you select | [OpenAI models](https://developers.openai.com/api/docs/models) | Arthur configuration |

> Do not expose an OpenAI API key in browser or desktop-client code. A production Arthur deployment should route requests through a protected backend that enforces account access, rate limits, approved tools, and audit logging.[2]

## Supabase: browser accounts and profile sync

Arthur requires a **Project URL** and **Publishable Key** for a browser or desktop client. In the Supabase Dashboard, open the project’s **Connect** dialog to copy both values, or open **Settings → API Keys** to locate a specific key. The official documentation distinguishes client-side publishable keys from server-only secret keys.[3][4]

| Arthur field | Developer enters | Where to obtain it | Where it belongs |
|---|---|---|---|
| Project URL | `https://your-project.supabase.co` | Project **Connect** dialog | Arthur client configuration |
| Publishable Key | Your project’s publishable key | Project **Connect** dialog or **Settings → API Keys** | Arthur client configuration |
| Secret Key | Your project’s server-only secret key | **Settings → API Keys** | Protected backend only; never Arthur’s desktop/client settings |

Enable **Row Level Security** on every user-data table and verify policies for the `anon` and `authenticated` roles before enabling profile sync.[3]

## Anthropic: secondary reasoning and long-form checks

Create a Claude Console account, then open **Account Settings → API keys** to generate an Anthropic API key. The Anthropic documentation states that you can select an expiration date and use workspaces to segment keys and control spend by use case.[5]

| Arthur field | Developer enters | Where to obtain it | Where it belongs |
|---|---|---|---|
| Provider | `Anthropic` | Arthur API vault | Arthur configuration |
| API key | Regenerated Anthropic API key | [Claude Console API keys](https://platform.claude.com/settings/keys) | Protected backend or OS credential manager during development only |
| Workspace | Optional workspace label | [Claude Console workspaces](https://platform.claude.com/settings/workspaces) | Arthur configuration |

Arthur should use the provider as an optional secondary reasoning service, with any external request subjected to the same per-user permission, approved-tool, and audit policies as the primary model.[5]

## Home Assistant: optional smart-home control

Arthur should request the user’s approval before connecting to a detected Home Assistant hub. The owner signs into Home Assistant, opens the **User Profile → Security** area, and creates a **Long-Lived Access Token**. The local hub URL and that token are required to make authorized REST calls.[6][7]

| Arthur field | Developer or authorized user enters | Where to obtain it | Where it belongs |
|---|---|---|---|
| Home Assistant URL | Local URL, for example `http://homeassistant.local:8123` | The user’s Home Assistant installation | Per-user encrypted settings |
| Long-Lived Access Token | Newly created token | **User Profile → Security** in Home Assistant | Per-user encrypted settings; never source code |

Arthur must show the requested device action, target entity, and a confirmation before controlling security, climate, locks, alarms, or other consequential smart-home functions.

## SerpAPI: authorized web research

Create a SerpAPI account, then obtain the API key from the key-management area. The official Python integration documentation recommends reading the value from a `SERPAPI_KEY` environment variable rather than embedding it in source code.[8]

| Arthur field | Developer enters | Where to obtain it | Where it belongs |
|---|---|---|---|
| Provider | `SerpAPI` | Arthur API vault | Arthur configuration |
| API key | Regenerated SerpAPI key | [SerpAPI sign-up](https://serpapi.com/users/sign_up) then [Manage API Key](https://serpapi.com/manage-api-key) | Protected backend or OS credential manager during development only |

Arthur must cite its sources in a visual panel only when the user permits a visual response, and it should never use search access to bypass logins, paywalls, access controls, or website restrictions.

## Luxand: optional, consent-based identity verification

Luxand.cloud requires the developer to create an account, choose the intended feature (for example face verification), and obtain a token through its developer workflow.[9] Arthur should keep this capability **disabled by default**, make enrolment and deletion explicit, and provide a password or other non-biometric fallback.

| Arthur field | Developer enters | Where to obtain it | Where it belongs |
|---|---|---|---|
| Provider | `Luxand` | Arthur API vault | Arthur configuration |
| API token | Regenerated Luxand.cloud API token | [Luxand.cloud account flow](https://luxand.cloud/how-to-try-luxand-cloud-api) | Protected backend only |

> Do not use facial recognition for background surveillance, hidden tracking, account-lockout decisions, or irreversible automated actions. Arthur should ask for a user-initiated verification and protect biometric data as highly sensitive information.

## No-key components and developer-defined integrations

| Capability | Key needed? | Developer action |
|---|---:|---|
| `openWakeWord` | No | Obtain the package from its trusted package source, present the exact installation command, and require the user’s approval before running it. |
| Windows system telemetry | No | Use local, least-privileged operating-system APIs. Show unavailable data instead of estimating readings. |
| GitHub Releases update checks | No for public release checks | Publish signed releases. Any GitHub publishing token stays in a CI secret store, never in Arthur. |
| Piped-compatible music adapter | Usually no developer key | Verify the endpoint owner, terms, privacy policy, availability, and playback authorization before enabling it. Prefer an approved music provider with user OAuth when available. |
| APIFrame, APIBox, Seper, or another custom API | Depends on the vendor | Use Arthur’s **Add approved integration** form. Record the vendor documentation URL, HTTPS base URL, authentication type, scope, privacy policy, timeout, and revocation path before adding the credential locally. |

For any custom provider, do not enable the integration merely because a key exists. The developer should test it in a restricted environment, allow only documented HTTPS endpoints, set short timeouts, log only metadata needed for diagnostics, and give users an off switch.

## References

[1] [OpenAI API Developer Quickstart](https://developers.openai.com/api/docs/quickstart)

[2] [OpenAI API Reference: Authentication](https://developers.openai.com/api/reference/overview#authentication)

[3] [Supabase: Understanding API keys](https://supabase.com/docs/guides/getting-started/api-keys)

[4] [Supabase: API URL and keys](https://supabase.com/docs/guides/api/creating-routes#api-url-and-keys)

[5] [Anthropic Claude API Overview](https://platform.claude.com/docs/en/api/overview)

[6] [Home Assistant Authentication](https://www.home-assistant.io/docs/authentication/)

[7] [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/)

[8] [SerpAPI Python integration](https://serpapi.com/integrations/python)

[9] [Luxand.cloud: How to try the API](https://luxand.cloud/how-to-try-luxand-cloud-api)
