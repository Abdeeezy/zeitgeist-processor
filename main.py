import os
import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
import app.processing.text_processing as PreProcessor
import app.processing.LLM_theme_deriver as ThemeDeriver
import app.storage.trivial_file_storing as FileStoring

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# -- Config --------------------------------------------------------------------
DEV_MODE = os.getenv("ZEITGEIST_DEV", "false").lower() == "true"
ARTICLE_BATCH_SIZE = 5# how many articles to send in one batch to the LLM for theme scoring. can adjust based on token limits and cost considerations. with claude-sonnet-4-5




# -- App state -----------------------------------------------------------------
# Holds the processed result in memory so /api/data doesn't re-run the pipeline.
# None = not yet processed. Empty list = pipeline ran but found nothing.
_pipeline_result: list[dict] | None = None


# -- FastAPI -------------------------------------------------------------------
# run `uvicorn main:app --reload`  in termiinal to start the FastAPI server, then access the data at the endpoint below:
#       http://127.0.0.1:8000/api/data
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # '*' -> Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"],# Allow all headers
)


# -- Routes --------------------------------------------------------------------

@app.get("/api/data")
def get_data():
    global _pipeline_result     
    # if the data is not already cached in memory, load it from there
    if _pipeline_result is None:
        _pipeline_result = run_pipeline() 
    return _pipeline_result


# this endpoint is for new webscraped data. 
# If the server has been running non-stop and user desires new data, 
# run this to wipe the cache and re-run the pipeline  
@app.post("/api/wipeAndProcessAnew")
def wipe_and_process_anew():
    global _pipeline_result
    try:
        FileStoring.delete_file("keywordData.json")
        FileStoring.delete_file("articleHeadlines.json")
        FileStoring.delete_file("articleScores.json")
        _pipeline_result = run_pipeline()
        return {"message": "Cache wiped and pipeline re-run."}
    except Exception as e:
        print(f"Wipe failed: {e}")
        return {"message": f"Error: {e}"}


@app.get("/api/isOnline")
def is_online():
    return {"status": True}


# -- Pipeline ------------------------------------------------------------------

def run_pipeline() -> list[dict]:
    """
    Single entry point. In dev mode, loads from cached files.
    In production, runs the full scrape → preprocess → LLM pipeline,
    then caches for next time.
    """
    if DEV_MODE:
        cached = _load_from_cache()
        if cached is not None:
            print(f"[DEV] Loaded {len(cached)} articles from cache")
            return cached
        print("[DEV] No cache found — falling through to full pipeline")

    # -- Scrape / Ingestion ---------------------------------------------
    collections: list[NewsCollection] = []

    # Fetch New York Times
    collections.append(MediaGet.FetchTopStoriesDataFromNYTimes())
    # Fetch AlJazeera
    collections.append(MediaGet.FetchTopStoriesDataFromAlJazeera())
    # Fetch BBC
    collections.append(MediaGet.FetchTopStoriesDataFromBBC())

    # -- Preprocess ----------------------------------------------------
    keywords_matrix, headlines = PreProcessor.process(collections)

    articles = [
        {"keywords": keywords_matrix[i], "headline": headlines[i]}
        for i in range(len(keywords_matrix))
    ]

    # -- LLM scoring ---------------------------------------------------
    scores = ThemeDeriver.score_articles_batch(articles, ARTICLE_BATCH_SIZE)

    # -- Cache for dev reuse -------------------------------------------
    FileStoring.save_keywords_to_json("keywordData.json", keywords_matrix)
    FileStoring.save_article_headlines_to_json("articleHeadlines.json", headlines)
    FileStoring.save_article_scores_to_json("articleScores.json", scores)

    # -- Build response ------------------------------------------------
    return _build_response(articles, scores)


def _load_from_cache() -> list[dict] | None:
    """Attempt to load all three cache files. Returns None if any are missing."""
    keywords = FileStoring.load_keywords_from_json("keywordData.json")
    headlines = FileStoring.load_article_headlines_from_json("articleHeadlines.json")
    scores = FileStoring.load_article_scores_from_json("articleScores.json")

    if any(x is None for x in (keywords, headlines, scores)):
        return None

    articles = [
        {"keywords": keywords[i], "headline": headlines[i]}
        for i in range(len(keywords))
    ]
    return _build_response(articles, scores)


def _build_response(articles: list[dict], scores: list[dict]) -> list[dict]:
    """Zip articles with their scores into the API response shape."""
    return [
        {
            "headline": articles[i]["headline"],
            "keywords": articles[i]["keywords"],
            "themeScores": scores[i],
        }
        for i in range(len(articles))
    ]