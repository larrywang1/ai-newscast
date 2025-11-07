import os
from newsapi import NewsApiClient
from dotenv import load_dotenv


load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

def fetch_stories(topics="", max_stories=25):
    """
    Fetch top headlines from NewsAPI.
    topics: comma-separated categories or keywords
    Returns a list of stories with title, url, source, summary, index
    """
    params = {}
    if topics:
        params["q"] = topics

    data = newsapi.get_top_headlines(
        language="en",
        page_size=max_stories,
        **params
    )

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