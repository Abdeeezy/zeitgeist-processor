import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article

import app.processing.text_processing as PreProcessor

import app.storage.trivial_file_storing as FileStoring


# attempt to load and then check if cached keyword json-file exists.. 
#   if not, run webscraping and preprocessing to extract keywords.
processed2DArrayArticlesToKeywords  = FileStoring.load_keywords_from_json("keywordData.json")
if(processed2DArrayArticlesToKeywords == None):
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
    processed2DArrayArticlesToKeywords = PreProcessor.process(listOfNewsCollection)

    # save/cache the data to local-storage 
    FileStoring.save_keywords_to_json("keywordData.json", processed2DArrayArticlesToKeywords)


if(processed2DArrayArticlesToKeywords != None):
    print("file does exist!")
    









def printArticleListContent(collection: NewsCollection):
    print("----------" + collection.name + "----------")
    count = 0
    for articleObj in collection.articleList:
        print(articleObj.content[:500])
        count += 1
        print("\n"+count.__str__()+"\n\n")