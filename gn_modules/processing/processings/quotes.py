"""
This a template that can be copy/pasted to create a new processing step.
"""

import typing

import gn_modules.processing.processing as gn_processing
import gn_modules.processing.processings.quote_extractor.french_pipeline.quote_extractor_fr_V2 as quote_extractor
import gn_modules.processing.processings.quote_extractor.french_pipeline.gender_stats as gender_stats

class Quotes(gn_processing.Processing):
    """
    The <class name> compute the <indicators> indicators.
    ...
    """

    QUOTES = 'quotes'
    WOMEN_COUNT = 'women_count'
    MEN_COUNT = 'men_count'
    UNKNOWN_COUNT = 'unknown_count'

    def __init__(self) -> None:
        self.name = 'quotes'
        self.indicators = [self.QUOTES, self.WOMEN_COUNT,
                           self.MEN_COUNT, self.UNKNOWN_COUNT]
        #self.jobs_df = self.__get_jobs_df()

    # Depending on the level at which you want to implement the processing step (either batch articles or single article text) you can:
    # - Overwrite process_text_one_article, a method that given an article text return a dictionary of indicators
    # - Overwrite process, a method that given an Article list return a list of dictionaries of indicators

    def process_text_one_article(self, txt: str) -> typing.Dict:
        """
        ...
        """
        # Compute your indicators here
        quotes = quote_extractor.quote_extractor_pipeline(txt)  # list of quotes
        stats = gender_stats.get_stats(quotes) #idk we'll see
        women_count = stats["women_speakers"]
        men_count = stats["men_speakers"]
        unknown_count = stats["unknown_speakers"]

        return {
            self.QUOTES: quotes,
            self.WOMEN_COUNT: women_count,
            self.MEN_COUNT: men_count,
            self.UNKNOWN_COUNT: unknown_count
        }
