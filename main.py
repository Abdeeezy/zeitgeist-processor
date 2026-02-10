import app.ingestion.media_reading as MediaGet
from app.models.NewsSiteDataModel import NewsCollection
from app.models.ArticleDataModel import Article

import app.processing.text_processing as PreProcessor
import app.processing.LLM_theme_deriver as ThemeDeriver

import app.storage.trivial_file_storing as FileStoring




from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json


articles = []
listOfArticleScores = []
listOfCorrespondingArticleHeadlines = []
processedArticlesToKeywordsMatrix = []



#instantialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],  # '*' -> Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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


    # process the articles in batches to get theme scores from the LLM
    articles = list[dict]()
    for i in range(len(processedArticlesToKeywordsMatrix)):
        keywords = processedArticlesToKeywordsMatrix[i]
        headline = listOfCorrespondingArticleHeadlines[i]

        articles.append({
            "keywords": keywords,
            "headline": headline
        })
    listOfArticleScores = ThemeDeriver.score_articles_batch(articles) # 4 cents per 5 articles with claude-sonnet-4-5, which can take up to 3000 tokens (enough for 5 articles with keywords).
    
    for i, article in enumerate(articles):
        print(f"Article: '{article['headline']}...' Theme Scores: {listOfArticleScores[i]}")
        print("-"*50 + "\n")


    # save/cache the data to local-storage 
    FileStoring.save_keywords_to_json("keywordData.json", processedArticlesToKeywordsMatrix)
    FileStoring.save_article_headlines_to_json("articleHeadlines.json", listOfCorrespondingArticleHeadlines)
    FileStoring.save_article_scores_to_json("articleScores.json", listOfArticleScores)

    



if(processedArticlesToKeywordsMatrix != None):
    print("file does exist!")
    listOfCorrespondingArticleHeadlines = FileStoring.load_article_headlines_from_json("articleHeadlines.json")
    listOfArticleScores = FileStoring.load_article_scores_from_json("articleScores.json")

    articles = list[dict]()
    for i in range(len(processedArticlesToKeywordsMatrix)):
        keywords = processedArticlesToKeywordsMatrix[i]
        headline = listOfCorrespondingArticleHeadlines[i]

        articles.append({
            "keywords": keywords,
            "headline": headline
        })

    for i, article in enumerate(articles):
        print("index: ", i)
        print(f"Article: '{article['headline']}...' Theme Scores: {listOfArticleScores[i]}")
        print("-"*50 + "\n")

    
    # run `uvicorn main:app --reload`  in termiinal to start the FastAPI server, then access the data at the endpoint below:
    #   http://127.0.0.1:8000/api/data
    @app.get("/api/data")
    def get_data():
        return [
            {
                "headline": articles[i]['headline'],
                "keywords": articles[i]['keywords'],
                "themeScores": listOfArticleScores[i]
            }
            for i in range(len(articles))  # return all articles with their headlines, keywords, and theme scores
        ]





