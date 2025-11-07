import os
from newsapi import NewsApiClient
from dotenv import load_dotenv


load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

def fetch_stories(topics="", max_stories=25):
    params = {}
    if topics:
        params["q"] = topics

    #use the api to get headlines
    data = newsapi.get_top_headlines(
        language="en",
        page_size=max_stories,
        **params
    )

    #append the data for these headlines into a variable then return it
    #get is used to make sure that if a value is not found would not create an error
    articles = data.get("articles", [])
    stories = []
    for i, a in enumerate(articles):
        stories.append({
            "title": a.get("title", ""),
            "url": a.get("url", ""),
            "source": a.get("source", {}).get("name", ""),
            "summary": a.get("description", "") or "",
            "index": i
        })
    return stories