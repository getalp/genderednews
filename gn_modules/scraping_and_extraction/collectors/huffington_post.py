"""
Huffington Post Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class HuffingtonPost(gn_collector.Collector):
    """
    A Collector for Huffington Post news website (https://www.huffingtonpost.fr/).
    """

    NAME = 'Huffington Post'
    TWITTER_USER = 'LeHuffPost'
    PREFIX_URLS = ['https://www.huffingtonpost.fr/entry/']
    BANNED_URLS = []
    RSS_FEED_URLS = ['https://www.huffingtonpost.fr/feeds/index.xml']
    CATEGORIES_ASSOCIATION = {
        'POLITIQUE': Category.POLITIQUE,
        'LIFE': Category.CULTURE,
        'Environnement': Category.SCIENCE_ET_ENVIRONNEMENT,
        'SCIENCE': Category.SCIENCE_ET_ENVIRONNEMENT,
        'CULTURE': Category.CULTURE,
        'Divertissement': Category.CULTURE,
        'INTERNATIONAL': Category.INTERNATIONAL,
        'Techno': Category.NUMERIQUE,
        'ÉCONOMIE': Category.ECONOMIE,
        'SPORT': Category.SPORT,
        'JUSTICE': Category.POLITIQUE,
        'Actualités': Category.INDEFINI,
        'FAITS DIVERS': Category.FAIT_DIVERS,
        'People': Category.PEOPLE,
        'LE BON LIEN': Category.PEOPLE,
        'Indéfini': Category.INDEFINI,
    }

    def __init__(self, scraping_mode: str) -> None:
        super().__init__(scraping_mode)
        if scraping_mode == "rss":
            self.source = gn_rss.RssSource(self.RSS_FEED_URLS, self.NAME)
        else:
            self.source = gn_twitter.TwitterSource(
                self.TWITTER_USER, self.NAME)

    # def get_authors(article: np.Article) -> typing.List[str]:

    @staticmethod
    def get_category(article: np.Article) -> str:
        """Get an article's category or section."""
        try:
            category = article.meta_data.get('article').get('section')
            if category is None:
                category = "Indéfini"
        except AttributeError:
            category = "Indéfini"
        return category

    @staticmethod
    def get_keywords(article: np.Article) -> typing.List[str]:
        """Get an article's keywords."""
        try:
            keywords = article.meta_data.get('keywords').split(',')
            if keywords is None:
                keywords = []
        except AttributeError:
            keywords = []
        return keywords

    # def get_access(article: np.Article) -> Article.Access:
