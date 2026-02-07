# 🎯 News Theme Tracking System - Complete Package

This package contains a production-ready BERTopic-based theme tracking system that integrates with your existing news processing pipeline.

## 📦 What's Included

### Core Files

1. **`theme_tracker.py`** - Main theme tracking class using BERTopic
   - Incremental daily updates
   - Automatic theme discovery
   - Model persistence
   - JSON export

2. **`main_with_themes.py`** - Updated main pipeline
   - Integrates with your existing code
   - Handles both initial setup and daily updates
   - Automated caching and saving

3. **`test_theme_discovery.py`** - Testing script
   - Test on your cached data without re-scraping
   - Quality analysis
   - Keyword diversity checks

4. **`requirements.txt`** - All dependencies
   - BERTopic and supporting libraries
   - Sentence transformers for embeddings
   - Clustering algorithms

5. **`THEME_TRACKING_GUIDE.md`** - Complete documentation
   - Setup instructions
   - Configuration guide
   - Troubleshooting
   - Advanced usage

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Test with Your Existing Data

```bash
# Make sure you have keywordData.json from your current pipeline
python test_theme_discovery.py
```

This will:
- Load your cached keywords
- Discover themes
- Show you a detailed report
- Save test results to `output/themes_test.json`

### Step 3: Integrate into Your Pipeline

Replace your existing `main.py` with the new version:

```bash
python main_with_themes.py
```

**For daily updates**, just run the same command each day - it will automatically load the previous model and update incrementally.

## 📊 What You'll Get

### Console Output

```
================================================================================
📊 THEME DISCOVERY REPORT - 2026-02-07 14:30
================================================================================

🎯 Theme #0: Venezuela + Maduro + Opposition
   Articles: 8
   Keywords: venezuela, maduro, opposition, assembly, president, government, law, country
   Sample articles:
      • Venezuela's National Assembly votes on amnesty bill for prisoners of conscience...

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
      "keywords": ["venezuela", "maduro", "opposition", "assembly", ...],
      "article_count": 8,
      "sample_articles": [
        {
          "headline": "Venezuela's National Assembly votes...",
          "date": "2026-02-06",
          "url": "https://...",
          "source": "Al Jazeera"
        }
      ]
    }
  }
}
```

## 🎛️ Configuration & Tuning

### During First Week - Tune These Parameters

In `main_with_themes.py`:

```python
tracker = ThemeTracker(
    min_topic_size=3,        # Adjust 2-5 based on your needs
    auto_reduce_topics=True  # Set False if getting merged too aggressively
)
```

**If getting too many small themes:**
- Increase `min_topic_size` to 4 or 5

**If themes are too broad:**
- Decrease `min_topic_size` to 2
- Set `auto_reduce_topics=False`

### Quality Checks to Monitor

The system will alert you when:
- **Outlier ratio > 15%** - Too many articles not fitting any theme
- **One theme > 30 articles** - Theme might need splitting
- **Themes changing drastically** - May need to review parameters

## 🔄 Daily Workflow

### Automated (Recommended)

Set up a daily cron job:

```bash
# Run at 6 AM every day
0 6 * * * cd /path/to/project && python main_with_themes.py >> logs/themes.log 2>&1
```

### Manual

```bash
# Day 1
python main_with_themes.py  # Creates initial model

# Day 2
python main_with_themes.py  # Loads model, adds new articles

# Day 3
python main_with_themes.py  # Continues updating...
```

## 🏗️ System Architecture

```
Your Existing Pipeline              New Theme Layer
─────────────────────              ───────────────
                                   
Scrape Articles         ──────>    BERTopic
     ↓                             Theme Discovery
Extract Keywords        ──────>         ↓
     ↓                             Save Model
Cache Results           ──────>    Export JSON
                                        ↓
                                   themes.json
                                   (for dashboards, etc.)
```

The theme tracker:
1. **Reads** your keyword extraction output
2. **Discovers** themes using BERTopic
3. **Updates** incrementally each day
4. **Saves** both models and JSON exports
5. **Alerts** when manual review is needed

## 📁 File Structure After Setup

```
your-project/
├── app/                          # Your existing code
│   ├── ingestion/
│   ├── models/
│   ├── processing/
│   └── storage/
├── models/                       # NEW - Auto-created
│   └── themes/
│       ├── bertopic_model_20260207/
│       └── metadata_20260207.pkl
├── output/                       # NEW - Auto-created
│   ├── themes.json
│   └── themes_visualization.html
├── theme_tracker.py              # NEW - Add this
├── main_with_themes.py           # NEW - Updated pipeline
├── test_theme_discovery.py       # NEW - Testing tool
└── requirements.txt              # NEW - Dependencies
```

## 🧪 Testing Before Full Integration

Before integrating into your main workflow:

```bash
# 1. Test theme discovery
python test_theme_discovery.py

# 2. Review output/themes_test.json
cat output/themes_test.json | less

# 3. If satisfied, integrate
python main_with_themes.py
```

## 💡 Advanced Features

### Visualizations

BERTopic includes built-in visualizations:

```python
from theme_tracker import ThemeTracker

tracker = ThemeTracker()
tracker.load_model()

# Interactive topic map
fig = tracker.topic_model.visualize_topics()
fig.write_html("output/topic_map.html")

# Topics over time
fig = tracker.topic_model.visualize_topics_over_time(...)
fig.write_html("output/topics_timeline.html")
```

### Custom Keyword Weighting

Already implemented in your `text_processing.py` - headlines are weighted 3x. To adjust:

```python
# In text_processing.py
HEADLINE_MULTIPLIER = 3  # Adjust as needed
```

### Export for Dashboards

The `themes.json` export is ready for:
- Web dashboards
- Tableau/PowerBI
- Custom analytics
- Notification systems

## 🐛 Troubleshooting

### "Model not fitted" Error
- You need to run `initial_fit()` first
- Or load an existing model with `load_model()`

### Slow Performance
- Switch to faster embedding model (see guide)
- Process in smaller batches
- Reduce number of keywords per article

### Unstable Themes Day-to-Day
- Keep rolling window of last 7 days
- Increase `min_topic_size`
- Manually merge similar themes

### High Memory Usage
- Process in batches of 100 articles
- Use lighter embedding model
- Reduce keyword count in preprocessing

## 📚 Further Reading

- **`THEME_TRACKING_GUIDE.md`** - Complete detailed documentation
- [BERTopic Documentation](https://maartengr.github.io/BERTopic/)
- [Sentence Transformers](https://www.sbert.net/)

## 🎯 Next Steps

1. **Today**: Test with `test_theme_discovery.py`
2. **Week 1**: Run daily, tune parameters, review themes
3. **Week 2**: Automate daily runs, set up alerts
4. **Week 3**: Fine-tune keyword extraction if needed
5. **Week 4**: Fully automated, hands-off operation!

## 📞 Need Help?

Check the troubleshooting section in `THEME_TRACKING_GUIDE.md` for common issues and solutions.

---

**Built with BERTopic** - State-of-the-art topic modeling for production use.
