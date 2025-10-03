import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from news_api import fetch_trending_articles
from issue_selector import filter_articles
from llm_generator import generate_llm_output

def main():
    filtered_articles = []
    seen_content = set()
    iteration_count = 0
    max_iterations = 4

    while len(filtered_articles) < 4 and iteration_count < max_iterations:
        data = fetch_trending_articles()
        articles = data.get("results", [])
        iteration_count += 1
        print(f"\n📰 Received {len(articles)} articles from API (Page {iteration_count} of {max_iterations})")

        if len(articles) == 0:
            print("⚠️ API response:", data)
            break

        if articles:
            sample_title = articles[0].get('title') or ''
            sample_desc = articles[0].get('description') or ''
            sample_url = articles[0].get('url', '')
            print("\n🔎 Sample article:")
            print(f"Title: {sample_title}")
            print(f"Description: {sample_desc}")
            print(f"URL: {sample_url}")
            print(f"Source: {articles[0].get('source_id')}")

        new_filtered = filter_articles(articles)
        for article in new_filtered:
            if len(filtered_articles) >= 4:
                break  # Cap at 4

            title = article.get('title') or ''
            desc = article.get('description') or ''
            content_key = (title.lower(), desc.lower())

            if content_key not in seen_content:
                filtered_articles.append(article)
                seen_content.add(content_key)

        if len(filtered_articles) < 4:
            if iteration_count >= max_iterations:
                print(f"\n⛔ Reached max API calls ({max_iterations}).")
                break
            print(f"\n🔁 Only found {len(filtered_articles)} relevant articles. Fetching more...")

    print(f"\n✅ Found {len(filtered_articles)} relevant articles:\n")

    for i, article in enumerate(filtered_articles):
        title = article.get('title') or ''
        desc = article.get('description') or ''
        source = article.get('source_id', '')
        pub_date = article.get('pubDate', '')
        url = article.get('url', '')

        print(f"\n{i+1}. 🗞️ Title: {title}")
        print(f"   📃 Description: {desc}")
        print(f"   🏷️ Source: {source} | 📅 Published: {pub_date}")
        print(f"   🔗 URL: {url}")

        llm_result = generate_llm_output(article)

        if "error" in llm_result:
            print(f"   ❌ LLM Error: {llm_result['error']}")
            print(f"   🔧 Raw Output: {llm_result.get('raw', 'N/A')}")
        else:
            print(f"   🧭 Issue: {llm_result['issue']}")
            print(f"   📊 Local Impact: {llm_result['local_stat']}")
            print(f"\n   📬 Donor Email:\n{llm_result['email']}\n")

if __name__ == "__main__":
    main()
