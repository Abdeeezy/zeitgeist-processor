# Theme Tracking System - Setup & Usage Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt

# Download spaCy model (if not already done)
python -m spacy download en_core_web_sm
```

### 2. Directory Structure

Ensure your project has these directories:

```
project/
├── app/
│   ├── ingestion/
│   │   └── media_reading.py
│   ├── models/
│   │   ├── ArticleDataModel.py
│   │   └── NewsSiteDataModel.py
│   ├── processing/
│   │   └── text_processing.py
│   └── storage/
│       └── trivial_file_storing.py
├── models/           # Created automatically - stores theme models
├── output/           # Created automatically - stores JSON exports
├── theme_tracker.py  # NEW - BERTopic theme tracker
└── main_with_themes.py  # NEW - Updated main pipeline
```

### 3. First Run (Initial Theme Discovery)

```bash
python main_with_themes.py
```

This will:
- Fetch articles from Al Jazeera
- Extract keywords using your existing preprocessing
- Discover initial themes using BERTopic
- Save the model for future updates
- Export themes to `output/themes.json`

### 4. Daily Updates

For subsequent runs (e.g., tomorrow's news):

```bash
python main_with_themes.py
```

The system will automatically:
- Load yesterday's theme model
- Process new articles
- Update themes incrementally
- Save the updated model

---

## 📊 Understanding the Output

### Console Output

You'll see a report like this:

```
================================================================================
📊 THEME DISCOVERY REPORT - 2026-02-07 14:30
================================================================================

🎯 Theme #0: Venezuela + Maduro + Opposition
   Articles: 8
   Keywords: venezuela, maduro, opposition, assembly, president, government, law, country

🎯 Theme #1: Climate + Energy + Emissions
   Articles: 5
   Keywords: climate, energy, emission, carbon, renewable, fossil, fuel, policy

📈 Summary:
   Total themes: 12
   Total articles: 94
   Categorized: 89
   Outliers: 5
================================================================================
```

### JSON Export (`output/themes.json`)

```json
{
  "timestamp": "2026-02-07T14:30:00",
  "total_articles": 94,
  "themes": {
    "0": {
      "name": "Venezuela + Maduro + Opposition",
      "keywords": ["venezuela", "maduro", "opposition", ...],
      "article_count": 8,
      "sample_articles": [
        {
          "headline": "Venezuela's National Assembly votes on amnesty bill",
          "date": "2026-02-06",
          "url": "https://...",
          "source": "Al Jazeera"
        }
      ]
    }
  }
}
```

---

## 🎛️ Tuning & Configuration

### Initial Setup Period (Days 1-7)

During your first week, monitor the themes and adjust parameters:

#### If you get TOO MANY small themes:

```python
tracker = ThemeTracker(
    min_topic_size=5,  # Increase from 3 to 5
    auto_reduce_topics=True
)
```

#### If themes are TOO BROAD/GENERIC:

```python
tracker = ThemeTracker(
    min_topic_size=2,  # Decrease to allow more granular themes
    auto_reduce_topics=False  # Turn off auto-merging
)
```

#### Manual Theme Merging

After initial discovery, you can merge similar themes:

```python
# In main_with_themes.py, after initial_fit():

# Merge themes 5 and 8 (they're about the same topic)
tracker.topic_model.merge_topics(tracker.documents, [5, 8])

# Reduce to exactly 10 themes
tracker.topic_model.reduce_topics(tracker.documents, nr_topics=10)
```

### Monitoring Theme Quality

Add this to your daily output to track theme stability:

```python
# Compare today vs yesterday
from datetime import datetime, timedelta

def compare_themes(today_themes, yesterday_themes):
    """Check how themes are evolving"""
    
    print("\n📈 THEME EVOLUTION:")
    
    for topic_id, today_info in today_themes.items():
        if topic_id in yesterday_themes:
            yesterday_count = yesterday_themes[topic_id]['article_count']
            today_count = today_info['article_count']
            change = today_count - yesterday_count
            
            print(f"  {today_info['name']}: "
                  f"{yesterday_count} → {today_count} "
                  f"({'+' if change > 0 else ''}{change})")
        else:
            print(f"  🆕 NEW: {today_info['name']} ({today_info['article_count']} articles)")
