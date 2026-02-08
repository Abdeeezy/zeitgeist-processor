"""
Main pipeline with integrated theme tracking
"""

import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article
import app.processing.text_processing as PreProcessor
import app.storage.trivial_file_storing as FileStoring

from app.processing.theme_tracker import ThemeTracker
from pathlib import Path
import json


def extract_metadata_from_collections(news_collections: list[NewsCollection]) -> list[dict]:
    """
    Extract metadata from news collections for theme tracking.
    
    Returns a flat list of article metadata dicts.
    """
    metadata = []
    for collection in news_collections:
        for article in collection.articleList:
            metadata.append({
                'headline': article.headline,
                'date': article.date,
                'url': article.url,
                'source': collection.name
            })
    return metadata


def main():
    """
    Main processing pipeline:
    1. Load or fetch articles
    2. Extract keywords
    3. Discover/update themes
    4. Save results
    """
    
    print("\n" + "="*80)
    print("🚀 NEWS THEME ANALYSIS PIPELINE")
    print("="*80 + "\n")
    
    # ========================================================================
    # STEP 1: Load or fetch keyword data
    # ========================================================================
    
    keywords_cache_file = "keywordData.json"
    metadata_cache_file = "articleMetadata.json"
    
    keywords_matrix = FileStoring.load_keywords_from_json(keywords_cache_file)
    
    # Try to load cached metadata
    metadata = None
    if Path(metadata_cache_file).exists():
        with open(metadata_cache_file, 'r') as f:
            metadata = json.load(f)
        print(f"✅ Loaded {len(metadata)} article metadata from cache")
    
    # If no cached data, fetch fresh articles
    if keywords_matrix is None:
        print("📡 No cached data found. Fetching fresh articles...")
        
        news_collections = []
        
        # Fetch AlJazeera
        print("   Fetching Al Jazeera...")
        aljazeera_collection = MediaGet.FetchTopStoriesDataFromAlJazeera()
        news_collections.append(aljazeera_collection)
        
        # Add more sources here as they become available
        # bbc_collection = MediaGet.FetchTopStoriesDataFromBBC()
        # news_collections.append(bbc_collection)
        
        # Extract keywords
        print("🔤 Extracting keywords...")
        keywords_matrix = PreProcessor.process(news_collections)
        
        # Extract metadata
        metadata = extract_metadata_from_collections(news_collections)
        
        # Cache both keywords and metadata
        FileStoring.save_keywords_to_json(keywords_cache_file, keywords_matrix)
        with open(metadata_cache_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Processed {len(keywords_matrix)} articles")
        print(f"💾 Cached keywords and metadata")
    else:
        print(f"✅ Loaded {len(keywords_matrix)} articles from cache")
    
    # ========================================================================
    # STEP 2: Theme Discovery/Update
    # ========================================================================
    
    tracker = ThemeTracker(
        min_topic_size=2,  # Minimum 3 articles per theme
        model_path="models/themes",
        auto_reduce_topics=False,
        nr_topics=8
    )
    
    # Check if we have an existing model (for daily updates)
    model_exists = False
    try:
        tracker.load_model()
        model_exists = True
        print("✅ Loaded existing theme model")
    except FileNotFoundError:
        print("ℹ️  No existing model found. Will create new one.")
    
    # Perform theme analysis
    if model_exists:
        # This is a daily update - add new articles
        print("\n🔄 Updating themes with new articles...")
        themes = tracker.add_daily_batch(keywords_matrix, metadata)
    else:
        # First run - initial fit
        print("\n🆕 Performing initial theme discovery...")
        themes = tracker.initial_fit(keywords_matrix, metadata)
    
    # ========================================================================
    # STEP 3: Display and Save Results
    # ========================================================================
    
    # Print detailed report
    tracker.print_theme_report(themes, detailed=True)
    
    # Save updated model
    tracker.save_model()
    
    # Export themes to JSON for other applications
    tracker.export_themes_to_json(themes, "output/themes.json")
    
    # ========================================================================
    # STEP 4: Interactive Analysis (Optional)
    # ========================================================================
    
    # You can add interactive exploration here
    print("\n💡 Theme analysis complete!")
    print("   • Model saved for tomorrow's update")
    print("   • Themes exported to output/themes.json")
    print("   • Ready for next batch!\n")
    
    return tracker, themes


def run_daily_update(new_articles_source="aljazeera"):
    """
    Simplified function for daily cron job.
    Fetches new articles and updates themes.
    """
    print("\n🌅 DAILY THEME UPDATE")
    print("="*80 + "\n")
    
    # Fetch fresh articles (don't use cache)
    news_collections = []
    
    if new_articles_source == "aljazeera":
        collection = MediaGet.FetchTopStoriesDataFromAlJazeera()
        news_collections.append(collection)
    
    # Extract keywords
    keywords_matrix = PreProcessor.process(news_collections)
    metadata = extract_metadata_from_collections(news_collections)
    
    print(f"📰 Fetched {len(keywords_matrix)} new articles")
    
    # Load existing model and update
    tracker = ThemeTracker()
    tracker.load_model()
    
    themes = tracker.add_daily_batch(keywords_matrix, metadata)
    
    # Print report and save
    tracker.print_theme_report(themes)
    tracker.save_model()
    tracker.export_themes_to_json(themes, "output/themes_daily.json")
    
    print("✅ Daily update complete!\n")
    
    return themes


if __name__ == "__main__":
    # Run the main pipeline
    tracker, themes = main()
    
    # Optional: Run some analysis queries
    print("\n" + "="*80)
    print("🔍 SAMPLE QUERIES")
    print("="*80 + "\n")
    
    # Example: Find which theme a specific article belongs to
    if len(tracker.documents) > 0:
        article_idx = 0
        theme_id = tracker.get_article_theme(article_idx)
        if theme_id is not None and theme_id != -1:
            theme = themes.get(theme_id)
            if theme:
                print(f"Article 0 belongs to theme: {theme['name']}")
                print(f"Theme keywords: {', '.join(theme['keywords'][:5])}")
