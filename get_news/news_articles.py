import sys
import os

sys.path.insert(0, os.path.abspath('/home/sangu/pygooglenews/pygooglenews'))

from google_news import GoogleNews
from googlenewsdecoder import new_decoderv1
from newspaper import Article

def get_og_link(source_url):

    interval_time = 5 # default interval is 1 sec, if not specified

    try:
        decoded_url = new_decoderv1(source_url, interval=interval_time)
        if decoded_url.get("status"):
            #print("Decoded URL:", decoded_url["decoded_url"])
            return decoded_url
        else:
            pass
            #print("Error:", decoded_url["message"])
    except Exception as e:
        #print(f"Error occurred: {e}")
        return f"{decoded_url["message"]}, Error occurred: {e}"

def get_top_news(country:str, country_code:str) :

    gn = GoogleNews(country=country_code)
    top_news = gn.geo_headlines(country)

    articles = []

    for article in top_news['entries']:
        articles.append(article['sub_articles'])

    for sub_article in articles:
        for index, sub_art in enumerate(sub_article):
            url = sub_art['url']
            og_url = get_og_link(url)
            og_url = og_url['decoded_url']
            article = Article(og_url)
            article.download()
            article.parse()
            sub_article[index]['published'] = article.publish_date
            sub_article[index]['article'] = article.text

    return articles


