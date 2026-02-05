import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article

import app.processing.text_processing as PreProcessor


# A list of each newsSite object. which contains all the scrapped articles within it 
listOfNewsCollection = list[NewsCollection]()

# Fetch CNN  //// (outdated - boring articles from <2023 only - needs a new webscraping method that doesn't use RSS-Feeds)
#cnnCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromCNN()
#listOfNewsCollection.append(cnnCollection)

# Fetch AlJazeera
alJazeeraCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromAlJazeera()
listOfNewsCollection.append(alJazeeraCollection)

# Fetch AlJazeera  //// (payblocked, only headlines and minimal keywords offered...)
#nyTimesCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromNYTimes()
#listOfNewsCollection.append(nyTimesCollection)



PreProcessor.process(listOfNewsCollection)








def printArticleListContent(collection: NewsCollection):
    print("----------" + collection.name + "----------")
    count = 0
    for articleObj in collection.articleList:
        print(articleObj.content[:500])
        count += 1
        print("\n"+count.__str__()+"\n\n")