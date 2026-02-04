from dataclasses import dataclass

@dataclass
class Article:
    """Class for keeping track of an article on a website."""
    title: str
    date: str
    content: str

    def __init__(self, title: str, date: str, content:str ):
        self.title = title
        self.date = date
        self.content = content 