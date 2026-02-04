import requests 
import feedparser
from playwright.sync_api import Page, sync_playwright
from datetime import datetime
from zoneinfo import ZoneInfo

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



def FetchTopStoriesDataFromCNN():
    ## https://www.cnn.com/services/rss/?no_redirect=true
    #
    #feed = feedparser.parse('http://rss.cnn.com/rss/cnn_topstories.rss')
    feed = feedparser.parse('http://rss.cnn.com/rss/cnn_world.rss')
    
    title = feed['channel']['title']
    print('--------' + title + "--------\n\n")

    # to access the multiple homonynous "item" elements, must use entries attribute
    for item in feed.entries:
        print(item['title'] + "\n\n")



def FetchTopStoriesDataFromAlJazeera():
    
    feed = feedparser.parse('https://www.aljazeera.com/xml/rss/all.xml')
    
    title = feed['channel']['title']
    print('--------' + title + "--------\n\n")

    # to access the multiple homonynous "item" elements, must use entries attribute
    for item in feed.entries:
        print(item['title'] + "\n\n")

def parseDateStringToDateTime(str):
    #example: "Updated 9:13 AM EST, Mon March 6, 2023 "  (CNN article)
    clean = (
        str.replace("Updated ", "")
        .replace("Published ", "")
       .replace(" EST", "")
       .replace(" PST", "")
       .replace(" UTC", "")
       .strip()
    )
    dt = datetime.strptime(clean, "%I:%M %p, %a %B %d, %Y")
    return dt

#https://www.cnn.com/style/article/francois-prost-gentlemens-club/index.html
def scrapeArticleCNN(url):
    
    # CNN dynamically loads their articles, so playwright is needed

    with sync_playwright() as pw:
        
        browser = pw.chromium.launch() 
        context = browser.new_context()
        page = context.new_page()
        page.goto(
            "https://www.cnn.com/style/article/francois-prost-gentlemens-club/index.html",
            timeout=60000)  # (milliseconds) maximum operation time  
            
        # Wait until the article is loaded
        page.wait_for_selector("article")

        title = page.locator("h1").first.inner_text()
        date = parseDateStringToDateTime(page.locator(".timestamp").first.inner_text())        
        content = "\n\n".join(page.locator(".article__content p").all_inner_texts())   

        print(title)
        print(date)
        print(content[:500])

        context.close()
        browser.close()
        
       

