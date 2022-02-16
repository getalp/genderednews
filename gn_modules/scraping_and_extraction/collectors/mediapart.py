"""
Mediapart Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class Mediapart(gn_collector.Collector):
    """
    A Collector for Mediapart news website (https://www.mediapart.fr/).
    """

    NAME = 'Mediapart'
    TWITTER_USER = 'Mediapart'
    PREFIX_URLS = ['https://www.mediapart.fr/journal/']
    BANNED_URLS = ['https://www.mediapart.fr/journal/une/']
    RSS_FEED_URLS = [
        'https://www.mediapart.fr/articles/feed',
    ]

    CATEGORIES_ASSOCIATION = {
        "Indéfini": Category.INDEFINI,
    }

    def __init__(self, scraping_mode: str) -> None:
        super().__init__(scraping_mode)
        if scraping_mode == "rss":
            self.source = gn_rss.RssSource(self.RSS_FEED_URLS, self.NAME)
        else:
            self.source = gn_twitter.TwitterSource(
                self.TWITTER_USER, self.NAME)

    @staticmethod
    def get_authors(article: np.Article) -> typing.List[str]:
        """Get an article's authors."""
        try:
            authors = article.meta_data.get('author')
            authors = authors.replace(' et ', ', ').split(', ')
        except AttributeError:
            authors = article.authors
        if not authors:
            authors = ['Indéfini']
        return authors

    # No information in the metadata about the category or section!
    @staticmethod
    def get_category(article: np.Article) -> str:
        """Get an article's category or section."""
        return 'Indéfini'

    # No information in the metadata about the access (free or premium)!
