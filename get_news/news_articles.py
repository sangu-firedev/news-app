import sys
import os
from time import sleep

sys.path.insert(0, os.path.abspath('/home/sangu/pygooglenews/pygooglenews'))

from tqdm import tqdm
from google_news import GoogleNews
from googlenewsdecoder import new_decoderv1 
from newspaper import Article
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_og_link(source_url, interval=5):
    """Decode the original link from the source URL."""
    try:
        decoded_url = new_decoderv1(source_url, interval = interval)
        if decoded_url.get("status"):
            return decoded_url["decoded_url"]
        else:
            print("Error:", decoded_url["message"])
            return None 
    except Exception as e:
        print(f"Error occurred: {e}")
        return None 

def fetch_article_content(og_url):
    """Fetches and parses article content."""
    try:
        article = Article(og_url)
        article.download()
        article.parse()
        return article.publish_date, article.text
    except Exception as e:
        print(f"Error fetching article content: {e}")
        return None, None

def process_single_article(sub_art, topic):
    """processing single article and grouping them according to their respective topics"""
    try:
        url = sub_art['url']
        og_url = get_og_link(url)
        if og_url:
            publish_date, article_text = fetch_article_content(og_url)
            if article_text:
                sub_art['topic'] = topic 
                sub_art['published'] = publish_date
                sub_art['article'] = article_text
                return sub_art
        print(f'Failed to decode or retrieve article at URL: {url}')
    except Exception as e:
        print(f'Error in process_single_article: {e}')
    return None

def extract_news(entries, threads):
    """Extracting articles concurrently while keeping them grouped by thier topic"""
    articles_data = {}

    # Flatten the sub_articles list, but group them by thier parent article(topic)
    sub_articles = []
    for article in entries:
        topic = article.get('title', 'Unknown')
        for sub_art in article.get('sub_articles', []):
            sub_articles.append((sub_art, topic))

    # Use ThreadPoolExecutor for multi-threading
    with ThreadPoolExecutor(max_workers=threads) as executor: # Adjust max_workers as per your requirement
        futures = {executor.submit(process_single_article, sub_art, topic) : sub_art for sub_art, topic in sub_articles} 
        # Collect the results as they complete
        for future in tqdm(as_completed(futures), desc="Extracting Articles", total=len(sub_articles)):
            result = future.result()
            if result:
                topic = result.get('topic')
                if topic not in articles_data:
                    articles_data[topic] = []
                articles_data[topic].append(result)
    
    return articles_data

def get_top_news(country:str, country_code:str, threads=10) :
    """Retrieve and decode top news articles for a specific country."""
    gn = GoogleNews(country=country_code)
    top_news = gn.geo_headlines(country)
    entries = top_news['entries']

    articles = extract_news(entries, threads)
    return articles