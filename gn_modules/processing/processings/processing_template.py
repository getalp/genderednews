"""
This a template that can be copy/pasted to create a new processing step.
"""

import typing

import gn_modules.processing.processing as gn_processing


class ProcessingTemplate(gn_processing.Processing):
    """
    The <class name> compute the <indicators> indicators.
    ...
    """

    INDICATOR_NAME_1 = 'indicator_name_1'
    INDICATOR_NAME_2 = 'indicator_name_2'

    def __init__(self) -> None:
        self.name = '<processing name>'
        self.indicators = [self.INDICATOR_NAME_1, self.INDICATOR_NAME_2]

    # Depending on the level at which you want to implement the processing step (either batch articles or single article text) you can:
    # - Overwrite process_text_one_article, a method that given an article text return a dictionary of indicators
    # - Overwrite process, a method that given an Article list return a list of dictionaries of indicators

    # def process_text_one_article(self, txt: str) -> typing.Dict:
    #     """
    #     ...
    #     """
    #
    #     # Compute your indicators here
    #     indicator_1_value = # Compute my indicator 1
    #     indicator_2_value = # Compute my indicator 2
    #
    #     return {
    #         self.INDICATOR_NAME_1: indicator_1_value,
    #         self.INDICATOR_NAME_2: indicator_2_value
    #     }

    # def process(self, articles: typing.List[gn_article.Article]) -> typing.List:
    #     """
    #     Given a list of articles, return a list of dictionnaries (in the same order of the articles list).
    #     Each dictionnary corresponds to the processing computed for an article.
    #     Each key in each dictionnary is the name of an indicator of the processing step.
    #     Each value in each dictionnary is the value of the corresponding indicator for the corresponding article.
    #     """
    #
    #     processings_result = # My processing
    #
    #     return processings_result
