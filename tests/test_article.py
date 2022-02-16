"""
Unit tests for article module.
"""

import datetime as dt
import copy
import faker

import gn_modules.article as gn_article
from gn_modules.category import Category

PROCESSINGS = {'process': {
    'updated_at': 'date',
    'indicators': {
        'key': 'value'
    }
}}

ARTICLE_DICT = {
    'link': "https://www.lemonde.fr/planete/article/2021/02/23/la-justice-saisie-pour-faire-barrage-au-retour-des-neonicotinoides_6070945_3244.html",
    'title': "Combien les règles coûtent-elles dans la vie d’une femme ?",
    'date': dt.datetime(2019, 2, 7, 00, 00, 00),
    'source_name': 'Le Monde',
    'text': None,
    'authors': ['Anne-Aël Durand', 'Gary Dagorn'],
    'category': Category.CULTURE,
    'word_count': 1920,
    'processings': PROCESSINGS,
    'hero_image': 'image.png',
    'access': gn_article.Article.Access.GRATUIT.to_string(),
}

ARTICLE = gn_article.Article(copy.deepcopy(ARTICLE_DICT))


class TestInit:
    """Test __init__ method."""

    def test_invalid_article(self):
        """Check if an exception is raised for an invalid article."""
        try:
            gn_article.Article({
                'link': None,
                'title': None,
                'date': dt.datetime.now() + dt.timedelta(days=1),
                'source_name': None,
                'text': None,
                'authors': None,
                'category': None,
                'word_count': 0,
                'indicators': None,
                'access': None,
            })
        except (AssertionError, ValueError):
            pass
            # ValueError (because None is not a valid Access value)
            # or AssertionError should be raised
        else:
            assert False

    def test_valid_article(self):
        """Check if no assert has failed for a valid article."""
        ARTICLE.check_valid()


class TestToRawDict:
    """Test to_raw_dict method."""

    def test_to_raw_dict(self):
        """Check if an article is correctly formatted in raw dict."""
        assert ARTICLE.to_raw_dict() == ARTICLE_DICT


class TestToFilteredDict:
    """Test to_filtered_dict method."""

    def test_to_filtered_dict(self):
        """Check if an article is correctly formatted in filtered dict."""
        filtered_dict = ARTICLE.to_raw_dict()
        filtered_dict.pop('text', None)
        assert ARTICLE.to_filtered_dict() == filtered_dict


class TestAddProccessing:
    """Test add_processing method."""

    def setup_method(self):
        """Create a test article that can be edited."""
        self.article_test = gn_article.Article(copy.deepcopy(ARTICLE_DICT))

    def test_add_processing_and_indicator(self):
        """Check if a new indicator can be added."""
        self.article_test.add_processing(
            'process_add', {'key_add': 'value_add'}, 'date_add')
        assert self.article_test.processings
        assert self.article_test.processings == {
            'process': {
                'updated_at': 'date',
                'indicators': {
                    'key': 'value',
                }
            },
            'process_add': {
                'updated_at': 'date_add',
                'indicators': {
                    'key_add': 'value_add'
                }
            }
        }

    def test_add_processing(self):
        """Check if a new processing can be added."""
        self.article_test.add_processing(
            'process', {'key_add': 'value_add'}, 'date_add')
        assert self.article_test.processings
        assert self.article_test.processings == {
            'process': {
                'updated_at': 'date_add',
                'indicators': {
                    'key_add': 'value_add',
                }
            }
        }

    def test_update_processing(self):
        """Check if an existing processing can be updated."""
        self.article_test.add_processing(
            'process', {'key': 'value_update'}, 'date_update')
        assert self.article_test.processings
        assert self.article_test.processings == {
            'process': {
                'updated_at': 'date_update',
                'indicators': {
                    'key': 'value_update'
                }
            }
        }


class TestGetText:
    """Test get_text method."""

    def test_simple(self):
        """Test if get_text returns something."""
        assert ARTICLE.get_text()

    def test_cleared_text(self):
        """Test if get_text returns something even if the text has been cleared."""
        ARTICLE.clear_text()
        assert ARTICLE.get_text()


class TestCreateRandomArticle:
    """Test create_random_article method."""

    @ classmethod
    def setup_class(cls):
        """Setup faker."""
        cls.fake = faker.Factory.create('fr_FR')

    def test_is_random_article_valid(self):
        """Check if a randomly generated article is valid."""
        fake_article = gn_article.Article.create_random_article(self.fake)
        fake_article.check_valid()
