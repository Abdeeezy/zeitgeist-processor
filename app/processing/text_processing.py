


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




