# Provider Connection-Test Research

Arthur’s API Vault sends a live request only after explicit user approval. The implementation limits checks to the following narrow, read-only provider endpoints.

| Provider family | Documented check | Authentication | Official reference |
|---|---|---|---|
| OpenAI, OpenAI Audio, and OpenAI TTS | List models: `GET /v1/models` | Bearer API key | [OpenAI API reference](https://developers.openai.com/api/reference/resources/models/methods/list) |
| Anthropic | List models: `GET /v1/models?limit=1` | `x-api-key` and the documented Anthropic API version header | [Anthropic Models API reference](https://platform.claude.com/docs/en/api/models/list) |

Arthur records only an outcome and timestamp. It never writes provider keys to source code, configuration files, test output, or user-visible error detail. Providers without a reviewed adapter remain explicitly unavailable rather than being represented as connected.
