"""
LesEchos Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class LesEchos(gn_collector.Collector):
    """
    A Collector for Les Echos news website (https://www.lesechos.fr).
    """

    NAME = 'Les Echos'
    TWITTER_USER = 'LesEchos'
    PREFIX_URLS = ['https://www.lesechos.fr/']
    BANNED_URLS = []
    RSS_FEED_URLS = []

    CATEGORIES_ASSOCIATION = {
        "Économie France": Category.ECONOMIE,
        "Industrie Services": Category.ECONOMIE,
        "Finances & Marchés": Category.ECONOMIE,
        "Élections": Category.POLITIQUE,
        "Monde": Category.INTERNATIONAL,
        "Tech - Médias": Category.NUMERIQUE,
        "PME Régions": Category.ECONOMIE,
        "Start-up": Category.ECONOMIE,
        "Idées & Débats": Category.DEBATS_ET_OPINIONS,
        "Politique Société": Category.POLITIQUE,
        "Patrimoine": Category.ECONOMIE,
        "Weekend": Category.CULTURE,
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
    def get_category(article: np.Article) -> str:
        """Get an article's category or section."""
        try:
            category = article.meta_data.get('article').get('section')
            if category is None:
                category = "Indéfini"
        except AttributeError:
            category = "Indéfini"
        return category
