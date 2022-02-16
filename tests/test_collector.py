"""
Unit tests for Collector module.
"""

import datetime as dt
import gn_modules.scraping_and_extraction.collectors.le_monde as gn_le_monde


# Example article date and url
DATE = dt.datetime(2021, 3, 10)
URL = "https://www.lemonde.fr/international/article/2021/03/10/relations-entre-le-royaume-uni-et-la-chine-de-l-age-d-or-au-refroidissement_6072577_3210.html"

# Le Monde Collector
LE_MONDE = gn_le_monde.LeMonde(scraping_mode='rss')


class TestScrapeAndExtractArticlesFromDayTo():
    """Test scrape_and_extract_articles_from_day_to function"""

    @classmethod
    def setup_class(cls):
        """Set up from_date, to_date and articles between these dates."""
        cls.from_date = dt.datetime.now() - dt.timedelta(days=3)
        cls.to_date = dt.datetime.now() - dt.timedelta(days=1)
        cls.articles = LE_MONDE.scrape_and_extract_articles_from_day_to(
            cls.from_date, cls.to_date)

    def test_articles_created(self):
        """Check if the list of articles is not empty"""
        for article in self.articles:
            assert article

    def test_scrape_extract_from_to(self):
        """Check if the article date is correct"""
        for article in self.articles:
            assert self.from_date.date() <= article.date.date() <= self.to_date.date()


class TestScrapAndExtractArticlesOfYesterday():
    """Test scrape_and_extreact_articles_of_yesterday function"""

    @classmethod
    def setup_class(cls):
        """Set up yesterday and articles of yesterday"""
        cls.yesterday = dt.datetime.now() - dt.timedelta(days=1)
        cls.articles = LE_MONDE.scrape_and_extract_articles_of_yesterday()

    def test_articles_created(self):
        """Check if the list of articles is empty"""
        for article in self.articles:
            assert article

    def test_scrape_extract_yesterday(self):
        """Check if the article date is yesterday"""
        for article in self.articles:
            assert article.date.date() == self.yesterday.date()


class TestCreateArticleFromLink():
    """Test create_article_from_link function"""

    @classmethod
    def setup_class(cls):
        """Get the article from the given URL"""
        cls.article = LE_MONDE.create_article_from_link(URL, DATE)

    def test_article_created(self):
        """Check if article created is not empty"""
        assert self.article

    def test_article_created_is_valid(self):
        """Check if the article created is valid"""
        self.article.check_valid()
