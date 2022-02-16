"""
Le Figaro Collector.
"""

import typing
import logging
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.scraping_and_extraction.twitter_source as gn_twitter

logger = logging.getLogger('genderednews.collector.lefigaro')
logger_debug = logging.getLogger('genderednews_debug.collector.lefigaro')


class LeFigaro(gn_collector.Collector):
    """
    A Collector for Le Figaro news website (https://www.lefigaro.fr).
    """

    NAME = 'Le Figaro'
    TWITTER_USER = 'Le_Figaro'
    PREFIX_URLS = ['https://www.lefigaro.fr/']
    BANNED_URLS = []
    RSS_FEED_URLS = [
        'http://www.lefigaro.fr/rss/figaro_actualites.xml',
        'http://www.lefigaro.fr/rss/figaro_flash-actu.xml',
        'http://www.lefigaro.fr/rss/figaro_politique.xml',
        'http://www.lefigaro.fr/rss/figaro_politique_le-scan.xml',
        'http://www.lefigaro.fr/rss/figaro_elections.xml',
        'http://www.lefigaro.fr/rss/figaro_international.xml',
        'http://www.lefigaro.fr/rss/figaro_actualite-france.xml',
        'http://www.lefigaro.fr/rss/figaro_vox.xml',
        'http://www.lefigaro.fr/rss/figaro_sciences.xml',
        'http://www.lefigaro.fr/rss/figaro_sante.xml',
        'http://www.lefigaro.fr/rss/figaro_lefigaromagazine.xml',
        # 'http://www.lefigaro.fr/rss/figaro_videos.xml',
        'http://www.lefigaro.fr/rss/figaro_photos.xml',
        'http://www.lefigaro.fr/rss/figaro_economie.xml',
        'http://www.lefigaro.fr/rss/figaro_economie_le-scan-eco.xml',
        'http://www.lefigaro.fr/rss/figaro_flash-eco.xml',
        'http://www.lefigaro.fr/rss/figaro_societes.xml',
        'http://www.lefigaro.fr/rss/figaro_medias.xml',
        'http://www.lefigaro.fr/rss/figaro_secteur_high-tech.xml',
        # 'http://www.lefigaro.fr/rss/figaro_immobilier.xml',
        # 'http://www.lefigaro.fr/rss/figaro_bourse.xml',
        'http://www.lefigaro.fr/rss/figaro_assurance.xml',
        'http://www.lefigaro.fr/rss/figaro_retraite.xml',
        'http://www.lefigaro.fr/rss/figaro_placement.xml',
        'http://www.lefigaro.fr/rss/figaro_impots.xml',
        'http://www.lefigaro.fr/rss/figaro_conso.xml',
        'http://www.lefigaro.fr/rss/figaro_emploi.xml',
        'http://www.lefigaro.fr/rss/figaro_finances-perso.xml',
        'http://www.lefigaro.fr/rss/figaro_management.xml',
        'http://www.lefigaro.fr/rss/figaro_culture.xml',
        'http://www.lefigaro.fr/rss/figaro_cinema.xml',
        'http://www.lefigaro.fr/rss/figaro_musique.xml',
        'http://www.lefigaro.fr/rss/figaro_livres.xml',
        'http://www.lefigaro.fr/rss/figaro_theatre.xml',
        'http://www.lefigaro.fr/rss/figaro_arts-expositions.xml',
        'http://www.lefigaro.fr/rss/figaro_histoire.xml',
        'http://www.lefigaro.fr/rss/figaro_lifestyle.xml',
        'http://www.lefigaro.fr/rss/figaro_automobile.xml',
        'http://www.lefigaro.fr/rss/figaro_gastronomie.xml',
        # 'http://www.lefigaro.fr/rss/figaro_sortir-paris.xml',
        # 'http://www.lefigaro.fr/rss/figaro_vins.xml',
        'http://www.lefigaro.fr/rss/figaro_voyages.xml',
        'http://www.lefigaro.fr/rss/figaro_jardin.xml',
        'http://www.lefigaro.fr/rss/figaro_style.xml',
        # 'http://www.lefigaro.fr/rss/figaro_horlogerie.xml',
        'http://www.lefigaro.fr/rss/figaro_industrie-mode.xml',
        'http://www.lefigaro.fr/rss/figaro_mode-homme.xml',
        # 'http://www.lefigaro.fr/rss/figaro_le-scan-sport.xml',
    ]
    CATEGORIES_ASSOCIATION = {
        'Société': Category.SOCIETE,
        'Sciences & Environnement': Category.SCIENCE_ET_ENVIRONNEMENT,
        'Entreprises': Category.ECONOMIE,
        'International': Category.INTERNATIONAL,
        'Politique': Category.POLITIQUE,
        'Cinéma': Category.CULTURE,
        'Vox Société': Category.SOCIETE,
        'Tech & Web': Category.NUMERIQUE,
        'Livres': Category.CULTURE,
        'Actu people': Category.PEOPLE,
        'Culture': Category.CULTURE,
        'Musique': Category.CULTURE,
        'Vox Monde': Category.INTERNATIONAL,
        'Vox Politique': Category.POLITIQUE,
        'Sports': Category.SPORT,
        'Indéfini': Category.INDEFINI,
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
        if article.meta_data.get('article') and article.meta_data.get('article').get('author'):
            authors = [article.meta_data.get('article').get('author')]
        else:
            logger_debug.warning(f'No authors found for {article.url}.')
            authors = ['Indéfini']
        return authors

    @staticmethod
    def get_category(article: np.Article) -> str:
        """Get an article's category or section."""
        if article.meta_data.get('article') and article.meta_data.get('article').get('section'):
            category = article.meta_data.get('article').get('section')
            if category is None:
                category = 'Indéfini'
        else:
            logger_debug.warning(f'No category found for {article.url}.')
            category = 'Indéfini'
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
