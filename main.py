import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article

import app.processing.text_processing as PreProcessor

import app.storage.trivial_file_storing as FileStoring


# Pseudo-code workflow
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

            # Fetch CNN  //// (outdated - boring articles from <2023 only - needs a new webscraping method that doesn't use RSS-Feeds)
            #cnnCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromCNN()
            #listOfNewsCollection.append(cnnCollection)

            # Fetch New York Times  //// (payblocked, only headlines and minimal keywords offered...)
            #nyTimesCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromNYTimes()
            #listOfNewsCollection.append(nyTimesCollection)

    # Fetch AlJazeera
    alJazeeraCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromAlJazeera()
    listOfNewsCollection.append(alJazeeraCollection)

    # extract keywords
    processedArticlesToKeywordsMatrix = PreProcessor.process(listOfNewsCollection)

    # save/cache the data to local-storage 
    FileStoring.save_keywords_to_json("keywordData.json", processedArticlesToKeywordsMatrix)


if(processedArticlesToKeywordsMatrix != None):
    print("file does exist!")












def printArticleListContent(collection: NewsCollection):
    print("----------" + collection.name + "----------")
    count = 0
    for articleObj in collection.articleList:
        print(articleObj.content[:500])
        count += 1
        print("\n"+count.__str__()+"\n\n")