


# Weight headlines heavily, maybe 3-5x the body text. Headlines are carefully crafted to capture the essence.

# Extract by article first, then aggregate - this lets you see which keywords span multiple articles (recurring themes)

# plug keywords into TF-IDF (term frequency-inverse document frequency) 
#   TF-IDF is a statistical measure used to evaluate the importance of a word in a document relative to a collection of documents. 
#   It helps in information retrieval and text mining by scoring and ranking the relevance of documents based on the frequency of terms.

#Concept Clustering
#   LDA topic modeling is almost designed for news corpora - it'll find recurring themes across articles automatically.
#   Cross-article phrase analysis - phrases appearing in 3+ articles are likely important recurring concepts.


# SpaCy for NLP preprocessing and Named-Entity-Recognition. cleans text and returns nouns/verbs/entities in text. 
# scikit-learn for TF-IDF and topic modeling
#   gensim for more advanced topic modeling

# instead of n-grams, Just use NER for entities (which are naturally multi-word)
#   And maybe Extract only high-frequency bi-grams (maybe top 50-100) that appear across multiple articles

# starting with keywords + named entities only



import spacy
import unicodedata

from app.models.ArticleDataModel import Article
from app.models.NewsSiteDataModel import NewsCollection


from dataclasses import dataclass
@dataclass
class ProcessedArticle:
    """Class for keeping track of a news-website's articles."""
    source: str
    keywordList: list[str]



# CONSTANTS
HEADLINE_MULTIPLIER = 3



#takes a list of news-website data-objects
def process(newsList: list[NewsCollection]):

    # Let spaCy do the heavy lifting 
    #   Whitespace normalization
    #   Lemmatization - Built-in, Access with `token.lemma_`
    nlp = spacy.load("en_core_web_sm") 

    # for each site
    for newsSite in newsList:

        for article in newsSite.articleList:

            # add the headline to be processed and tokenized.
            #   multiplied because headlines are crafted to be representative of the main-themes of the article
            text = "" + (article.headline * 3) + article.content

            # Minimal pre-processing
            text = unicodedata.normalize('NFC', text)  
            text = text.strip() 

            doc = nlp(text)

            # Extract what you need
            keywords = [token.lemma_.lower() for token in doc 
                if not token.is_stop and not token.is_punct and token.pos_ in ['NOUN', 'PROPN']]

            entities = [(ent.text, ent.label_) for ent in doc.ents]

            print("\n\n------KEYWORDS------\n\n")
            print (keywords)
            print("\n\n------ENTITIES------\n\n")
            print (entities)
            

            break # RUN ONCE.. REMOVE


