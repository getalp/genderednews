"""
Unit tests for db_helper module.
"""


import copy
import datetime as dt
import pymongo as pm

import gn_modules.article as gn_article
from gn_modules.category import Category
import gn_modules.db_helper as gn_db_helper
import gn_modules.processing.processings.masculinity_rate_and_names as masculinity

MASCULINITY = masculinity.MasculinityRateAndNames()

PROCESSINGS_1 = {MASCULINITY.name: {
    'updated_at': dt.datetime(2021, 6, 30, 00, 00, 00),
    'indicators': {
        'key1': 'value1'
    }
}}

PROCESSINGS_2 = {MASCULINITY.name: {
    'updated_at': dt.datetime(2021, 6, 27, 00, 00, 00),
    'indicators': {
        'key2': 'value2'
    }
}}

ARTICLE_1_DICT = {
    'link': "https://www.lemonde.fr/planete/article/2021/02/23/la-justice-saisie-pour-faire-barrage-au-retour-des-neonicotinoides_6070945_3244.html",
    'title': "Combien les règles coûtent-elles dans la vie d’une femme ?",
    'date': dt.datetime(2019, 2, 7, 00, 00, 00),
    'source_name': 'Le Monde',
    'text': None,
    'authors': ['Anne-Aël Durand', 'Gary Dagorn'],
    'category': Category.CULTURE.to_string(),
    'word_count': 1920,
    'processings': {},
    'hero_image': 'image.png',
    'access': gn_article.Article.Access.GRATUIT.to_string(),
}

ARTICLE_2_DICT = {
    'link': "https://www.lefigaro.fr/secteur/high-tech/le-programme-a-l-origine-du-web-vendu-5-4-millions-de-dollars-20210701",
    'title': "title",
    'date': dt.datetime(2021, 2, 7, 00, 00, 00),
    'source_name': 'Le Figaro',
    'text': None,
    'authors': ['author1', 'author2'],
    'category': Category.NUMERIQUE.to_string(),
    'word_count': 1921,
    'processings': {},
    'hero_image': 'image.png',
    'access': gn_article.Article.Access.PAYANT.to_string(),
}

YESTERDAY = dt.datetime.now() - dt.timedelta(days=1)

ARTICLE_3_DICT = {
    'link': "link",
    'title': "title",
    'date': YESTERDAY,
    'source_name': 'source_name',
    'text': None,
    'authors': ['author1', 'author2'],
    'category': "category",
    'word_count': 1921,
    'processings': {},
    'hero_image': 'image.png',
    'access': gn_article.Article.Access.PAYANT.to_string(),
}

DB_HELPER = gn_db_helper.DbHelper(mode="test")


class TestInit:
    """Test __init__ method."""

    def test_mongo_connection(self):
        """Check if the connection with the mongodb can be established"""

        try:
            # Replace 'mongo' by 'localhost' if you test locally
            client = pm.MongoClient("mongo", 27017)
            client.server_info()
        except pm.errors.ServerSelectionTimeoutError:
            assert False


class TestInsertOrUpdateArticle:
    """Test insert_or_update_article methods"""

    def setup_method(self):
        """Create articles that can be edited"""
        self.article_test1 = gn_article.Article(copy.deepcopy(ARTICLE_1_DICT))
        self.article_test2 = gn_article.Article(copy.deepcopy(ARTICLE_2_DICT))
        self.articles = []
        self.articles.append(self.article_test1)
        self.articles.append(self.article_test2)

    def test_insert_article(self):
        """Check if an article can be added in the database"""

        DB_HELPER.insert_or_update_article(self.article_test1)
        article_test1 = self.article_test1.to_filtered_dict()
        res = DB_HELPER.articles_collection.find_one(article_test1)
        assert res

    def test_update_article(self):
        """Check if the article is updated in the database"""

        self.article_test1.add_processing(
            MASCULINITY.name, {'key1': 'value1'}, dt.datetime(2021, 6, 30, 00, 00, 00))
        DB_HELPER.insert_or_update_article(self.article_test1)
        article_test1 = self.article_test1.to_filtered_dict()
        res = DB_HELPER.articles_collection.find_one(article_test1)
        assert res['processings'] == PROCESSINGS_1

    def test_insert_or_update_articles(self):
        """Check if the articles is inserted or updated in the database"""

        DB_HELPER.insert_or_update_articles(self.articles)
        for article in self.articles:
            article = article.to_filtered_dict()
            res = DB_HELPER.articles_collection.find_one(article)
            assert res

    def teardown_method(self):
        """Reset the database"""

        DB_HELPER.articles_collection.delete_many({})


class TestUpdateArticle:
    """Test update_article methods"""

    def setup_method(self):
        """Create articles in the database"""

        self.article_test1 = gn_article.Article(copy.deepcopy(ARTICLE_1_DICT))
        self.article_test2 = gn_article.Article(copy.deepcopy(ARTICLE_2_DICT))
        self.articles = []
        self.articles.append(self.article_test1)
        self.articles.append(self.article_test2)

        DB_HELPER.insert_or_update_articles(self.articles)

    def test_update_article(self):
        """Check if the article is updated in the database"""

        self.article_test1.add_processing(
            MASCULINITY.name, {'key1': 'value1'}, dt.datetime(2021, 6, 30, 00, 00, 00))
        DB_HELPER.update_article(self.article_test1)
        article_test1 = self.article_test1.to_filtered_dict()
        res = DB_HELPER.articles_collection.find_one(article_test1)
        assert res['processings'] == PROCESSINGS_1

    def test_update_articles(self):
        """Check if articles are updated in the database"""

        self.article_test1.add_processing(
            MASCULINITY.name, {'key2': 'value2'}, dt.datetime(2021, 6, 27, 00, 00, 00))
        self.article_test2.add_processing(
            MASCULINITY.name, {'key1': 'value1'}, dt.datetime(2021, 6, 30, 00, 00, 00))
        DB_HELPER.update_articles(self.articles)
        article_test1 = self.article_test1.to_filtered_dict()
        res = DB_HELPER.articles_collection.find_one(article_test1)
        assert res['processings'] == PROCESSINGS_2
        article_test2 = self.article_test2.to_filtered_dict()
        res = DB_HELPER.articles_collection.find_one(article_test2)
        assert res['processings'] == PROCESSINGS_1

    def teardown_method(self):
        """Reset the database"""

        DB_HELPER.articles_collection.delete_many({})


