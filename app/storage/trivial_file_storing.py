import json


# used to "cache" webscraped and processed data (specifically just the keywords) so that testing is quicker/easier.
def save_keywords_to_json(path:str , processedArticlesKeywords2DArray: list[list[str]] ):
    with open(path, 'w') as f:
        json.dump(processedArticlesKeywords2DArray, f, indent=2)

def save_article_headlines_to_json(path:str , listOfArticleHeadlines: list[str]):
    with open(path, 'w') as f:
        json.dump(listOfArticleHeadlines, f, indent=2)

# read in the cache again
def load_keywords_from_json(path:str):
    try:
        with open(path, 'r') as f:
            processedArticlesKeywords2DArray: list[list[str]] = json.load(f)
            return processedArticlesKeywords2DArray
    except:
        print("'File error - doesn't exist")
    return None


# read in the cache again
def load_article_headlines_from_json(path:str):
    try:
        with open(path, 'r') as f:
            listOfArticleHeadlines: list[str] = json.load(f)
            return listOfArticleHeadlines
    except:
        print("'File error - doesn't exist")
    return None




