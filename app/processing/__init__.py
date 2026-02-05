# you can write code in the __init__.py file to initialize package-level variables,
# define functions or classes, and control what gets imported when the package is used.
#  
# it signals that the directory should be treated like a module/package
#
# However, it's not mandatory to include code in this file; 
# it mainly serves to mark a directory as a Python package.



'''

[Preprocessing] (filler removal, tokenization)
       ↓
[Feature Extraction] (keywords, n-grams, embeddings)
       ↓
[Theme Detector] (clustering, topic modeling)


After extracting keywords and n-grams, you'll need a clustering/grouping layer to identify coherent themes
Consider using embeddings (sentence transformers like all-MiniLM-L6-v2) to map text chunks into semantic space, then cluster (HDBSCAN, DBSCAN)
Each cluster becomes a "proto-theme" that you can label either through:

    Extractive methods (most central keywords)

    LLM-based summarization (send top keywords → get theme name)

    Topic modeling (LDA, BERTopic) for hierarchical themes



Theme Properties to Extract:

    Intensity/Energy: frequency of mentions, sentiment strength, keyword density

    Polarity: sentiment (positive/negative/neutral)

    


'''

