"""
Unit tests for RSS_source module.
"""

import datetime as dt

import gn_modules.scraping_and_extraction.rss_source as gn_rss_source


MONDE_ACTUALITE = 'https://www.lemonde.fr/actualite-en-continu/rss_full.xml'
MONDE_INTERNATIONAL = 'https://www.lemonde.fr/international/rss_full.xml'
MONDE_POLITIQUE = 'https://www.lemonde.fr/politique/rss_full.xml'
MONDE_SOCIETE = 'https://www.lemonde.fr/societe/rss_full.xml'
MONDE_ECONOMIE = 'https://www.lemonde.fr/economie/rss_full.xml'
MONDE_SPORT = 'https://www.lemonde.fr/sport/rss_full.xml'
MONDE_PLANETE = 'https://www.lemonde.fr/planete/rss_full.xml'
MONDE_SCIENCES = 'https://www.lemonde.fr/sciences/rss_full.xml'
MONDE_CAMPUS = 'https://www.lemonde.fr/campus/rss_full.xml'
MONDE_AFRIQUE = 'https://www.lemonde.fr/afrique/rss_full.xml'
MONDE_SANTE = 'https://www.lemonde.fr/sante/rss_full.xml'
MONDE_EDUCATION = 'https://www.lemonde.fr/education/rss_full.xml'
MONDE_ARGENT = 'https://www.lemonde.fr/argent/rss_full.xml'
MONDE_EMPLOI = 'https://www.lemonde.fr/emploi/rss_full.xml'
MONDE_CULTURE = 'https://www.lemonde.fr/culture/rss_full.xml'
MONDE_RSS_FEED_LINKS = [MONDE_ACTUALITE,
                        MONDE_INTERNATIONAL,
                        MONDE_POLITIQUE,
                        MONDE_SOCIETE,
                        MONDE_ECONOMIE,
                        MONDE_SPORT,
                        MONDE_PLANETE,
                        MONDE_SCIENCES,
                        MONDE_CAMPUS,
                        MONDE_AFRIQUE,
                        MONDE_SANTE,
                        MONDE_EDUCATION,
                        MONDE_ARGENT,
                        MONDE_EMPLOI,
                        MONDE_CULTURE, ]
MONDE = gn_rss_source.RssSource(MONDE_RSS_FEED_LINKS, 'Le Monde')


class TestScrapeAllXml:
    """Test scrape_all_xml function."""

    @classmethod
    def setup_class(cls):
        """Get all the entries for each RSS feed."""
        cls.monde_entries = MONDE.scrape_all_xml()

    def test_entries_not_empty(self):
        """Check if the list is not empty."""
        for entry in self.monde_entries:
            assert entry

    def test_link_is_string(self):
        """Check if the link is a String."""
        for entry in self.monde_entries:
            assert isinstance(entry['link'], str)

    def test_link_is_non_empty_string(self):
        """Check if the link is a String."""
        for entry in self.monde_entries:
            assert entry['link'] != ''

    def test_date_is_datetime(self):
        """Check if the date is a Datetime."""
        for entry in self.monde_entries:
            assert isinstance(entry['date'], dt.datetime)

    def test_date_in_past(self):
        """Check if the date is in the past."""
        for entry in self.monde_entries:
            assert entry['date'] <= dt.datetime.now()


class TestGetEntriesFromTo:
    """Test get_entries_from_to function."""

    @classmethod
    def setup_class(cls):
        """Set up useful dates."""
        cls.today = dt.datetime.now()
        cls.yesterday = cls.today - dt.timedelta(days=1)
        cls.ereyesterday = cls.today - dt.timedelta(days=2)
        cls.tomorrow = cls.today + dt.timedelta(days=1)
        cls.overmorrow = cls.today + dt.timedelta(days=2)

    def from_loop(self, from_date):
        """Check if all dates are after from_date."""
        entries = MONDE.get_entries_from_to(from_date, from_date)
        for entry in entries:
            assert entry['date'].date() >= from_date.date()

    def test_from(self):
        """Check if the from date is respected."""
        self.from_loop(self.today)
        self.from_loop(self.yesterday)
        self.from_loop(self.ereyesterday)
        self.from_loop(self.tomorrow)
        self.from_loop(self.overmorrow)

    def to_loop(self, to_date):
        """Check if all dates are before to_date."""
        entries = MONDE.get_entries_from_to(to_date, to_date)
        for entry in entries:
            assert entry['date'].date() <= to_date.date()

    def test_to(self):
        """Check if the to date is respected."""
        self.to_loop(self.today)
        self.to_loop(self.yesterday)
        self.to_loop(self.ereyesterday)
        self.to_loop(self.tomorrow)
        self.to_loop(self.overmorrow)

    def test_from_to(self):
        """Check if from and to are respected."""
        from_date = self.yesterday
        to_date = self.ereyesterday
        entries = MONDE.get_entries_from_to(from_date, to_date)
        for entry in entries:
            assert from_date.date() <= entry['date'].date() <= to_date.date()


class TestGetEntriesOfYesterday:
    """Test get_entries_of_yesterday function."""

    def test_yesterday(self):
        """Check if from and to are respected."""
        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        entries = MONDE.get_entries_of_yesterday()
        for entry in entries:
            assert entry['date'].date() == yesterday.date()
