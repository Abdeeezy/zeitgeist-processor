from wsgiref import headers
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
def FetchTopStoriesDataFromBBC():

    print('--------' + "BBC News - British Broadcast Channel" + "--------\n\n")

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
            url = el.evaluate("""
                node => {
                    let current = node;
                    while (current && current.tagName !== 'A') {
                        current = current.parentElement;
                    }
                    return current ? current.href : null;
                }
            """)
            if url:
                articles_to_visit.append((headline_text, url))

        # Now visit each article page and extract the data
        for headline_text, url in articles_to_visit:
                try:
                    page.goto(url, timeout=30000)
                    page.wait_for_load_state('domcontentloaded')
                    print("\nLINK: " + url + "\n\n")

                    # --- Date ---
                    # BBC typically uses a <time> element with a datetime attribute
                    date = ""
                    time_el = page.query_selector('time')
                    if time_el:
                        date = time_el.get_attribute('datetime') or ""

                    # --- Content ---
                    # BBC article body lives in elements with data-component="text-block"
                    # Scrape all content paragraph text
                    content = "\n\n".join(page.locator("p").all_inner_texts())   

                    article = Article(
                        headline=headline_text,
                        date=date,
                        content=content,
                        url=url,
                        source="BBC"
                    )
                    articleCollection.append(article)

                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")
                    continue
           
           
        context.close()
        browser.close()

        return NewsCollection("BBC", articleCollection)




# BOT-BLOCKS, UNUSABLE...
def FetchTopStoriesDataFromCBC():

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get('https://www.cbc.ca/webfeed/rss/rss-topstories', headers=headers)
    feed = feedparser.parse(response.content)
    # the above was used to replace -> `feed = feedparser.parse('https://www.cbc.ca/webfeed/rss/rss-topstories')`
    #        CBC might have been blocking the request without a user-agent header, which is common practice to prevent bots from scraping. By adding a user-agent header that mimics a real browser, we can often bypass such blocks
    
    headline = feed['channel']['title']
    print('--------' + headline + "--------\n\n")

    # CBC dynamically loads their articles, so playwright is needed
    with sync_playwright() as pw:
        browser = pw.chromium.launch() 
        context = browser.new_context( # this is to attempt to bypass bot-detection by mimicking a real user's browser context.
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            locale='en-CA',
        ) 
        page = context.new_page()
       
        articleCollection = list[Article]()


        # to access the multiple homonynous "item" elements, must use entries attribute
        for item in feed.entries:
            try:
                print("\nLINK: " + item['link'] + "\n\n")
                # exclusion cases 
                if("/player/" not in item['link'] and "/radio/" not in item['link'] and "/sports/" not in item['link']):
                    page.goto(
                        item['link'].split('?')[0], # remove query parameters (the `?cmp=rss` at the end) to avoid potential issues with dynamic content loading or tracking parameters that might interfere with scraping.
                        timeout=30000)  # (milliseconds) maximum operation time  
                    
                    # Scrape title
                    title = page.locator("h1").first.inner_text()
                    
                    # Extract date
                    # CBC typically uses a <time> element with a datetime attribute
                    date = ""
                    time_el = page.query_selector('time')
                    if time_el:
                        date = time_el.get_attribute('datetime') or ""

                    # Scrape all content paragraph text
                    content = "\n\n".join(page.locator("p:not([class])").all_inner_texts()) 
                        # `p:not([class])` matches only <p> elements that have no class attribute at all, which should exclude the author biography paragraphs (and any other styled paragraphs)  
                    
                    print('title: ' + title)
                    print('content: ' + content[:200] + "...\n\n")

                    # create the object to return
                    articleData = Article(title, date, content, page.url, source="CBC")
                    articleCollection.append(articleData) # add to list of articles

            except PlaywrightTimeoutError:
                print("⚠️ Timeout — skipping:", item['link'])
                continue
    
        # clean up 
        context.close()
        browser.close()

        return NewsCollection("CBC", articleCollection)


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
                articleData = Article(title, date, content, page.url, source="AlJazeera")
                articleCollection.append(articleData) # add to list

            except PlaywrightTimeoutError:
                print("⚠️ Timeout — skipping:", item['link'])
                continue
    
        # clean up 
        context.close()
        browser.close()

        return  NewsCollection("AlJazeera", articleCollection)

def FetchTopStoriesDataFromNYTimes():
    
    feed = feedparser.parse('https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml')
    
    headline = feed['channel']['title']
    print('--------' + headline + "--------\n\n")

    # New York Times dynamically loads their articles, but also locks articles behind a paywall.
    # however, the RSS feed supplies "categories"/"keywords". 
    #   That alongside the headline, should be enough i guess..
    
    articleCollection = list[Article]()

    for item in feed.entries:
       
        categories = [] #empty array fallback in case there are no supplied categories/keywords
         
        # each <category> is found in the `item.tags` attribute 
        if hasattr(item, "tags"):
            categories = [tag.term for tag in item.tags]
        # else:
        #     print("Categories: None")

        print('url: ' + item.link)

        articleCollection.append(Article(item.title, "N/A", "", item.link, categories, source="NYTimes")) # add to list
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