```

---

## 🔄 Daily Workflow

### Automated Daily Update (Recommended)

Create a cron job or scheduled task:

```bash
# Run at 6 AM daily
0 6 * * * cd /path/to/project && python main_with_themes.py >> logs/daily_themes.log 2>&1
```

### Manual Review Triggers

Set up alerts for when you should manually review:

```python
def should_review(themes, outlier_count):
    """Determine if manual review is needed"""
    
    # Review if too many outliers
    total_articles = sum(t['article_count'] for t in themes.values())
    outlier_ratio = outlier_count / (total_articles + outlier_count)
    
    if outlier_ratio > 0.15:  # More than 15% outliers
        print("⚠️  HIGH OUTLIER RATIO - Manual review recommended")
        return True
    
    # Review if a theme explodes in size
    for theme in themes.values():
        if theme['article_count'] > 30:
            print(f"⚠️  Theme '{theme['name']}' has {theme['article_count']} articles - may need splitting")
            return True
    
    return False
```

---

## 💡 Advanced Usage

### Custom Keyword Weighting

If you want to emphasize certain types of keywords:

```python
# In text_processing.py, add weights to your keywords:

def process(newsList: list[NewsCollection]):
    # ... existing code ...
    
    for article in newsSite.articleList:
        # Extract keywords with custom weights
        keywords_weighted = []
        
        for token in doc:
            if not token.is_stop and not token.is_punct:
                # Verbs are important for actions/events
                if token.pos_ == 'VERB':
                    keywords_weighted.extend([token.lemma_.lower()] * 2)
                # Proper nouns (names, places)
                elif token.pos_ == 'PROPN':
                    keywords_weighted.extend([token.lemma_.lower()] * 3)
                # Regular nouns
                elif token.pos_ == 'NOUN':
                    keywords_weighted.append(token.lemma_.lower())
        
        return keywords_weighted
```

### Exporting for Dashboards

Create visualizations for monitoring:

```python
from theme_tracker import ThemeTracker

tracker = ThemeTracker()
tracker.load_model()

# BERTopic has built-in visualizations
fig = tracker.topic_model.visualize_topics()
fig.write_html("output/themes_visualization.html")

# Topic over time (if you have dates)
fig2 = tracker.topic_model.visualize_topics_over_time(
    tracker.documents, 
    timestamps=[meta['date'] for meta in tracker.articles_metadata]
)
fig2.write_html("output/themes_over_time.html")
```

---

## 🐛 Troubleshooting

### Issue: Model taking too long to train

Solution: Use a smaller embedding model

```python
from sentence_transformers import SentenceTransformer

# Faster but slightly less accurate
tracker.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Current (good balance)
# OR even faster:
tracker.embedding_model = SentenceTransformer('paraphrase-MiniLM-L3-v2')  # Fastest
```

### Issue: Themes too unstable day-to-day

Solution: Load full history instead of just yesterday

```python
# Keep a rolling window of last 7 days
# Modify add_daily_batch to maintain this window
```

### Issue: Out of memory

Solution: Process in smaller batches

```python
# Instead of all at once, process in chunks
BATCH_SIZE = 100

for i in range(0, len(keywords_matrix), BATCH_SIZE):
    batch = keywords_matrix[i:i+BATCH_SIZE]
    batch_metadata = metadata[i:i+BATCH_SIZE]
    tracker.add_daily_batch(batch, batch_metadata)
```

---

## 📝 Next Steps

1. **Week 1**: Run daily, review themes, tune `min_topic_size`
2. **Week 2**: Set up automated daily runs, monitor outliers
3. **Week 3**: Fine-tune keyword extraction if needed
4. **Week 4**: Fully automated, only review on alerts

After 1 month, the system should run autonomously with minimal intervention!
