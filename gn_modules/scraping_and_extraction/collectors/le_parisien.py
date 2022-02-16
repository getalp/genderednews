"""
LeParisien Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class LeParisien(gn_collector.Collector):
    """
    A Collector for Le Parisien news website (https://www.leparisien.fr).
    """

    NAME = 'Le Parisien'
    TWITTER_USER = 'le_Parisien'
    PREFIX_URLS = ['https://www.leparisien.fr/']
    BANNED_URLS = []
    RSS_FEED_URLS = [
        'https://feeds.leparisien.fr/leparisien/rss/faits-divers',
        'https://feeds.leparisien.fr/leparisien/rss/politique',
        'https://feeds.leparisien.fr/leparisien/rss/economie',
        'https://feeds.leparisien.fr/leparisien/rss/international',
        'https://feeds.leparisien.fr/leparisien/rss/sports',
        'https://feeds.leparisien.fr/leparisien/rss/culture-loisirs',
        'https://feeds.leparisien.fr/leparisien/rss/immobilier',
        'https://feeds.leparisien.fr/leparisien/rss/environnement',
        'https://feeds.leparisien.fr/leparisien/rss/societe',
        'https://feeds.leparisien.fr/leparisien/rss'
    ]

    CATEGORIES_ASSOCIATION = {
        "/economie/": Category.ECONOMIE,
        "/societe/": Category.SOCIETE,
        "/politique/": Category.POLITIQUE,
        "/sports/": Category.SPORT,
        "/culture-loisirs/": Category.CULTURE,
        "/international/": Category.INTERNATIONAL,
        "/faits-divers/": Category.FAIT_DIVERS,
        "/immobilier/": Category.ECONOMIE,
        "/environnement/": Category.SCIENCE_ET_ENVIRONNEMENT,
        "/meteo/": Category.SCIENCE_ET_ENVIRONNEMENT,
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
