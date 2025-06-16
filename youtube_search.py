import requests
import re

SCRAPE_DO_KEY = "25a5d54f8e64460c83cc9f81e367d1be5b9406f983d"


def search_youtube_video(query: str) -> str:
    google_query = f"site:youtube.com -inurl:shorts -inurl:playlist {query}"
    raw_search_url = f"https://www.google.com/search?q={google_query}&num=3"

    # Properly encode the entire Google URL
    encoded_search_url = requests.utils.quote(raw_search_url, safe='')

    # Scrape.do URL with encoded target
    proxy_url = f"https://api.scrape.do?token={SCRAPE_DO_KEY}&url={encoded_search_url}"
    
    response = requests.get(proxy_url, timeout=10)
    
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Scrape.do error: {response.status_code}")

    html = response.text

    # Extract the first valid YouTube video URL
    matches = re.findall(r"https://www\.youtube\.com/watch\?v=[\w-]+", html)
    if matches:
        return matches[0]
    else:
        raise Exception("No YouTube video link found.")

if __name__=="__main__":
    video_url = search_youtube_video("Types of Machine Learning (Supervised, Unsupervised, Reinforcement)")
    print("Video URL:", video_url)
