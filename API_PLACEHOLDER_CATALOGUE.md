# Function-Classified API Placeholder Catalogue

Arthur’s API Vault uses **functional categories** rather than pretending that every listed provider is connected. A provider is shown as an available placeholder with a declared authentication pattern, responsible owner, and non-networked test state. Commands route only after a developer or approved account connection is present.

| Functional category | Representative supplied placeholders | Connection boundary |
|---|---|---|
| Core AI & reasoning | OpenAI, Anthropic, Gemini, Groq, DeepSeek, Mistral, Cohere, Together AI, Hugging Face | Developer-managed API or token; no secret in the browser |
| Search, research & news | Perplexity, SerpAPI, Brave, Tavily, NewsAPI, GNews, Guardian, Google Programmable Search | Source-aware retrieval; access and use are approval-scoped |
| Speech, language & media | ElevenLabs, AssemblyAI, Deepgram, DeepL, Google Translate, LibreTranslate, Runway, HeyGen, D-ID, Veed | Developer-managed API or account authorisation; recording and camera consent remain explicit |
| Visual, OCR & documents | Google Vision, OCR.space, Textract, Adobe PDF Services, PDF.co, Cloudinary, Unsplash, Pexels, Pixabay | Selected-file/media only; privacy controls precede processing |
| Maps, geography & weather | Google Maps, Mapbox, HERE, OpenWeather, WeatherAPI, IPinfo, ipapi, MaxMind | User location is never sent without permission |
| Finance, market & regulated data | Alpha Vantage, Finnhub, CoinGecko, CoinMarketCap, ExchangeRate, Frankfurter, Plaid, Tink, Upvest | Information-only unless an approved regulated workflow is separately configured; no trades or transfers |
| Communication | Twilio, Vonage, Telnyx, SendGrid, Resend, Mailgun, SES, Discord, Telegram, Slack | Draft/preview then explicit send approval |
| App building, code & deployment | Lovable, GitHub, GitLab, Vercel, Netlify, Replit, Render, Railway, Figma, Framer, Webflow | OAuth or developer-managed connection; code and deploy actions remain approval-gated |
| Automation & integrations | Make, Zapier, Apify, Bright Data, Postman, n8n-compatible custom tools | Each workflow needs owner, trigger, permission scope, pause state, and audit record |
| Data, storage & memory | Supabase, Firebase, Pinecone, Weaviate, Qdrant, Neon, MongoDB Atlas, PlanetScale, Upstash, Airtable | User data is account-scoped; secrets remain server/desktop only |
| Productivity, business & social | Google Workspace, Microsoft Graph, Notion, HubSpot, Salesforce, Zoho, Meta, X, LinkedIn | Account OAuth and explicit action confirmation are required |
| Lifestyle & public data | Spotify, YouTube, TMDB, NASA, Google Books, Open Library, REST Countries, RAWG, IGDB, sports, travel, food, shipping, jobs, real estate | Informational by default; bookings, purchases, posts, and messages require approval |
| Security, monitoring & infrastructure | Cloudflare, Snyk, Datadog, PagerDuty, Vanta, HackerOne, VirusTotal, AbuseIPDB, Sentry, PostHog, Mixpanel | Defensive monitoring only. No scanning, target enumeration, bypassing, exploit delivery, or credential collection. |
| Provider discovery | RapidAPI, Postman API Network, APIs.guru, public API directories | Discovery does not grant execution; every selected provider must be reviewed and connected separately |

## Sensitive / review-required categories

Banking, payments, investment, health, real estate, social posting, security intelligence, identity, and cloud-infrastructure categories are kept as **review-required placeholders**. The catalogue does not activate money movement, medical or legal advice, public posting, target scanning, identity scraping, or infrastructure changes.

## Update-check policy

The catalogue may show **Update watch: paused** until an individual provider is connected. Real provider health or version checks need a protected server job, rate limits, provider-specific terms review, credential-safe requests, an audit record, and a user-visible pause control. The browser never polls third-party providers on its own.
