"""
Unit tests for Processing
"""

import gn_modules.processing.processings.masculinity_rate_and_names as masculinity
import gn_modules.processing.processings.homogenous_category as homogenous_category
import gn_modules.scraping_and_extraction.collectors.le_monde as gn_le_monde
import gn_modules.processing.processings.quotes as quotes


MASCULINITY = masculinity.MasculinityRateAndNames()
HOMOGENOUS_CATEGORY = homogenous_category.HomogenousCategory()
QUOTES = quotes.Quotes()

LE_MONDE = gn_le_monde.LeMonde(scraping_mode='rss')

# Scrape and extract all articles of yesterday of Le Monde
ARTICLES = LE_MONDE.scrape_and_extract_articles_of_yesterday()

# Take an example of text
TEXT = ARTICLES[0].get_text()


class TestProcessTextOneArticle():
    """Test process_text_one_article method."""

    def test_masculinity_result(self):
        """Check if masculinity rate is calculated."""
        res = MASCULINITY.process_text_one_article(TEXT)
        assert res

    def test_quotes_result(self):
        """Check if quotes are extracted and counted"""
        res = QUOTES.process_text_one_article(TEXT)
        assert res


class TestProcess():
    """Test process method."""

    def test_general_process(self):
        """Check if indicators are correct."""
        indicators = [MASCULINITY.process(ARTICLES)]
        for list_articles in indicators:
            for indicator in list_articles:
                assert indicator

    def test_homogenous_category_process(self):
        """Check if indicators are correct."""
        indicators = [HOMOGENOUS_CATEGORY.process(ARTICLES)]
        for list_articles in indicators:
            for indicator in list_articles:
                assert indicator


class TestApplyOn():
    """Test apply_on method."""

    @classmethod
    def setup_class(cls):
        """Set processings of articles to empty."""
        for article in ARTICLES:
            article.processings = {}

    def test_apply_on(self):
        """Check if processings are added to articles"""
        processes = [MASCULINITY.apply_on(ARTICLES)]
        for list_articles in processes:
            for article in list_articles:
                assert article.processings
