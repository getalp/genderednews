"""
L'Equipe Collector.
"""

import typing
import newspaper as np
from urllib.request import urlopen
import bs4 as bs

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class LEquipe(gn_collector.Collector):
    """
    A Collector for L'Equipe news website (https://www.lequipe.fr).
    """

    NAME = "L'Equipe"
    TWITTER_USER = 'lequipe'
    PREFIX_URLS = ['https://www.lequipe.fr/']
    BANNED_URLS = ['https://www.lequipe.fr/abonnement/',
                   'https://www.lequipe.fr/explore/']
    RSS_FEED_URLS = [
        'http://www.lequipe.fr/rss/actu_rss.xml',
        'http://www.lequipe.fr/rss/actu_rss_Football.xml',
        'http://www.lequipe.fr/rss/actu_rss_Transferts.xml',
        'http://www.lequipe.fr/rss/actu_rss_Auto-Moto.xml',
        'http://www.lequipe.fr/rss/actu_rss_F1.xml',
        'http://www.lequipe.fr/rss/actu_rss_Rallye.xml',
        'http://www.lequipe.fr/rss/actu_rss_Moto.xml',
        'http://www.lequipe.fr/rss/actu_rss_Tennis.xml',
        'http://www.lequipe.fr/rss/actu_rss_Golf.xml',
        'http://www.lequipe.fr/rss/actu_rss_Rugby.xml',
        'http://www.lequipe.fr/rss/actu_rss_Basket.xml',
        'http://www.lequipe.fr/rss/actu_rss_Hand.xml',
        'http://www.lequipe.fr/rss/actu_rss_Cyclisme.xml',
        'http://www.lequipe.fr/rss/actu_rss_Judo.xml',
        'http://www.lequipe.fr/rss/actu_rss_Ski.xml',
        'http://www.lequipe.fr/rss/actu_rss_Athletisme.xml',
        'http://www.lequipe.fr/rss/actu_rss_Voile.xml',
        'http://www.lequipe.fr/rss/actu_rss_Natation.xml',
        'http://www.lequipe.fr/rss/actu_rss_Escrime.xml',
        'http://www.lequipe.fr/rss/actu_rss_Volley.xml',
    ]

    CATEGORIES_ASSOCIATION = {
        "Sport": Category.SPORT,
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
        return "Sport"

    @staticmethod
    def get_text(article: np.Article):
        """Get text from the article"""
        text = ""
        html = urlopen(article.url).read()
        page = bs.BeautifulSoup(html, features="html.parser")
        for paragraph in page.find_all('p'):
            text += "\n" + paragraph.getText()
        return text
