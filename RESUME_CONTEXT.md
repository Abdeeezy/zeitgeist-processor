# Zeitgeist Processor — Resume Context

## What it is
News analysis pipeline: scrape → NLP → LLM semantic scoring → REST API

## Pipeline flow
1. **Ingestion** — Playwright (headless browser automation) scrapes BBC, Al Jazeera, NYT; RSS feeds parsed via `feedparser`
2. **NLP** — spaCy (`en_core_web_sm`): tokenization, lemmatization, POS tagging → extract only NOUN/PROPN tokens; headline tokens weighted 3x
3. **LLM Scoring** — batched (5 articles/call) zero-shot classification via Claude API (Sonnet); articles scored 0.0–1.0 against 27 custom thematic concepts (e.g. Entropy, Renewal, Corruption, Resilience...)
4. **Caching** — JSON file cache avoids redundant scraping/LLM calls; in-memory cache within server lifetime
5. **Serving** — FastAPI + Uvicorn REST API; CORS-enabled for frontend integration

## Libraries
`spacy` · `anthropic` · `playwright` · `feedparser` · `fastapi` · `uvicorn` · `requests`

## Design patterns / concepts
- **ETL pipeline** architecture (Extract → Transform → Load)
- **Zero-shot LLM classification** (no fine-tuning; prompt-driven)
- **Batch processing** for API cost/rate-limit management
- **Multi-layer caching** (disk + in-memory)
- **Dataclass** models for typed data flow
- Adaptive scraping strategy per source (RSS vs. dynamic JS via Playwright)

## Notable technical details
- 27 thematic dimensions custom-designed (philosophical/archetypal framing of news)
- Rate limiting baked in (15s delay between LLM batches)
- Unicode NFC normalization for multilingual robustness
- Bot-detection workaround via User-Agent spoofing + Playwright browser context
