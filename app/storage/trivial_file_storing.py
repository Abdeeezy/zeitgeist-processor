import json


# used to "cache" webscraped and processed data (specifically just the keywords) so that testing is quicker/easier.
def save_keywords_to_json(path:str , processedArticlesKeywords2DArray: list[list[str]] ):
    with open(path, 'w') as f:
        json.dump(processedArticlesKeywords2DArray, f, indent=2)

# read in the cache again
def load_keywords_from_json(path:str):
    try:
        with open(path, 'r') as f:
            processedArticlesKeywords2DArray: list[list[str]] = json.load(f)
            return processedArticlesKeywords2DArray
    except:
        print("'File error - doesn't exist")
    return None




