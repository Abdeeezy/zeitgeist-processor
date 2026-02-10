import json
import os


# used to "cache" webscraped and processed data (specifically just the keywords) so that testing is quicker/easier.
def save_keywords_to_json(path:str , processedArticlesKeywords2DArray: list[list[str]] ):
    with open(path, 'w') as f:
        json.dump(processedArticlesKeywords2DArray, f, indent=2)

def save_article_headlines_to_json(path:str , listOfArticleHeadlines: list[str]):
    with open(path, 'w') as f:
        json.dump(listOfArticleHeadlines, f, indent=2)

def save_article_scores_to_json(path:str , listOfArticleScores: list[dict]):
    with open(path, 'w') as f:
        json.dump(listOfArticleScores, f, indent=2)



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


# read in the cache again
def load_article_scores_from_json(path:str):
    try:
        with open(path, 'r') as f:
            listOfArticleScores: list[dict] = json.load(f)
            return listOfArticleScores
    except:
        print("'File error - doesn't exist")
    return None


def delete_file(path:str):
    try:
        os.remove(path)
        print(f"File '{path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{path}' not found.")
    except Exception as e:
        print(f"An error occurred while trying to delete the file: {e}")




