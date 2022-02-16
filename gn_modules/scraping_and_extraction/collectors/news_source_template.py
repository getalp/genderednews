"""
This a template that can be copy/pasted to create a new news source.
<Class Name> Collector.
"""

import typing
import newspaper as np

from gn_modules.article import Article
from gn_modules.category import Category
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.rss_source as gn_rss


class NewsSourceTemplate(gn_collector.Collector):
    """
    A Collector for <source name> news website (<source website url>).
    """

    NAME = '<source name>'
    RSS_FEED_URLS = [
        'a list of',
        'the news source',
        'rss links'
    ]
    CATEGORIES_ASSOCIATION = {
        'category name in this source metadata articles': Category.FRANCE,
        'category name in this source metadata articles': Category.INTERNATIONAL ,
        'category name in this source metadata articles': Category.CULTURE ,
        #...
    }

    def __init__(self) -> None:
        super().__init__()
        self.source = gn_rss.RssSource(self.RSS_FEED_URLS, self.NAME)

    # Only if needed (when the default implementation doesn't work for this source), the methods below can be re-implemented.
    # Each method take a np.Article as an argument, see https://newspaper.readthedocs.io/en/latest/ for more information on this type.

    # def get_title(article: np.Article) -> str:
    # def get_text(article: np.Article) -> str:
    # def get_authors(article: np.Article) -> typing.List[str]:
    # def get_category(article: np.Article) -> str:
    # def get_word_count(article: np.Article) -> int:
    # def get_keywords(article: np.Article) -> typing.List[str]:
    # def get_hero_image(article: np.Article) -> str:
    # def get_metadata(article: np.Article) -> typing.Dict:
    # def get_access(article: np.Article) -> Article.Access:
