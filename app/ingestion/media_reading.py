import requests 
import feedparser
from playwright.sync_api import Page, sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo

from app.models.ArticleDataModel import Article

#https://feedparser.readthedocs.io/en/latest/    api


# USE RSS FEEDS TO FETCH THE STORIES AND THEIR RESPECTIVE LINKS.
#  THEN USE STATIC OR DYNAMIC SCRAPING TO READ THE ARTICLE'S CONTENTS
#
#  EACH NEWS-WEBSITE WILL PROBABLY NEED A UNIQUE SCRAPING ALGORITHM.    

'''
 URL
  ↓
 Try HTTP fetch
  ↓
 If JS needed → Playwright
  ↓
 HTML
  ↓
 trafilatura / readability
  ↓
 Clean article text
  ↓
 Construct Return Data-object
   NewsSource: ArticleData[]

'''


## Helper functions
def parseDateStringToDateTime(str):
    #example: "Updated 9:13 AM EST, Mon March 6, 2023 "  (CNN article)
    clean = (
        str.replace("Updated ", "")
        .replace("Published ", "")
       .replace(" EST", "")
       .replace(" PST", "")
       .replace(" UTC", "")
       .replace(" EDT", "")
       .strip()
    )
    dt = datetime.strptime(clean, "%I:%M %p, %a %B %d, %Y")
    return dt



## main functions
def FetchTopStoriesDataFromCNN():
    ## https://www.cnn.com/services/rss/?no_redirect=true
    #
    #feed = feedparser.parse('http://rss.cnn.com/rss/cnn_topstories.rss')
    feed = feedparser.parse('http://rss.cnn.com/rss/cnn_world.rss')
    
    title = feed['channel']['title']
    print('--------' + title + "--------\n\n")

    # CNN dynamically loads their articles, so playwright is needed
    with sync_playwright() as pw:
        browser = pw.chromium.launch() 
        context = browser.new_context()
        page = context.new_page()


        # to access the multiple homonynous "item" elements, must use entries attribute
        for item in feed.entries:
            print("\nLINK: " + item['link'] + "\n\n")
            # exclusion cases because other pages break the algorithm.
            if("article" in item['link']):
                page.goto(
                    item['link'],
                    timeout=60000)  # (milliseconds) maximum operation time  
                scrapeArticleCNN(page)
    
        # clean up 
        context.close()
        browser.close()


def FetchTopStoriesDataFromAlJazeera():
    
    feed = feedparser.parse('https://www.aljazeera.com/xml/rss/all.xml')
    
    title = feed['channel']['title']
    print('--------' + title + "--------\n\n")

    # to access the multiple homonynous "item" elements, must use entries attribute
    for item in feed.entries:
        print(item['title'] + "\n\n")


#https://www.cnn.com/style/article/francois-prost-gentlemens-club/index.html
def scrapeArticleCNN(page: Page):
    
        # Scrape title
        title = page.locator("h1").first.inner_text()
        
        # Scrape time, clean it and simplify; DISREGARDING TIMEZONE NUANCE..
        date = parseDateStringToDateTime(page.locator(".timestamp").first.inner_text())        
        
        # Scrape all content paragraph text
        content = "\n\n".join(page.locator(".article__content p").all_inner_texts())   

        # create the object to return
        articleData = Article(title, date, content)
        
        print("TITLE: " + articleData.title + "\n------------------------------\n")
        print("" + articleData.date.__str__() + "\n------------------------------\n")
        print(articleData.content[:500])

        return articleData
       

