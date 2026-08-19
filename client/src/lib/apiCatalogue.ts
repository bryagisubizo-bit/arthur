export type CatalogueAuth = "Developer API key" | "User OAuth" | "Public / no key" | "Desktop or local adapter" | "Review required";
export type CatalogueOwner = "Developer" | "User account" | "Local desktop" | "Review required";

export type CatalogueCategory = {
  id: string;
  name: string;
  function: string;
  providers: string[];
  auth: CatalogueAuth;
  owner: CatalogueOwner;
  reviewRequired?: boolean;
};

/**
 * A provider may appear in more than one functional room, so tag identity must
 * include its room as well as its display name. The source catalogue enforces
 * unique provider names within each room.
 */
export function providerPlaceholderKey(categoryId: string, provider: string) {
  return `${categoryId}:${provider.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}`;
}

export const apiCatalogue: CatalogueCategory[] = [
  { id: "ai", name: "AI, reasoning & embeddings", function: "Conversation, coding, planning, multimodal analysis, embeddings, and model inference.", providers: ["OpenAI", "Anthropic", "Google AI Studio / Gemini", "Groq", "DeepSeek", "Hugging Face", "Perplexity", "Mistral", "Cohere", "Together AI", "Replicate"], auth: "Developer API key", owner: "Developer" },
  { id: "search", name: "Search, news & research", function: "Approved search retrieval, current-news context, and source-aware research.", providers: ["SerpAPI", "Brave Search", "Tavily", "Google Programmable Search", "NewsAPI", "GNews", "Guardian API", "Perplexity"], auth: "Developer API key", owner: "Developer" },
  { id: "voice", name: "Speech, translation & language", function: "Speech recognition, text-to-speech, translation, dictionaries, and language switching.", providers: ["OpenAI Audio", "ElevenLabs", "AssemblyAI", "Deepgram", "Google Cloud Speech", "Azure Speech", "DeepL", "Google Translate", "LibreTranslate", "Oxford Dictionaries", "Wordnik"], auth: "Developer API key", owner: "Developer" },
  { id: "media", name: "Images, video & creative media", function: "Opt-in generation, avatar/video tools, media editing, stock imagery, and image cleanup.", providers: ["Midjourney", "Leonardo.ai", "Runway", "D-ID", "HeyGen", "Veed.io", "Remove.bg", "Cloudinary", "Unsplash", "Pexels", "Pixabay", "GIPHY"], auth: "Developer API key", owner: "Developer" },
  { id: "vision", name: "Vision, OCR & documents", function: "Selected-file OCR, document parsing, visual context, and controlled extraction.", providers: ["Google Cloud Vision", "Luxand", "OCR.space", "Amazon Textract", "Adobe PDF Services", "PDF.co", "Docparser", "Mindee", "Nanonets"], auth: "Developer API key", owner: "Developer" },
  { id: "maps", name: "Maps, weather & geolocation", function: "Permissioned maps, routing, weather, IP enrichment, and geocoding.", providers: ["Google Maps Platform", "Mapbox", "HERE", "OpenWeatherMap", "WeatherAPI", "Open-Meteo", "IPinfo", "ipapi", "MaxMind"], auth: "Developer API key", owner: "Developer" },
  { id: "app-building", name: "App building, code & deployment", function: "Authorised project creation, repositories, design handoff, build, and deployment workflows.", providers: ["Lovable", "GitHub", "GitLab", "Vercel", "Netlify", "Replit", "Render", "Railway", "Figma", "Framer", "Webflow"], auth: "User OAuth", owner: "User account" },
  { id: "automation", name: "Automation, workflow & scraping", function: "Declared automations, data collection, API testing, and workflow orchestration.", providers: ["Make", "Zapier", "Apify", "Bright Data", "Postman", "n8n-compatible custom tools", "RapidAPI", "Postman API Network", "APIs.guru"], auth: "Developer API key", owner: "Developer", reviewRequired: true },
  { id: "database", name: "Databases, storage & AI memory", function: "Account-scoped data, files, relational stores, caching, and vector retrieval.", providers: ["Supabase", "Firebase", "Pinecone", "Weaviate", "Qdrant", "Neon", "MongoDB Atlas", "PlanetScale", "Upstash", "Airtable"], auth: "Developer API key", owner: "Developer" },
  { id: "messaging", name: "Email, messaging & communications", function: "Drafted email, SMS, voice, chat, and notification delivery after explicit send approval.", providers: ["Twilio", "Vonage", "Telnyx", "Resend", "SendGrid", "Mailgun", "Amazon SES", "Discord", "Telegram", "Slack", "Microsoft Teams"], auth: "User OAuth", owner: "User account", reviewRequired: true },
  { id: "identity", name: "Identity, auth & user accounts", function: "Account registration, login, verification, and user identity flows.", providers: ["Clerk", "Auth0", "Supabase Auth", "Firebase Auth", "OAuth providers"], auth: "User OAuth", owner: "User account", reviewRequired: true },
  { id: "payments", name: "Payments, banking & investment", function: "Review-required financial information, payments, account linking, and regulated investment infrastructure.", providers: ["Stripe", "PayPal", "Square", "Plaid", "Tink", "Wise", "Upvest", "Coinbase Commerce"], auth: "Review required", owner: "Review required", reviewRequired: true },
  { id: "markets", name: "Finance, markets & crypto data", function: "Read-only market prices, exchange rates, crypto data, and financial information.", providers: ["Alpha Vantage", "Finnhub", "IEX Cloud", "Financial Modeling Prep", "CoinGecko", "CoinMarketCap", "ExchangeRate API", "Frankfurter"], auth: "Developer API key", owner: "Developer", reviewRequired: true },
  { id: "analytics", name: "Analytics, SEO & observability", function: "Opt-in product analytics, error monitoring, performance, and SEO research.", providers: ["Google Analytics", "Hotjar", "Mixpanel", "PostHog", "Sentry", "LogRocket", "Semrush", "Ahrefs", "GTmetrix", "PageSpeed Insights", "BuiltWith"], auth: "Developer API key", owner: "Developer", reviewRequired: true },
  { id: "cloud", name: "Cloud, infrastructure & domains", function: "Approved hosting, logs, DNS, certificates, monitoring, and domain configuration.", providers: ["Cloudflare", "AWS", "Azure", "Google Cloud", "DigitalOcean", "Namecheap", "Let's Encrypt", "Datadog", "PagerDuty"], auth: "Review required", owner: "Review required", reviewRequired: true },
  { id: "security", name: "Defensive security & compliance", function: "Review-required defensive enrichment, reputation, exposure, vulnerability, alert, and threat-context lookups only. Arthur never performs active scanning, bypass, exploitation, credential collection, malware handling, or automatic security actions.", providers: ["Snyk", "Vanta", "HackerOne", "Keeper Security", "VirusTotal", "AbuseIPDB", "Cloudflare", "SecurityTrails", "URLScan.io", "AlienVault OTX", "GreyNoise", "IBM X-Force", "CrowdStrike", "Microsoft Defender", "Google Safe Browsing", "Have I Been Pwned", "NIST NVD", "MITRE ATT&CK", "CVE.org", "EPSS", "OpenCTI", "MISP", "PhishTank", "URLhaus", "MalwareBazaar", "ThreatFox", "CIRCL"], auth: "Review required", owner: "Review required", reviewRequired: true },
  { id: "productivity", name: "Productivity, CRM & business", function: "Authorised calendars, documents, wikis, customer records, and business workflows.", providers: ["Google Workspace", "Microsoft Graph", "Notion", "HubSpot", "Salesforce", "Zoho", "Airtable", "Monday.com", "Asana", "Trello"], auth: "User OAuth", owner: "User account", reviewRequired: true },
  { id: "social", name: "Social, communities & publishing", function: "Draft, schedule, and publish content only after explicit approval.", providers: ["Meta Graph API", "X API", "LinkedIn", "Reddit", "YouTube Data API", "Discord", "Telegram", "Twitch"], auth: "User OAuth", owner: "User account", reviewRequired: true },
  { id: "music", name: "Music, podcasts & audio discovery", function: "Authorised playback, catalogues, podcast discovery, and music metadata.", providers: ["Spotify", "YouTube Music", "Apple Music", "Deezer", "Last.fm", "MusicBrainz", "Piped-compatible", "BhariyaMusic"], auth: "User OAuth", owner: "User account" },
  { id: "entertainment", name: "Movies, television & games", function: "Entertainment discovery, metadata, watch-provider, and game catalogues.", providers: ["TMDB", "OMDb", "TVmaze", "JustWatch", "RAWG", "IGDB", "Steam Web API", "Twitch"], auth: "Developer API key", owner: "Developer" },
  { id: "books", name: "Books, education & reference", function: "Books, dictionaries, education, country, government, and public-reference lookups.", providers: ["Google Books", "Open Library", "Crossref", "Wikidata", "REST Countries", "World Bank", "OpenAlex", "OpenStax"], auth: "Public / no key", owner: "Developer" },
  { id: "science", name: "Science, space & environment", function: "Public science, space, climate, biodiversity, and environmental information.", providers: ["NASA", "NOAA", "Open-Meteo", "GBIF", "USGS", "OpenAQ", "WolframAlpha"], auth: "Developer API key", owner: "Developer" },
  { id: "health", name: "Health & wellness information", function: "Review-required public health information and personal wellness integrations; never diagnosis or emergency triage.", providers: ["FHIR-compatible systems", "Google Fit", "Apple Health", "Nutritionix", "Edamam", "Spoonacular"], auth: "Review required", owner: "Review required", reviewRequired: true },
  { id: "travel", name: "Travel, transport & vehicles", function: "Read-only travel, flight, rail, vehicle, traffic, and route information.", providers: ["Amadeus", "Skyscanner", "Kiwi", "Rome2Rio", "Transport for London", "NHTSA", "Open Charge Map", "HERE"], auth: "Developer API key", owner: "Developer", reviewRequired: true },
  { id: "commerce", name: "Commerce, products & shipping", function: "Product, order, inventory, price, shipping, and parcel information.", providers: ["Shopify", "WooCommerce", "eBay", "Amazon Product Advertising", "EasyPost", "Shippo", "AfterShip", "UPS", "FedEx", "DHL"], auth: "Review required", owner: "Review required", reviewRequired: true },
  { id: "food", name: "Food, recipes & local places", function: "Recipe, nutrition, dining, and local-place research.", providers: ["Spoonacular", "Edamam", "Yelp Fusion", "Google Places", "Foursquare"], auth: "Developer API key", owner: "Developer" },
  { id: "sports", name: "Sports & live scores", function: "Sports schedules, leagues, results, and live-score information.", providers: ["TheSportsDB", "Football-Data.org", "API-Football", "Sportradar", "ESPN APIs"], auth: "Developer API key", owner: "Developer" },
  { id: "iot", name: "IoT & smart home", function: "User-authorised device discovery, sensor data, scenes, and home automation.", providers: ["Home Assistant", "Philips Hue", "SmartThings", "IFTTT", "Tuya", "MQTT adapter"], auth: "User OAuth", owner: "User account", reviewRequired: true },
  { id: "jobs", name: "Jobs, companies & real estate", function: "Public job, company, property, and domain information.", providers: ["Adzuna", "JSearch", "Clearbit", "Crunchbase", "RentCast", "WhoisXML API", "WhoisFreaks"], auth: "Developer API key", owner: "Developer", reviewRequired: true },
  { id: "utilities", name: "Developer utilities & test data", function: "Safe format validation, compatibility lookups, code sharing, test data, and local webhook setup.", providers: ["Regex101", "JSONLint", "CanIUse", "JSONPlaceholder", "ngrok", "Carbon", "Stack Overflow", "Font Awesome", "SVG Repo"], auth: "Public / no key", owner: "Developer" },
  { id: "local", name: "Windows & local desktop", function: "Reviewed Windows apps, diagnostics, file actions, and wake word; no raw shell execution.", providers: ["Arthur Windows adapter", "openWakeWord", "approved local parsers", "WSL diagnostics"], auth: "Desktop or local adapter", owner: "Local desktop", reviewRequired: true },
];

export const catalogueCounts = {
  categories: apiCatalogue.length,
  providers: apiCatalogue.reduce((total, category) => total + category.providers.length, 0),
  reviewRequired: apiCatalogue.filter((category) => category.reviewRequired).length,
};
