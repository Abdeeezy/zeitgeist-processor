

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


    aggregatedListOfKeywordArrays = list[list[str]]()
    listOfCorrespondingArticleHeadlines = list[str]()
    # for each site
    for newsSite in newsList:

        # NewYorkTimes blocks content with a subscription - do skip the processing, they supply keywords freely though
        if newsSite.name == "NYTimes": 
            for article in newsSite.articleList:
                listOfCorrespondingArticleHeadlines.append(article.source + ' ->>- ' + article.headline)
                aggregatedListOfKeywordArrays.append(article.keywords)
            continue # skip this iteration of the former-loop.


        for article in newsSite.articleList:

            # keep track of the headline for later reference (LLM processing context)
            listOfCorrespondingArticleHeadlines.append(article.source + ' ->>- ' + article.headline)

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

            #entities = [(ent.text, ent.label_) for ent in doc.ents]  # unneeded, mostly irrelevant data. but keeping it here as a reminder in case i do find a use.

            print("\n\n------KEYWORDS------\n")
            print (keywords)
            
            aggregatedListOfKeywordArrays.append(keywords)
    

    return aggregatedListOfKeywordArrays, listOfCorrespondingArticleHeadlines
            



