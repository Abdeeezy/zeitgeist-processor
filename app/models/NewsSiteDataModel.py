from dataclasses import dataclass

from app.models.ArticleDataModel import Article

@dataclass
class NewsCollection:
    """Class for keeping track of a news-website's articles."""
    name: str
    articleList: list[Article]

    #automatically creates the initalizer.
