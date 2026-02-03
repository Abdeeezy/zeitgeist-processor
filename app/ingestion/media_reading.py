import requests 
import feedparser


#https://feedparser.readthedocs.io/en/latest/    api


# USE RSS FEEDS TO FETCH THE STORIES AND THEIR RESPECTIVE LINKS.
#  THEN USE DYNAMIC SCRAPING TO READ THE ARTICLE'S CONTENTS
#    





def simpleFetchPrintContent(url):
    response = requests.get(url)
    print(response.content)


def FetchTopStoriesDataFromCNN():
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


