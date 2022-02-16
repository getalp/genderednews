"""
LeMonde Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter


class LeMonde(gn_collector.Collector):
    """
    A Collector for Le Monde news website (https://www.lemonde.fr).
    """

    NAME = 'Le Monde'
    TWITTER_USER = 'lemondefr'
    PREFIX_URLS = ['https://www.lemonde.fr/']
    BANNED_URLS = ['https://www.lemonde.fr/blog/',
                   'https://www.lemonde.fr/televisions-radio/',
                   'https://www.lemonde.fr/fragments-de-france/',
                   'https://www.lemonde.fr/enquetes-video/',
                   'https://www.lemonde.fr/podcasts/',
                   'https://www.lemonde.fr/facebook-files/']
    RSS_FEED_URLS = [
        'https://www.lemonde.fr/actualite-en-continu/rss_full.xml',
        'https://www.lemonde.fr/international/rss_full.xml',
        'https://www.lemonde.fr/politique/rss_full.xml',
        'https://www.lemonde.fr/societe/rss_full.xml',
        'https://www.lemonde.fr/economie/rss_full.xml',
        'https://www.lemonde.fr/les-decodeurs/rss_full.xml',
        'https://www.lemonde.fr/resultats-elections/rss_full.xml',
        'https://www.lemonde.fr/sport/rss_full.xml',
        'https://www.lemonde.fr/planete/rss_full.xml',
        'https://www.lemonde.fr/sciences/rss_full.xml',
        'https://www.lemonde.fr/campus/rss_full.xml',
        'https://www.lemonde.fr/afrique/rss_full.xml',
        'https://www.lemonde.fr/pixels/rss_full.xml',
        'https://www.lemonde.fr/actualite-medias/rss_full.xml',
        'https://www.lemonde.fr/sante/rss_full.xml',
        'https://www.lemonde.fr/big-browser/rss_full.xml',
        'https://www.lemonde.fr/disparitions/rss_full.xml',
        'https://www.lemonde.fr/education/rss_full.xml',
        'https://www.lemonde.fr/argent/rss_full.xml',
        'https://www.lemonde.fr/emploi/rss_full.xml',
        'https://www.lemonde.fr/archives-du-monde/rss_full.xml',
        'https://www.lemonde.fr/le-monde-et-vous/rss_full.xml',
        'https://www.lemonde.fr/idees/rss_full.xml',
        'https://www.lemonde.fr/m-perso/rss_full.xml',
        'https://www.lemonde.fr/m-styles/rss_full.xml',
        'https://www.lemonde.fr/les-recettes-du-monde/rss_full.xml',
        'https://www.lemonde.fr/culture/rss_full.xml',
        'https://www.lemonde.fr/livres/rss_full.xml',
        'https://www.lemonde.fr/m-le-mag/rss_full.xml'
    ]

    CATEGORIES_ASSOCIATION = {
        "Opinions": Category.DEBATS_ET_OPINIONS,
        "Économie": Category.ECONOMIE,
        "Afrique": Category.INTERNATIONAL,
        "Société": Category.SOCIETE,
        "Politique": Category.POLITIQUE,
        "Sport": Category.SPORT,
        "Culture": Category.CULTURE,
        "International": Category.INTERNATIONAL,
        "Livres": Category.CULTURE,
        "Pixels": Category.NUMERIQUE,
        "Disparitions": Category.FAIT_DIVERS,
        "Sciences": Category.SCIENCE_ET_ENVIRONNEMENT,
        "Éducation": Category.EDUCATION,
        "Football": Category.SPORT,
        "Santé": Category.SANTE,
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
        authors = article.meta_data.get('og').get('article').get('author')
        if authors:
            authors = authors.replace(' et ', ', ').split(', ')
        else:
            if article.authors:
                authors = article.authors
            else:
                authors = ['Indéfini']
        return authors

    @staticmethod
    def get_access(article: np.Article) -> Article.Access:
        """Get an article's access level (free or premium)."""
        try:
            content_tier = article.meta_data.get(
                'og').get('article').get('content_tier')
            if content_tier == 'free':
                content_tier = Article.Access.GRATUIT
            elif content_tier == 'locked':
                content_tier = Article.Access.PAYANT
            else:
                content_tier = Article.Access.INDEFINI
        except AttributeError:
            content_tier = Article.Access.INDEFINI
        return content_tier
