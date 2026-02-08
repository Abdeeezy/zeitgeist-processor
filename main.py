import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article

import app.processing.text_processing as PreProcessor
import app.processing.LLM_theme_deriver as ThemeDeriver

import app.storage.trivial_file_storing as FileStoring


# Pseudo-code workflow  - IGNORE THIS
'''
1. Collect all keywords from all articles                           DONE
2. Create a document-term matrix (articles × keywords)              DONE
3. Apply TF-IDF weighting to highlight distinctive terms            ...
4. Use clustering or topic modeling                                 ...
5. Examine top keywords per cluster to label themes                 ...
'''



# attempt to load and then check if cached keyword json-file exists.. 
#   if not, run webscraping and preprocessing to extract keywords.
processedArticlesToKeywordsMatrix  = FileStoring.load_keywords_from_json("keywordData.json")
if(processedArticlesToKeywordsMatrix == None):
    # A list of each newsSite object. which contains all the scrapped articles within it 
    listOfNewsCollection = list[NewsCollection]()

            ##ignore
            # Fetch CNN  //// (outdated - boring articles from <2023 only - needs a new webscraping method that doesn't use RSS-Feeds)
            #cnnCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromCNN()
            #listOfNewsCollection.append(cnnCollection)
            
            ##ignore
            # Fetch New York Times  //// (payblocked, only headlines and minimal keywords offered...)
            #nyTimesCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromNYTimes()
            #listOfNewsCollection.append(nyTimesCollection)

    # Fetch AlJazeera
    alJazeeraCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromAlJazeera()
    listOfNewsCollection.append(alJazeeraCollection)

    # extract keywords
    processedArticlesToKeywordsMatrix, listOfCorrespondingArticleHeadlines = PreProcessor.process(listOfNewsCollection)

    # save/cache the data to local-storage 
    FileStoring.save_keywords_to_json("keywordData.json", processedArticlesToKeywordsMatrix)
    FileStoring.save_article_headlines_to_json("articleHeadlines.json", listOfCorrespondingArticleHeadlines)


if(processedArticlesToKeywordsMatrix != None):
    print("file does exist!")
    listOfCorrespondingArticleHeadlines = FileStoring.load_article_headlines_from_json("articleHeadlines.json")


    articles = list[dict]()
    for i in range(len(processedArticlesToKeywordsMatrix)):
        keywords = processedArticlesToKeywordsMatrix[i]
        headline = listOfCorrespondingArticleHeadlines[i]

        articles.append({
            "keywords": keywords,
            "headline": headline
        })

        
    # batch api calls to score articles with Claude Sonnet 4.5
    theme_scores = ThemeDeriver.score_articles_batch(articles[:5]) # 4 cents per 5 articles with claude-sonnet-4-5, which can take up to 3000 tokens (enough for 5 articles with keywords).
    
    for i, article in enumerate(articles[:5]):
        print(f"Article: '{article['headline'][:50]}...' Theme Scores: {theme_scores[i]}")
        print("-"*50 + "\n")



# processing pipeline will continue here..






