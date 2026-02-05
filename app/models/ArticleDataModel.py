from dataclasses import dataclass

@dataclass
class Article:
    """Class for keeping track of an article on a website."""
    headline: str
    date: str
    content: str
    url: str
    keywords: list[str]

    #custom initializer.
    def __init__(self, headline: str, date: str, content:str, url: str, keywords = list()):
        self.headline = headline
        self.date = date
        self.content = content 
        self.url = url
        self.keywords = keywords
