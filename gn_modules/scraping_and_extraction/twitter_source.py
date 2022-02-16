"""
Define the class Source responsible for the extraction of article links from twitter tweets.
"""

import os
import datetime as dt
import logging
import re
import typing
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError, URLError
import tweepy
import requests
from requests.exceptions import MissingSchema
import gn_modules.secure_dotenv as gn_dotenv


logger = logging.getLogger('genderednews.twitter_source')
logger_debug = logging.getLogger('genderednews_debug.twitter_source')


class TwitterSource():
    """
    The class Source is responsible for extracting links from twitter tweets.
    """
    HEADERS = {'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5)'
                              'AppleWebKit/537.36 (KHTML, like Gecko)'
                              'Chrome/45.0.2454.101 Safari/537.36')}

    def __init__(self, user: str, source_name: str):
        self.user = user
        self.name = source_name

        # authentication
        self._api = self.create_api()

    def create_api(self):
        """Create an api with API key and access token"""

        gn_dotenv.load_dotenv_secure()
        api_key = os.environ.get('API_KEY')
        api_secret_key = os.environ.get('API_SECRET_KEY')
        access_token = os.environ.get('ACCESS_TOKEN')
        access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

        auth = tweepy.OAuthHandler(api_key, api_secret_key)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)

        try:
            api.verify_credentials()
        except:
            logger.exception("Error during twitter authentication")

        return api

    def find_url(self, tweet):
        """Extract link from the tweet"""
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        url = re.findall(regex, tweet)
        return url[0][0]

    def get_original_twitter_url(self, _url):
        """Get the original url from the extracted url"""
        response = requests.get(url=_url, headers=self.HEADERS)
        data = response.text
        url = re.search("(?P<url>https?://[^\s]+)\"", data).group("url")
        url = urlopen(url).url
        # remove all parameters of the url
        url = urljoin(url, urlparse(url).path)
        return url

    def extract_tweets(self, max_tweets: int) -> typing.List[typing.Dict]:
        """Extract the given number of tweets"""

        articles_entries = []

        for tweet in tweepy.Cursor(self._api.user_timeline, screen_name=self.user, tweet_mode="extended").items(limit=max_tweets):
            try:
                # print(tweet.full_text)
                if hasattr(tweet, 'retweeted_status'):
                    link = self.find_url(tweet.retweeted_status.full_text)
                else:
                    link = self.find_url(tweet.full_text)
            except IndexError:
                continue
            try:
                link = self.get_original_twitter_url(link)
            except (HTTPError, URLError, MissingSchema):
                continue

            logger_debug.debug(f'Article found: {link}')
            articles_entries.append(
                {'link': link, 'date': tweet.created_at})

        logger_debug.debug(f'{len(articles_entries)} articles found.')

        return articles_entries

    def get_entries_from_to(self, from_date: dt.datetime, to_date: dt.datetime) -> typing.List[typing.Dict]:
        """
        Return an array of entries (dict with 'link' & 'date') from this source that has been published between [from_date, to_date].
        The granularity is at the level of the day.
        """
        return [entry for entry in self.extract_tweets(200) if from_date.date() <= entry['date'].date() <= to_date.date()]

    def get_entries_of_yesterday(self) -> typing.List[typing.Dict]:
        """
        Return an array of entries (dict with 'link' & 'date') from this source that has been published yesterday.
        The granularity is at the level of the day.
        """
        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        return self.get_entries_from_to(yesterday, yesterday)
