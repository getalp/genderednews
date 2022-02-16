"""
La Croix Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class LaCroix(gn_collector.Collector):
    """
    A Collector for La Croix news website (https://www.la-croix.com).
    """

    NAME = 'La Croix'
    TWITTER_USER = 'LaCroix'
    PREFIX_URLS = ['https://www.la-croix.com/']
    BANNED_URLS = []
    RSS_FEED_URLS = [
        'http://www.la-croix.com/RSS/UNIVERS_WFRA',
        'http://www.la-croix.com/RSS/UNIVERS_WMON',
        'http://www.la-croix.com/RSS/UNIVERS_WECO',
        'http://www.la-croix.com/RSS/UNIVERS_WSPO',
        'http://www.la-croix.com/RSS/UNIVERS_WFAM',
        'http://www.la-croix.com/RSS/UNIVERS_WSCI',
        'http://www.la-croix.com/RSS/UNIVERS_WCLT',
        'http://www.la-croix.com/RSS/UNIVERS_WDEB',
        'http://www.la-croix.com/RSS/UNIVERS_WREL',
        'http://www.la-croix.com/RSS/WFRA-POL',
        'http://www.la-croix.com/RSS/WFRA-JUST',
        'http://www.la-croix.com/RSS/WFRA-SECU',
        'http://www.la-croix.com/RSS/WFRA-EDU',
        'http://www.la-croix.com/RSS/WFRA-EXCL',
        'http://www.la-croix.com/RSS/WFRA-IMMI',
        'http://www.la-croix.com/RSS/WMON-EUR',
        'http://www.la-croix.com/RSS/WMON-AFR',
        'http://www.la-croix.com/RSS/WMON-AME',
        'http://www.la-croix.com/RSS/WMON-MOY',
        'http://www.la-croix.com/RSS/WMON-ASI-OCE',
        'http://www.la-croix.com/RSS/WECO-FRA',
        'http://www.la-croix.com/RSS/WECO-MON',
        'http://www.la-croix.com/RSS/WECO-SOC',
        'http://www.la-croix.com/RSS/WECO-ENT',
        'http://www.la-croix.com/RSS/WECO-MED',
        'http://www.la-croix.com/RSS/WECO-SOL',
        'http://www.la-croix.com/RSS/WECO-CAH',
        'http://www.la-croix.com/RSS/WREL-LAI',
        'http://www.la-croix.com/RSS/WREL-CAT',
        'http://www.la-croix.com/RSS/WREL-ISL',
        'http://www.la-croix.com/RSS/WREL-JUD',
        'http://www.la-croix.com/RSS/WREL-PRO',
        'http://www.la-croix.com/RSS/WREL-ORT',
        'http://www.la-croix.com/RSS/WREL-BOU',
        'http://www.la-croix.com/RSS/WCLT-CINE',
        'http://www.la-croix.com/RSS/WCLT-MUS',
        'http://www.la-croix.com/RSS/WCLT-TV',
        'http://www.la-croix.com/RSS/WCLT-AV',
        'http://www.la-croix.com/RSS/WCLT-THE',
        'http://www.la-croix.com/RSS/WCLT-EXP',
        'http://www.la-croix.com/RSS/WCLT-CAH',
        'http://www.la-croix.com/RSS/WFAM-EDU',
        'http://www.la-croix.com/RSS/WFAM-COUPL',
        'http://www.la-croix.com/RSS/WFAM-ENF',
        'http://www.la-croix.com/RSS/WFAM-LOI',
        'http://www.la-croix.com/RSS/WFAM-CAH',
        'http://www.la-croix.com/RSS/WSCI-SAN',
        'http://www.la-croix.com/RSS/WSCI-SCI',
        'http://www.la-croix.com/RSS/WSCI-MED',
        'http://www.la-croix.com/RSS/WSCI-ENV',
        'http://www.la-croix.com/RSS/WSCI-NUM',
        'http://www.la-croix.com/RSS/WSCI-ETI',
        'http://www.la-croix.com/RSS/WSCI-CAH',
        'http://www.la-croix.com/RSS/WDEB-CHRO',
        'http://www.la-croix.com/RSS/WDEB-EDI',
        'http://www.la-croix.com/RSS/WDEB-COURRIER',
        'http://www.la-croix.com/RSS/WDEB-FORUM',
        'http://www.la-croix.com/RSS/WSPO'
    ]
    CATEGORIES_ASSOCIATION = {
        'Monde': Category.INTERNATIONAL,
        'Débats': Category.DEBATS_ET_OPINIONS,
        'Religion': Category.RELIGION,
        'France': Category.FRANCE,
        'Culture': Category.CULTURE,
        'Economie': Category.ECONOMIE,
        'Sciences et éthique': Category.SCIENCE_ET_ENVIRONNEMENT,
        'Sport': Category.SPORT,
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
        if article.authors:
            authors = article.authors
        else:
            try:
                authors = article.meta_data.get('article').get('author')
                authors = authors.replace(' et ', ', ').split(', ')
            except AttributeError:
                authors = ['Indéfini']
        return authors

    @staticmethod
    def get_category(article: np.Article) -> str:
        """Get an article's category or section."""
        try:
            category = article.meta_data.get('article').get('section')
            if category is None:
                category = 'Indéfini'
        except AttributeError:
            category = 'Indéfini'
        return category

    # No information in the metadata about the article access (free or premium)!
    # Need to parse the HTML with BeautifulSoup for example.
