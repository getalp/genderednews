"""
Define the Processing class as well as the processings list.
"""

import datetime as dt
import abc
import inspect
import pathlib
import logging
import typing
import time

import gn_modules.article as gn_article

logger = logging.getLogger('genderednews.processing')
logger_debug = logging.getLogger('genderednews_debug.processing')


class Processing(abc.ABC):
    """
    Processing is an abstract class.
    Any processing step for the article must be a subclass of Processing and override the process function.
    The process method will be automatically called in the main program through the apply_on method.
    The apply_on method adds some extra metadata on top of the processing(s) computed by the process.
    """

    def __init__(self) -> None:
        self.name = ''
        self.indicators = []

    def process(self, articles: typing.List[gn_article.Article]) -> typing.List:
        """
        Given a list of articles, return a list of dictionnaries (in the same order of the articles list).
        Each dictionnary corresponds to the processing computed for an article.
        Each key in each dictionnary is the name of an indicator of the processing step.
        Each value in each dictionnary is the value of the corresponding indicator for the corresponding article.
        """
        processings = []
        article: gn_article.Article
        for article in articles:
            time.sleep(1)
            processing = self.process_text_one_article(article.get_text())
            logger_debug.debug(f'Article {article.link} processed...')
            logger_debug.debug(f'... processing: {processing}')
            processings.append(processing)
        return processings

    def process_text_one_article(self, txt: str) -> typing.Dict:
        """
        Take the text of one article as an argument and return a dictionnary of the computed indicators.
        Used in the default version of process.
        When implementing a new process, this method is the bare minimum to implement
        but implementing the more general process method allows for more flexibility and optimization.
        """

        return None

    def apply_on(self, articles: typing.List[gn_article.Article]) -> typing.List[gn_article.Article]:
        """
        Call process on articles to compute the indicator(s) and then
        add the indicator(s) to the articles along with the moment they were computed at (now).
        """

        processing_result_for_articles = self.process(articles)
        now = dt.datetime.now()

        article: gn_article.Article
        for i, article in enumerate(articles):
            article.add_processing(
                self.name, processing_result_for_articles[i], now)

        return articles

    def get_last_update_date(self) -> dt.datetime:
        """Returns the date at which the processing file has been last edited."""

        class_filename = inspect.getfile(self.__class__)
        class_file = pathlib.Path(class_filename)
        return dt.datetime.fromtimestamp(
            class_file.stat().st_mtime)
