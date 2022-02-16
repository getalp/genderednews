"""
Twitter api: extract tweets
"""

import os
import re
import sys
from urllib.request import urlopen
from urllib.error import HTTPError
from tweepy.error import TweepError
import requests
import tweepy

import gn_modules.secure_dotenv as gn_dotenv

HEADERS = {'USER-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                          'AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/45.0.2454.101 Safari/537.36')}

# USER = "libe"
# USER = "lemondefr"
# USER = "lequipe"
# USER = "le_Parisien"
USER = "LesEchos"
# USER = "LaCroix"
# USER = "Le_Figaro"
# USER = "Mediapart"
# USER = "LeHuffPost"


def create_api():
    """Create an api with API key and access token"""

    gn_dotenv.load_dotenv_secure()
    api_key = os.environ.get('API_KEY')
    api_secret_key = os.environ.get('API_SECRET_KEY')
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    _api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    try:
        _api.verify_credentials()
    except TweepError:
        print("Error during twitter authentication")
        sys.exit()

    return _api


def find_url(tweet):
    """Extract link from the tweet"""
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, tweet)
    return url[0][0]


def get_original_twitter_url(_url):
    """Get the original url from the extracted url"""
    response = requests.get(url=_url, headers=HEADERS)
    data = response.text
    url = re.search("(?P<url>https?://[^\s]+)\"", data).group("url")
    url = urlopen(url).url
    return url


def extract_tweets_and_print_results(_api, max_tweets: int):
    """Extract the given number of tweets and print the results"""
    articles_entries = []

    for tweet in tweepy.Cursor(_api.user_timeline, screen_name=USER, tweet_mode="extended").items(limit=max_tweets):
        try:
            # print(tweet.full_text)
            if hasattr(tweet, 'retweeted_status'):
                link = find_url(tweet.retweeted_status.full_text)
            else:
                link = find_url(tweet.full_text)
        except IndexError:
            continue
        print(link) # print link extracted
        try:
            link = get_original_twitter_url(link)
        except HTTPError:
            continue
        articles_entries.append({'link': link, 'date': tweet.created_at})

    print('\n\n\n\n')
    for article in articles_entries:
        print(article['link'])
        print(article['date'])

    print("Total: " + str(len(articles_entries)))


api = create_api()
extract_tweets_and_print_results(api, 50)
