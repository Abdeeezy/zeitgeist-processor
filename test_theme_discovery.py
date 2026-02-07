"""
Test script to run theme discovery on your existing keyword data.
Use this to test the system without re-scraping articles.
"""

import json
from pathlib import Path
from app.processing.theme_tracker import ThemeTracker


def test_with_existing_data():
    """
    Test theme discovery using your cached keywordData.json
    """
    
    print("\n🧪 TESTING THEME DISCOVERY WITH CACHED DATA")
    print("="*80 + "\n")
    
    # Load your existing keyword data
    keywords_file = Path("keywordData.json")
    
    if not keywords_file.exists():
        print("❌ Error: keywordData.json not found!")
        print("   Please run your existing pipeline first to generate cached data.")
        return
    
    # Load keywords
    with open(keywords_file, 'r') as f:
        keywords_matrix = json.load(f)
    
    print(f"✅ Loaded {len(keywords_matrix)} articles from cache")
    
    # Optional: Load metadata if available
    metadata = None
    metadata_file = Path("articleMetadata.json")
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print(f"✅ Loaded metadata for {len(metadata)} articles")
    
    # Initialize theme tracker
    print("\n🔍 Initializing theme tracker...")
    tracker = ThemeTracker(
        min_topic_size=2,
        model_path="models/themes_test",
        auto_reduce_topics=False,
        nr_topics=8  # Force exactly 8 themes
    )
    
    # Discover themes
    print("🎯 Discovering themes...")
    themes = tracker.initial_fit(keywords_matrix, metadata)
    
    # Show detailed report
    tracker.print_theme_report(themes, detailed=True)
    
    # Save results
    print("\n💾 Saving test results...")
    tracker.save_model(suffix="_test")
    tracker.export_themes_to_json(themes, "output/themes_test.json")
    
    print("\n✅ Test complete!")
    print("   Check output/themes_test.json for results")
    
    # Interactive exploration
    print("\n" + "="*80)
    print("🔎 THEME DETAILS")
    print("="*80)
    
    for topic_id, info in sorted(themes.items(), key=lambda x: x[1]['article_count'], reverse=True):
        print(f"\n{'─'*80}")
        print(f"Theme #{topic_id}: {info['name']}")
        print(f"{'─'*80}")
        print(f"Articles: {info['article_count']}")
        print(f"\nTop 15 keywords:")
        for i, kw in enumerate(info['keywords'][:15], 1):
            print(f"  {i:2d}. {kw}")
        
        if info['sample_articles']:
            print(f"\nSample articles:")
            for i, article in enumerate(info['sample_articles'][:3], 1):
                if 'headline' in article:
                    print(f"  {i}. {article['headline'][:70]}...")
                else:
                    print(f"  {i}. Article index: {article.get('index', 'unknown')}")
    
    print("\n" + "="*80)
    
    return tracker, themes


def analyze_theme_quality(tracker, themes):
    """
    Run some basic quality checks on discovered themes
    """
    print("\n📊 THEME QUALITY ANALYSIS")
    print("="*80 + "\n")
    
    total_articles = len(tracker.documents)
    categorized = sum(t['article_count'] for t in themes.values())
    outliers = total_articles - categorized
    
    print(f"Coverage:")
    print(f"  Total articles: {total_articles}")
    print(f"  Categorized: {categorized} ({categorized/total_articles*100:.1f}%)")
    print(f"  Outliers: {outliers} ({outliers/total_articles*100:.1f}%)")
    
    # Theme size distribution
    sizes = [t['article_count'] for t in themes.values()]
    if sizes:
        print(f"\nTheme size distribution:")
        print(f"  Smallest theme: {min(sizes)} articles")
        print(f"  Largest theme: {max(sizes)} articles")
        print(f"  Average: {sum(sizes)/len(sizes):.1f} articles")
    
    # Check for dominant theme
    if sizes and max(sizes) > total_articles * 0.3:
        print(f"\n⚠️  Warning: One theme contains {max(sizes)/total_articles*100:.1f}% of articles")
        print(f"   Consider increasing min_topic_size or splitting this theme")
    
    # Check outlier ratio
    outlier_ratio = outliers / total_articles
    if outlier_ratio > 0.2:
        print(f"\n⚠️  Warning: High outlier ratio ({outlier_ratio*100:.1f}%)")
        print(f"   Consider decreasing min_topic_size to capture more themes")
    elif outlier_ratio < 0.05:
        print(f"\n✅ Good outlier ratio ({outlier_ratio*100:.1f}%)")
    
    print("\n" + "="*80)


def compare_keyword_overlap():
    """
    Quick analysis of keyword diversity in your data
    """
    print("\n📝 KEYWORD DIVERSITY ANALYSIS")
    print("="*80 + "\n")
    
    keywords_file = Path("keywordData.json")
    with open(keywords_file, 'r') as f:
        keywords_matrix = json.load(f)
    
    # Flatten all keywords
    all_keywords = []
    for article_kws in keywords_matrix:
        all_keywords.extend(article_kws)
    
    # Count unique
    unique_keywords = set(all_keywords)
    
    print(f"Total keywords (with duplicates): {len(all_keywords)}")
    print(f"Unique keywords: {len(unique_keywords)}")
    print(f"Average keywords per article: {len(all_keywords)/len(keywords_matrix):.1f}")
    print(f"Keyword diversity ratio: {len(unique_keywords)/len(all_keywords):.2f}")
    
    # Most common keywords
    from collections import Counter
    keyword_counts = Counter(all_keywords)
    
    print(f"\nMost common keywords:")
    for kw, count in keyword_counts.most_common(20):
        print(f"  {kw:20s} ({count:3d} occurrences)")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # Run keyword analysis first
    try:
        compare_keyword_overlap()
    except Exception as e:
        print(f"⚠️  Couldn't analyze keywords: {e}")
    
    # Run theme discovery test
    tracker, themes = test_with_existing_data()
    
    # Analyze quality
    if tracker and themes:
        analyze_theme_quality(tracker, themes)
        
        print("\n💡 Next steps:")
        print("   1. Review the themes in output/themes_test.json")
        print("   2. If satisfied, copy theme_tracker.py to your app/ directory")
        print("   3. Update your main.py to use main_with_themes.py as a template")
        print("   4. Run the full pipeline with: python main_with_themes.py")
