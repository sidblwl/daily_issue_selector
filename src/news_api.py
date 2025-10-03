import requests
import yaml

def load_config():
    with open("config/settings.yaml") as f:
        return yaml.safe_load(f)

_next_page = 1  # guardian uses numeric pages

def fetch_trending_articles():
    global _next_page
    try:
        config = load_config()
        api_key = config["news_api"]["key"]
        url = "https://content.guardianapis.com/search"

        params = {
            "api-key": api_key,
            "section": "us-news",  # covers US politics too
            "page": _next_page,
            "page-size": 10,
            "order-by": "newest",
            "show-fields": "body,headline,trailText"
        }

        print(f"\nFetching articles from {url} (page {_next_page})...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = data.get("response", {}).get("results", [])
        if not results:
            print("⚠️ No articles found")
            return {"results": [], "nextPage": None}

        # transform guardian data to match your app’s expected structure
        articles = []
        for item in results:
            fields = item.get("fields", {})
            articles.append({
                "title": fields.get("headline", item.get("webTitle", "")),
                "description": fields.get("trailText", ""),
                "full_text": fields.get("body", ""),
                "source_id": "guardian",
                "pubDate": item.get("webPublicationDate", ""),
                "url": item.get("webUrl", "")
            })

        # increment page for next call
        _next_page += 1
        return {"results": articles, "nextPage": _next_page}

    except requests.exceptions.RequestException as e:
        print(f"🛑 Error fetching articles: {str(e)}")
        return {"results": [], "nextPage": None}
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {"results": [], "nextPage": None}
