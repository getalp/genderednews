"""
Libération Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class Liberation(gn_collector.Collector):
    """
    A Collector for Libération news website (https://www.liberation.fr).
    """

    NAME = 'Libération'
    TWITTER_USER = 'libe'
    PREFIX_URLS = ['https://www.liberation.fr/']
    BANNED_URLS = ['https://www.liberation.fr/dossier/',
                   'https://www.liberation.fr/auteur/',
                   'https://www.liberation.fr/tags/',
                   'https://www.liberation.fr/checknews-questions/']
    RSS_FEED_URLS = [
        # 'https://www.liberation.fr/arc/outboundfeeds/rss/',
        'https://www.liberation.fr/arc/outboundfeeds/rss/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/culture/cinema/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/culture/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/societe/education/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/environnement/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/societe/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/economie/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/idees-et-debats/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/idees-et-debats/opinions/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/tags_slug/lgbt/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/culture/livres/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/culture/photographie/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/international/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/tags_slug/poesie/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/politique/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/portraits/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/societe/?outputType=xml',
        'https://www.liberation.fr/arc/outboundfeeds/rss/category/sports/?outputType=xml',
    ]

    CATEGORIES_ASSOCIATION = {
        "Santé": Category.SANTE,
        "Europe": Category.INTERNATIONAL,
        "Société": Category.SOCIETE,
        "Politique": Category.POLITIQUE,
        "International": Category.INTERNATIONAL,
        "Asie Pacifique": Category.INTERNATIONAL,
        "Droits des femmes": Category.SOCIETE,
        "Gastronomie": Category.CULTURE,
        "Afrique": Category.INTERNATIONAL,
        "Amérique": Category.INTERNATIONAL,
        "Musique": Category.CULTURE,
        "Cinéma": Category.CULTURE,
        "Education": Category.EDUCATION,
        "Livres": Category.CULTURE,
        "Economie": Category.ECONOMIE,
        "Sports": Category.SPORT,
        "Culture": Category.CULTURE,
        "Moyen-Orient": Category.INTERNATIONAL,
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
        authors = article.meta_data.get('article').get('author')
        if not isinstance(authors, str):
            authors = authors.get('identifier')
        return authors

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
    def get_access(article: np.Article) -> Article.Access:
        """Get an article's access level (free or premium)."""
        try:
            premium = article.meta_data.get('article').get('premium')
            if premium == 'false':
                premium = Article.Access.GRATUIT
            elif premium == 'true':
                premium = Article.Access.PAYANT
            else:
                premium = Article.Access.INDEFINI
        except AttributeError:
            premium = Article.Access.INDEFINI
        return premium
