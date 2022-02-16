"""
Collector class.
"""

import abc
import typing
import logging
import datetime as dt
import newspaper as np

import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter
import gn_modules.article as gn_article
from newspaper.article import ArticleException

logger = logging.getLogger('genderednews.collector')
logger_debug = logging.getLogger('genderednews_debug.collector')


class Collector(abc.ABC):
    """
    Collector is an abstract class.
    Any news source must be a subclass of Collector.
    Any subclass can use the default create_article_from_link method or
    override it for custom extraction of metadatas.
    """
    USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    CATEGORIES_ASSOCIATION = {}
    PREFIX_URLS = []
    BANNED_URLS = []

    def __init__(self, scraping_mode: str) -> None:
        if scraping_mode == "rss":
            self.source: gn_rss.RssSource = None

        else:
            self.source: gn_twitter.TwitterSource = None

        # Config newspaper (to avoid read time out error)
        self.config = np.Config()
        self.config.browser_user_agent = self.USER_AGENT
        self.config.request_timeout = 10

    def scrape_and_extract_articles_from_day_to(self, from_date: dt.datetime, to_date: dt.datetime, max=1000) -> typing.List[gn_article.Article]:
        """
        Return a list of Article from this Collector that has been published in [from_date, to_date].
        The granularity is at the level of the day.
        """
        entries = self.source.get_entries_from_to(from_date, to_date)

        articles = []
        for i, entry in enumerate(entries):

            # Check if url is correct
            if not entry['link'].startswith(tuple(self.BANNED_URLS)) and entry['link'].startswith(tuple(self.PREFIX_URLS)) and len(entry['link']) > 30:
                try:
                    article = self.create_article_from_link(
                        entry['link'], entry['date'])
                except (ArticleException, AttributeError):
                    continue
                logger_debug.debug(f'Article extracted: {article.link}')
                articles.append(article)
                if i + 1 == max:
                    return articles
            else:
                continue

        return articles

    def scrape_and_extract_articles_of_yesterday(self, max=1000) -> typing.List[gn_article.Article]:
        """
        Return a list of Article from this source that has been published yesterday.
        The granularity is at the level of the day.
        """
        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        return self.scrape_and_extract_articles_from_day_to(yesterday, yesterday, max)

    @staticmethod
    def get_title(article: np.Article) -> str:
        """Get an article's title."""
        if article.title:
            return article.title
        return ""

    @staticmethod
    def get_text(article: np.Article) -> str:
        """Get an article's text."""
        return article.text

    @staticmethod
    def get_authors(article: np.Article) -> typing.List[str]:
        """Get an article's authors."""
        if article.authors:
            return article.authors
        return ['Indéfini']

    @staticmethod
    def get_category(article: np.Article) -> str:
        """Get an article's category or section."""
        category = article.meta_data.get('og').get('article').get('section')
        if category is None:
            category = "Indéfini"
        return category

    @staticmethod
    def get_word_count(article: np.Article) -> int:
        """Get an article's text length (word count)."""
        return len(article.text.split())

    @staticmethod
    def get_keywords(article: np.Article) -> typing.List[str]:
        """Get an article's keywords."""
        if article.meta_keywords:
            return article.meta_keywords
        return []

    @staticmethod
    def get_hero_image(article: np.Article) -> str:
        """Get an article's hero or top image link."""
        if article.top_image:
            return article.top_image
        return ""

    @staticmethod
    def get_access(article: np.Article) -> gn_article.Article.Access:
        """Get an article's access level (free or premium)."""
        return gn_article.Article.Access.INDEFINI

    def create_article_from_link(self, link: str, date: dt.datetime = None, html: str = None):
        """Creates an article ready to be stored from a link and the source name."""

        # Download and parse an article from its link
        article = np.Article(link, language='fr', config=self.config)
        if html:
            article.set_html(html)
        else:
            article.download()
        article.parse()

        # Get all info from the parsed article
        title = self.get_title(article)
        text = self.get_text(article)
        authors = self.get_authors(article)
        category = self.get_category(article)
        word_count = self.get_word_count(article)
        # keywords = self.get_keywords(article)
        hero_image = self.get_hero_image(article)
        access = self.get_access(article)

        # Return the object created from the info
        return gn_article.Article({
            'link': link,
            'date': date,
            'title': title,
            'text': text,
            'source': self.source.name,
            'authors': authors,
            'category': category,
            'word_count': word_count,
            'source_name': self.source.name,
            # 'keywords':keywords,
            'hero_image': hero_image,
            'access': access.to_string(),
        })
