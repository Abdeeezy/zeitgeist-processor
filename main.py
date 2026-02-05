import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article





#cnnCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromCNN()

alJazeeraCollection: NewsCollection = MediaGet.FetchTopStoriesDataFromAlJazeera()

#MediaGet.FetchTopStoriesDataFromNYTimes()








def printArticleListContent(collection: NewsCollection):
    print("----------" + collection.name + "----------")
    count = 0
    for articleObj in collection.articleList:
        print(articleObj.content[:500])
        count += 1
        print("\n"+count.__str__()+"\n\n")