"""
Process the raw category into a homogenous category from a limited category list.
"""

import typing
import logging

import gn_modules.processing.processing as gn_processing
import gn_modules.article as gn_article
import gn_modules.scraping_and_extraction.config_collectors as gn_config_collectors
from gn_modules.category import Category

logger = logging.getLogger('genderednews.homogenous_category')
logger_debug = logging.getLogger('genderednews_debug.homogenous_category')


class HomogenousCategory(gn_processing.Processing):
    """
    The <class name> compute the <indicators> indicators.
    ...
    """

    MAIN_CATEGORY = 'main_category'

    def __init__(self) -> None:
        self.name = 'homogenous_categories'
        self.indicators = [self.MAIN_CATEGORY]

    def process(self, articles: typing.List[gn_article.Article]) -> typing.List:
        """
        Given a list of articles, return a list of dictionnaries (in the same order of the articles list).
        Each dictionnary corresponds to the processing computed for an article.
        Each key in each dictionnary is the name of an indicator of the processing step.
        Each value in each dictionnary is the value of the corresponding indicator for the corresponding article.
        """

        processings_result = []

        article: gn_article.Article
        for article in articles:
            category = article.category
            associator = gn_config_collectors.collectors[article.source_name].CATEGORIES_ASSOCIATION
            try:
                homogenous_category = associator[category].to_string()
            except (AttributeError, KeyError):
                homogenous_category = Category.INDEFINI.to_string()

            indicator = {self.MAIN_CATEGORY: homogenous_category}
            logger_debug.debug(f'Article {article.link} processed...')
            logger_debug.debug(f'... processing: {indicator}')

            processings_result.append({self.MAIN_CATEGORY: homogenous_category})

        return processings_result
