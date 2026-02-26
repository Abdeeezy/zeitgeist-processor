import requests 
import feedparser
from playwright.sync_api import Page, sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime

from app.models.ArticleDataModel import Article
from app.models.NewsSiteDataModel import NewsCollection



# USE RSS FEEDS TO FETCH THE STORIES AND THEIR RESPECTIVE LINKS.
#  THEN USE STATIC OR DYNAMIC SCRAPING TO READ THE ARTICLE'S CONTENTS
#
#  EACH NEWS-WEBSITE NEEDS A UNIQUE SCRAPING ALGORITHM.    






## main functions
async def FetchTopStoriesDataFromBBC():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        articleCollection = []

        page.goto('https://www.bbc.com/news', timeout=30000)

        # Grab all headline elements and extract their parent anchor URLs first,
        # before navigating away from the page.
        headline_elements = page.query_selector_all('[data-testid="card-headline"]')

        articles_to_visit = []
        for el in headline_elements:
            headline_text = el.inner_text().strip()

            # Walk up the DOM to find the nearest <a> ancestor
            anchor = el.evaluate_handle("""
                node => {
                    let current = node;
                    while (current && current.tagName !== 'A') {
                        current = current.parentElement;
                    }
                    return current;
                }
            """)

            href = anchor.get_property('href')
            url = await href.json_value() if href else None

            # Some links are relative paths
            if url and url.startswith('/'):
                url = 'https://www.bbc.com' + url

            if url:
                articles_to_visit.append((headline_text, url))

        # Now visit each article page and extract the data
        for headline_text, url in articles_to_visit:
            try:
                page.goto(url, timeout=30000)
                page.wait_for_load_state('domcontentloaded')

                # --- Date ---
                # BBC typically uses a <time> element with a datetime attribute
                date = ""
                time_el = page.query_selector('time')
                if time_el:
                    date = time_el.get_attribute('datetime') or ""

                # --- Content ---
                # BBC article body lives in elements with data-component="text-block"
                # Scrape all content paragraph text
                content = "\n\n".join(page.locator(".article__content p").all_inner_texts())   
        

                article = Article(
                    headline=headline_text,
                    date=date,
                    content=content,
                    url=url
                )
                articleCollection.append(article)

            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue

        context.close()
        browser.close()

        return NewsCollection("BBC", articleCollection)




#cnn rss feed is 3 years outdated. It's not current seems to just cycle old topics....
def FetchTopStoriesDataFromCNN():
    ## https://www.cnn.com/services/rss/?no_redirect=true
    #
    #feed = feedparser.parse('http://rss.cnn.com/rss/cnn_topstories.rss')
    feed = feedparser.parse('http://rss.cnn.com/rss/cnn_world.rss')
    
    headline = feed['channel']['title']
    print('--------' + headline + "--------\n\n")

    # CNN dynamically loads their articles, so playwright is needed
    with sync_playwright() as pw:
        browser = pw.chromium.launch() 
        context = browser.new_context()
        page = context.new_page()

        articleCollection = list[Article]()


        # to access the multiple homonynous "item" elements, must use entries attribute
        for item in feed.entries:
            try:
                print("\nLINK: " + item['link'] + "\n\n")
                # exclusion cases because other pages break the algorithm.
                if("article" in item['link']):
                    page.goto(
                        item['link'],
                        timeout=30000)  # (milliseconds) maximum operation time  
                    articleCollection.append(scrapeArticleCNN(page)) # add to list of articles

            except PlaywrightTimeoutError:
                print("⚠️ Timeout — skipping:", item['link'])
                continue
    
        # clean up 
        context.close()
        browser.close()

        return NewsCollection("CNN", articleCollection)


def scrapeArticleCNN(page: Page):
    
        # Scrape title
        title = page.locator("h1").first.inner_text()
        
        # Scrape time, clean it and simplify; DISREGARDING TIMEZONE NUANCE..
        date = parseDateStringToDateTime(page.locator(".timestamp").first.inner_text(), "CNN")        
        
        # Scrape all content paragraph text
        content = "\n\n".join(page.locator(".article__content p").all_inner_texts())   
        
        # create the object to return
        articleData = Article(title, date, content, page.url)

        return articleData


def FetchTopStoriesDataFromAlJazeera():
    
    feed = feedparser.parse('https://www.aljazeera.com/xml/rss/all.xml')
    
    headline = feed['channel']['title']
    print('--------' + headline + "--------\n\n")

    # AlJazeera dynamically loads their articles, so playwright is needed
    with sync_playwright() as pw:
        browser = pw.chromium.launch() 
        context = browser.new_context()
        page = context.new_page()

        articleCollection = list[Article]()


        # to access the multiple homonynous "item" elements, must use entries attribute
        for item in feed.entries:
            try:
                print("\nLINK: " + item['link'] + "\n\n")
                page.goto(
                    item['link'],
                    timeout=30000)  # (milliseconds) maximum operation time  
                articleCollection.append(scrapeArticleAlJazeera(page)) # add to list
            except PlaywrightTimeoutError:
                print("⚠️ Timeout — skipping:", item['link'])
                continue
    
        # clean up 
        context.close()
        browser.close()

        return  NewsCollection("AlJazeera", articleCollection)
def scrapeArticleAlJazeera(page: Page):
    
        # Scrape title
        title = page.locator("h1").first.inner_text()
        
        # Scrape time, clean it and simplify; DISREGARDING TIMEZONE NUANCE..
        date = parseDateStringToDateTime(page.locator(".date-simple").first.inner_text(), "AlJazeera")        
        
        # Scrape all content paragraph text
        if("/video/" in page.url):
            content = "\n\n".join(page.locator("p.article__subhead").all_inner_texts())   
        else:
            content = "\n\n".join(page.locator("[class$='--all-content'] p").all_inner_texts())  #'($=)' wildcard selector in CSS targets elements whose attribute value ends with a specific string

        # create the object to return
        articleData = Article(title, date, content, page.url)

        return articleData


def FetchTopStoriesDataFromNYTimes():
    
    feed = feedparser.parse('https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml')
    
    headline = feed['channel']['title']
    print('--------' + headline + "--------\n\n")

    # New York Times dynamically loads their articles, but also locks articles behind a paywall.
    # however, the RSS feed supplies "categories"/"keywords". 
    #   That alongside the headline, should be enough i guess..
    
    articleCollection = list[Article]()

    for item in feed.entries:
        
        # each <category> is found in the `item.tags` attribute 
        if hasattr(item, "tags"):
            categories = [tag.term for tag in item.tags]
        #     print("Categories/Keywords:", categories)
        # else:
        #     print("Categories: None")

        articleCollection.append(Article(headline, "N/A", "PAYBLOCKED", item.link, categories)) # add to list
        print()

    return NewsCollection("NYTimes", articleCollection)

        




## Helper functions
def parseDateStringToDateTime(dateStr:str, source:str):
    if(source == "CNN"):
        #example: "Updated 9:13 AM EST, Mon March 6, 2023 "  (CNN article)
        clean = (
            dateStr.replace("Updated ", "")
            .replace("Published ", "")
            .replace(" EST", "")
            .replace(" PST", "")
            .replace(" UTC", "")
            .replace(" EDT", "")
            .strip()
        )
        return datetime.strptime(clean, "%I:%M %p, %a %B %d, %Y")

    elif(source=="AlJazeera"):
        clean = (
            dateStr.replace("Updated On ", "")
            .replace("Published On ", "")
            .strip()
        )
        #"Published On 4 Feb 2026\n4 Feb 2026" how it looks
        clean = clean.splitlines()[0]  # ← important
        return datetime.strptime(clean, "%d %b %Y")
    else:
        return datetime.strptime("January 1, 1777", "%B %d, %Y") # placeholder data in case nothing runs...
