"""
Define the class Source responsible for the extraction of article links from rss feeds.
"""

import datetime as dt
import time
import typing
import logging
import feedparser
import newspaper as np
from newspaper.article import ArticleException

logger = logging.getLogger('genderednews.rss_source')
logger_debug = logging.getLogger('genderednews_debug.rss_source')


class RssSource():
    """
    The class Source is responsible for extracting links from rss feeds.
    """
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'

    def __init__(self, rss_feed_links: typing.List[str], source_name: str) -> None:
        self.rss_feed_links = rss_feed_links
        self.name = source_name

        # Config newspaper (to avoid read time out error)
        self.config = np.Config()
        self.config.browser_user_agent = self.USER_AGENT
        self.config.request_timeout = 10

    def _scrape_one_xml(self, source_link: str) -> typing.List[typing.Dict]:
        """
        Scrape all the articles links from one xml RSS feed.
        """

        # Parse the xml file
        rss_feed = feedparser.parse(source_link)

        for entry in rss_feed.entries:
            # Check if there are missing links
            try:
                if not entry.link:
                    raise RuntimeError(
                        'No link for {entry}. You can try to look into rss_feed variable.')
            except AttributeError:
                continue

            # Conversion of published date in datetime format
            try:
                entry.datetime = dt.datetime.fromtimestamp(
                    time.mktime(entry.published_parsed))

            # Retrieve published date in the metadata of the article
            except (AttributeError, KeyError):
                article = np.Article(
                    entry.link, language='fr', config=self.config)
                try:
                    article.download()
                    article.parse()
                except ArticleException:
                    # Ignore this article (article url not working)
                    entry.datetime = dt.datetime.now() - dt.timedelta(days=10)
                    continue
                try:
                    entry.datetime = article.publish_date.replace(tzinfo=None)
                except AttributeError:
                    # Ignore this article (publish_date == None)
                    entry.datetime = dt.datetime.now() - dt.timedelta(days=10)
                    continue

        # Return the entries published yesterday
        return rss_feed.entries

    def scrape_all_xml(self) -> typing.List[typing.Dict]:
        """
        Return an array of all entries (dict with 'link' & 'date') from this source.
        """

        article_entries = []
        for feed in self.rss_feed_links:
            newsfeed = self._scrape_one_xml(feed)
            for entry in newsfeed:
                try:
                    if entry.link:
                        logger_debug.debug(f'Article found: {entry.link}')
                        article_entries.append(
                            {'link': entry.link, 'date': entry.datetime})
                except AttributeError:
                    continue
        logger_debug.debug(f'{len(article_entries)} articles found.')

        return article_entries

    def get_entries_from_to(self, from_date: dt.datetime, to_date: dt.datetime) -> typing.List[typing.Dict]:
        """
        Return an array of entries (dict with 'link' & 'date') from this source that has been published between [from_date, to_date].
        The granularity is at the level of the day.
        """

        return [entry for entry in self.scrape_all_xml() if from_date.date() <= entry['date'].date() <= to_date.date()]

    def get_entries_of_yesterday(self) -> typing.List[typing.Dict]:
        """
        Return an array of entries (dict with 'link' & 'date') from this source that has been published yesterday.
        The granularity is at the level of the day.
        """

        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        return self.get_entries_from_to(yesterday, yesterday)