class TestDeleteArticle:
    """Test delete_article method"""

    def setup_method(self):
        """Create an article in the database"""

        self.article_test = gn_article.Article(copy.deepcopy(ARTICLE_1_DICT))
        DB_HELPER.insert_or_update_article(self.article_test)

    def test_delete_article(self):
        """Check if the article is deleted in the database"""

        DB_HELPER.delete_article(self.article_test)
        article_test = self.article_test.to_filtered_dict()
        res = DB_HELPER.articles_collection.find_one(article_test)
        assert res is None

    def teardown_method(self):
        """Reset the database"""

        DB_HELPER.articles_collection.delete_many({})


class TestGetArticles:
    """Test get_articles methods"""

    def setup_method(self):
        """Create articles in the database"""

        self.article_test1 = gn_article.Article(copy.deepcopy(ARTICLE_1_DICT))
        self.article_test2 = gn_article.Article(copy.deepcopy(ARTICLE_2_DICT))
        self.article_test3 = gn_article.Article(copy.deepcopy(ARTICLE_3_DICT))
        DB_HELPER.insert_or_update_article(self.article_test1)
        DB_HELPER.insert_or_update_article(self.article_test2)
        DB_HELPER.insert_or_update_article(self.article_test3)

    def test_get_article(self):
        """Check if we can get an article"""
        res = DB_HELPER.get_article(self.article_test1)
        assert res

    def test_get_articles_never_processed(self):
        """Check if we can get never processed articles"""

        articles_never_processed = DB_HELPER.get_articles_never_processed(10)
        assert articles_never_processed
        for article in articles_never_processed:
            assert article.processings == {}

    def test_get_yesterday_articles_missing_process(self):
        """Check if we can get yesterday article with given missing process"""

        yesterday_articles_missing_process = DB_HELPER.get_yesterday_articles_missing_process(
            MASCULINITY)
        assert len(yesterday_articles_missing_process) == 1

    def test_get_articles_missing_process(self):
        """Check if we can get article with given missing process"""

        articles_missing_process = DB_HELPER.get_articles_missing_process(
            MASCULINITY, 10)
        assert len(articles_missing_process) == 3

    def test_get_articles_process_updated_before(self):
        """Check if we can get articles which the given processing has been updated before the given date"""

        self.article_test1.add_processing(
            MASCULINITY.name, {'key2': 'value2'}, dt.datetime(2021, 6, 27, 00, 00, 00))
        DB_HELPER.update_article(self.article_test1)
        date = dt.datetime(2021, 6, 28, 00, 00, 00)
        articles_process_updated_before = DB_HELPER.get_articles_process_updated_before(
            MASCULINITY, date, 10)
        assert len(articles_process_updated_before) == 3

        self.article_test2.add_processing(
            MASCULINITY.name, {'key1': 'value1'}, dt.datetime(2021, 6, 30, 00, 00, 00))
        DB_HELPER.update_article(self.article_test2)
        articles_process_updated_before = DB_HELPER.get_articles_process_updated_before(
            MASCULINITY, date, 10)
        assert len(articles_process_updated_before) == 2

    def teardown_method(self):
        """Reset the database"""

        DB_HELPER.articles_collection.delete_many({})


class TestSanityCheck:
    """Test sanity_check method"""

    def setup_method(self):
        """Create articles in the database"""

        self.article_test1 = gn_article.Article(copy.deepcopy(ARTICLE_1_DICT))
        self.article_test2 = gn_article.Article(copy.deepcopy(ARTICLE_2_DICT))
        DB_HELPER.insert_or_update_article(self.article_test1)
        DB_HELPER.insert_or_update_article(self.article_test2)

    def test_sanity_check(self):
        """Check if the sanitycheck method works"""

        DB_HELPER.sanity_check(fix=True)

    def teardown_method(self):
        """Reset the database"""

        DB_HELPER.articles_collection.delete_many({})


class TestReExtractAndProcess:
    """Test re_extract_and_process_everything method"""

    def setup_method(self):
        """Create articles in the database"""

        self.article_test1 = gn_article.Article(copy.deepcopy(ARTICLE_1_DICT))
        self.article_test2 = gn_article.Article(copy.deepcopy(ARTICLE_2_DICT))
        DB_HELPER.insert_or_update_article(self.article_test1)
        DB_HELPER.insert_or_update_article(self.article_test2)

    def test_re_extract_and_process_everything(self):
        """Check if we can re-extract and process every articles"""

        DB_HELPER.re_extract_and_process_everything()

    def teardown_method(self):
        """Reset the database"""

        DB_HELPER.articles_collection.delete_many({})
