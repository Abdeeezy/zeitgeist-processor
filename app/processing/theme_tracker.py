"""
Theme Tracker using BERTopic for incremental theme discovery
Integrates with existing article processing pipeline
"""

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pickle


class ThemeTracker:
    """
    Discovers and tracks themes across news articles using BERTopic.
    Supports incremental daily updates.
    """
    
    def __init__(self, 
                 min_topic_size: int = None,
                 model_path: str = "models/theme_model",
                 auto_reduce_topics: bool = False,
                 nr_topics: int = None):
        """
        Initialize the theme tracker.
        
        Args:
            min_topic_size: Minimum number of articles to form a theme (auto-calculated if None)
            model_path: Path to save/load the model
            auto_reduce_topics: Whether to automatically merge similar themes (default: False)
            nr_topics: Force exact number of topics (overrides auto_reduce_topics)
        """
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.min_topic_size = min_topic_size
        self.nr_topics = nr_topics
        self.auto_reduce_topics = auto_reduce_topics
        
        # Use a lightweight but effective embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Custom vectorizer to handle our keyword-based documents
        self.vectorizer = CountVectorizer(
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,  # Changed from 2 to 1 for small datasets
            max_df=0.95,  # More lenient for small datasets
            stop_words='english'
        )
        
        # Will initialize BERTopic in initial_fit with dynamic parameters
        self.topic_model = None
        
        # Track articles and metadata
        self.articles_metadata = []  # List of dicts with article info
        self.documents = []  # Processed keyword documents
        self.fitted = False
        
    def _keywords_to_document(self, keywords: List[str]) -> str:
        """
        Convert keyword list to a document string.
        Deduplicates and joins keywords.
        """
        # Remove duplicates while preserving some order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            kw_clean = kw.lower().strip()
            if kw_clean and kw_clean not in seen and len(kw_clean) > 2:
                seen.add(kw_clean)
                unique_keywords.append(kw_clean)
        
        return ' '.join(unique_keywords)
    
    def initial_fit(self, 
                   keywords_matrix: List[List[str]], 
                   metadata: Optional[List[Dict]] = None) -> Dict:
        """
        Perform initial theme discovery on first batch of articles.
        
        Args:
            keywords_matrix: List of keyword lists (one per article)
            metadata: Optional list of dicts with article info (headline, date, url, etc.)
            
        Returns:
            Dictionary with theme information
        """
        print(f"\n🔍 Performing initial theme discovery on {len(keywords_matrix)} articles...")
        
        # Convert keywords to documents
        self.documents = [self._keywords_to_document(kws) for kws in keywords_matrix]
        
        # Store metadata
        if metadata:
            self.articles_metadata = metadata
        else:
            self.articles_metadata = [{'index': i} for i in range(len(keywords_matrix))]
        
        # Auto-calculate min_topic_size if not provided
        if self.min_topic_size is None:
            num_articles = len(self.documents)
            if num_articles < 50:
                self.min_topic_size = 2
            elif num_articles < 200:
                self.min_topic_size = 3
            else:
                self.min_topic_size = 5
            print(f"   Auto-set min_topic_size to {self.min_topic_size} based on {num_articles} articles")
        
        # Initialize BERTopic with calculated parameters
        self.topic_model = BERTopic(
            embedding_model=self.embedding_model,
            vectorizer_model=self.vectorizer,
            min_topic_size=self.min_topic_size,
            nr_topics=self.nr_topics if self.nr_topics else ("auto" if self.auto_reduce_topics else None),
            calculate_probabilities=True,
            verbose=True
        )
        
        # Fit the model
        topics, probabilities = self.topic_model.fit_transform(self.documents)
        self.fitted = True
        
        # Get theme summary
        themes = self._get_theme_summary()
        
        print(f"✅ Discovered {len(themes)} themes")
        
        # Warn if too few themes
        if len(themes) < len(self.documents) / 10:
            print(f"⚠️  Warning: Only {len(themes)} themes for {len(self.documents)} articles.")
            print(f"   Consider decreasing min_topic_size (currently {self.min_topic_size})")
            print(f"   or setting nr_topics to force more granular themes.")
        
        return themes
    
    def add_daily_batch(self, 
                       new_keywords_matrix: List[List[str]],
                       new_metadata: Optional[List[Dict]] = None) -> Dict:
        """
        Add new articles and update themes incrementally.
        
        Args:
            new_keywords_matrix: List of keyword lists for new articles
            new_metadata: Optional metadata for new articles
            
        Returns:
            Updated theme dictionary
        """
        if not self.fitted:
            raise ValueError("Model not fitted. Call initial_fit() first.")
        
        print(f"\n📰 Adding {len(new_keywords_matrix)} new articles...")
        
        # Convert new keywords to documents
        new_docs = [self._keywords_to_document(kws) for kws in new_keywords_matrix]
        
        # Update metadata
        if new_metadata:
            self.articles_metadata.extend(new_metadata)
        else:
            start_idx = len(self.articles_metadata)
            self.articles_metadata.extend([
                {'index': start_idx + i} 
                for i in range(len(new_keywords_matrix))
            ])
        
        # Transform new documents (assign to existing topics)
        new_topics, new_probs = self.topic_model.transform(new_docs)
        
        # Add to our document store
        self.documents.extend(new_docs)
        
        # Update the model with new documents
        # This allows topics to evolve over time
        all_topics = list(self.topic_model.topics_) + list(new_topics)
        self.topic_model.update_topics(
            self.documents,
            topics=all_topics,
            vectorizer_model=self.vectorizer
        )
        
        themes = self._get_theme_summary()
        
        print(f"✅ Updated themes. Now tracking {len(themes)} themes across {len(self.documents)} articles")
        
        return themes
    
    def _get_theme_summary(self) -> Dict:
        """
        Extract readable theme information from the model.
        
        Returns:
            Dictionary mapping theme IDs to theme info
        """
        topic_info = self.topic_model.get_topic_info()
        
        themes = {}
        
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            
            # Skip outlier topic (-1)
            if topic_id == -1:
                continue
            
            # Get top keywords for this theme
            topic_words = self.topic_model.get_topic(topic_id)
            if topic_words:
                top_keywords = [word for word, score in topic_words[:15]]
            else:
                top_keywords = []
            
            # Get articles in this theme
            article_indices = [
                i for i, t in enumerate(self.topic_model.topics_) 
                if t == topic_id
            ]
            
            # Generate a readable theme name from top keywords
            theme_name = self._generate_theme_name(top_keywords[:3])
            
            themes[topic_id] = {
                'name': theme_name,
                'keywords': top_keywords,
                'article_count': len(article_indices),
                'article_indices': article_indices,
                'sample_articles': self._get_sample_articles(article_indices[:3])
            }
        
        return themes
    
    def _generate_theme_name(self, top_keywords: List[str]) -> str:
        """Generate a human-readable theme name from keywords"""
        if not top_keywords:
            return "Unknown Theme"
        
        # Capitalize and join top 3 keywords
        name = ' + '.join([kw.title() for kw in top_keywords[:3]])
        return name
    
    def _get_sample_articles(self, indices: List[int]) -> List[Dict]:
        """Get metadata for sample articles"""
        samples = []
        for idx in indices:
            if idx < len(self.articles_metadata):
                samples.append(self.articles_metadata[idx])
        return samples
    
    def get_article_theme(self, article_index: int) -> Optional[int]:
        """Get the theme ID for a specific article"""
        if article_index < len(self.topic_model.topics_):
            return self.topic_model.topics_[article_index]
        return None
    
    def print_theme_report(self, themes: Dict, detailed: bool = False):
        """
        Print a formatted report of discovered themes.
        
        Args:
            themes: Dictionary from get_theme_summary()
            detailed: Whether to show sample articles
        """
        print("\n" + "="*80)
        print(f"📊 THEME DISCOVERY REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80)
        
        # Sort themes by article count
        sorted_themes = sorted(
            themes.items(), 
            key=lambda x: x[1]['article_count'], 
            reverse=True
        )
        
        for topic_id, info in sorted_themes:
            print(f"\n🎯 Theme #{topic_id}: {info['name']}")
            print(f"   Articles: {info['article_count']}")
            print(f"   Keywords: {', '.join(info['keywords'][:8])}")
            
            if detailed and info['sample_articles']:
                print(f"   Sample articles:")
                for article in info['sample_articles']:
                    headline = article.get('headline', 'No headline')
                    print(f"      • {headline[:80]}...")
        
        print("\n" + "="*80)
        
        # Summary stats
        total_articles = sum(t['article_count'] for t in themes.values())
        outliers = len(self.documents) - total_articles
        
        print(f"\n📈 Summary:")
        print(f"   Total themes: {len(themes)}")
        print(f"   Total articles: {len(self.documents)}")
        print(f"   Categorized: {total_articles}")
        print(f"   Outliers: {outliers}")
        print("="*80 + "\n")
    
    def save_model(self, suffix: str = ""):
        """Save the model and metadata to disk"""
        timestamp = datetime.now().strftime('%Y%m%d')
        
        # Save BERTopic model
        model_file = self.model_path / f"bertopic_model_{timestamp}{suffix}"
        self.topic_model.save(str(model_file))
        
        # Save metadata separately
        metadata_file = self.model_path / f"metadata_{timestamp}{suffix}.pkl"
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'articles_metadata': self.articles_metadata,
                'documents': self.documents,
                'fitted': self.fitted
            }, f)
        
        print(f"💾 Model saved to {model_file}")
        print(f"💾 Metadata saved to {metadata_file}")
    
    def load_model(self, suffix: str = ""):
        """Load a previously saved model"""
        timestamp = datetime.now().strftime('%Y%m%d')
        
        model_file = self.model_path / f"bertopic_model_{timestamp}{suffix}"
        metadata_file = self.model_path / f"metadata_{timestamp}{suffix}.pkl"
        
        # Try to load today's model first, fall back to latest
        if not model_file.exists():
            # Find most recent model
            model_files = sorted(self.model_path.glob("bertopic_model_*"))
            if model_files:
                model_file = model_files[-1]
                # Get corresponding metadata file
                date_str = model_file.stem.split('_')[-1]
                metadata_file = self.model_path / f"metadata_{date_str}.pkl"
            else:
                raise FileNotFoundError("No saved model found")
        
        # Load model
        self.topic_model = BERTopic.load(str(model_file))
        
        # Load metadata
        if metadata_file.exists():
            with open(metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.articles_metadata = data['articles_metadata']
                self.documents = data['documents']
                self.fitted = data['fitted']
        
        print(f"📂 Model loaded from {model_file}")
        print(f"📂 Metadata loaded from {metadata_file}")
    
    def export_themes_to_json(self, themes: Dict, output_file: str):
        """Export themes to JSON for external use"""
        # Convert to JSON-serializable format
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_articles': len(self.documents),
            'themes': {}
        }
        
        for topic_id, info in themes.items():
            export_data['themes'][str(topic_id)] = {
                'name': info['name'],
                'keywords': info['keywords'],
                'article_count': info['article_count'],
                'sample_articles': info['sample_articles']
            }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"📄 Themes exported to {output_file}")
