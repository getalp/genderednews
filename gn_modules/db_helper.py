"""
The DbHelper class.
"""


import os
import sys
import logging
import typing
import datetime as dt
import pymongo as pm
import sshtunnel

import gn_modules.article as gn_article
import gn_modules.processing.config_processings as gn_config_processing
import gn_modules.processing.processing as gn_processing
import gn_modules.misc as gn_misc
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.config_collectors as gn_config_collector


logger = logging.getLogger('genderednews.db_helper')
logger_debug = logging.getLogger('genderednews_debug.db_helper')


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DbHelper(metaclass=SingletonMeta):
    """
    The DbHelper class include every method needed for the communication to the database:
    - inserting or updating one or multiple articles
    - retrieving articles
    The class also include methods to check the sanity of the database and fix/log errors.
    """

    def __init__(self, mode: str = "localhost") -> None:
        """Connect to the database with arguments from the CLI."""

        # normal __init__
        if mode == "localhost":
            # Check if environment variables have been loaded
            if 'DB_ADDR' not in os.environ:
                raise LookupError(
                    'Environment variables have not been loaded. Run load_dotenv_secure() first.'
                )

            # Establish a connection to the database
            client = pm.MongoClient(os.getenv('DB_ADDR'),
                                    int(os.getenv('DB_PORT')))

            # Get a handle to the database
            self.articles_collection = client[os.getenv(
                'DB_NAME')][os.getenv('DB_ARTICLE_COLLECTION')]

        # __init__ for the unit test
        elif mode == "test":
            # Replace 'mongo' by 'localhost' if you test locally; default db port: 27017
            client = pm.MongoClient("mongo", 27017)
            self.articles_collection = client["test_db"]["test_collection"]

        elif mode == "ssh":
            # Etablish ssh connection
            self.tunnel = sshtunnel.open_tunnel(
                ssh_address_or_host=(
                    os.getenv('GENDEREDNEWS_HOST'), int(os.getenv('GENDEREDNEWS_PORT'))),
                remote_bind_address=(os.getenv('DB_ADDR'),
                                     int(os.getenv('DB_PORT'))),
                ssh_username=os.getenv('ssh_USER'),
                ssh_pkey=os.getenv('ssh_PKEY'),
            )
            self.tunnel.start()

            # Check if environment variables have been loaded
            if 'DB_ADDR' not in os.environ:
                raise LookupError(
                    'Environment variables have not been loaded. Run load_dotenv_secure() first.'
                )

            # Establish a connection to the database
            client = pm.MongoClient(
                os.getenv('DB_ADDR'), self.tunnel.local_bind_port)

            # Get a handle to the database
            self.articles_collection = client[os.getenv(
                'DB_NAME')][os.getenv('DB_ARTICLE_COLLECTION')]

        else:
            print("Database connection failed")
            sys.exit()

    def ssh_stop(self) -> None:
        """Stop ssh connection"""
        self.tunnel.stop()

    # INSERT, UPDATE AND DELETE METHODS

    def insert_or_update_article(self, article: gn_article.Article) -> None:
        """Update an article in the database with an Article object if it already exists.
        Else, insert a new article with an Article object."""

        try:
            article = article.to_filtered_dict()
            res = self.articles_collection.update_one({'link': article['link']}, {
                '$set': article}, upsert=True)

            logger.info(f'article upserted or updated.')
            logger_debug.info(
                f'article upserted or updated.')
        except pm.errors.OperationFailure:
            logger_debug.exception('insert failed, error:')

    def update_article(self, article: gn_article.Article) -> None:
        """Update an article in the database with an Article object.
        If the article does not exist in the database, no article will be updated."""

        try:
            article = article.to_filtered_dict()
            res = self.articles_collection.update_one(
                {'link': article['link']}, {'$set': article})

            logger.info(f'{res.modified_count} article updated.')
            logger_debug.info(f'{res.modified_count} article updated.')
        except pm.errors.OperationFailure:
            logger_debug.exception('update failed, error:')

    def delete_article(self, article: gn_article.Article) -> None:
        """Delete an article in the database with an Article object."""

        try:
            article = article.to_filtered_dict()
            res = self.articles_collection.delete_one(
                {'link': article['link']})

        except pm.errors.OperationFailure:
            logger_debug.exception('delete failed, error:')

    def insert_or_update_articles(self, articles: typing.List[gn_article.Article]) -> None:
        """Update articles in the database with an Article objects if they already exists.
        Else, insert new articles with Article objects."""

        try:
            filtered_articles = [article.to_filtered_dict()
                                 for article in articles]
            updates = [pm.UpdateOne({'link': article['link']}, {'$set': article}, upsert=True)
                       for article in filtered_articles]
            res = self.articles_collection.bulk_write(updates)

            logger.info(
                f'{res.upserted_count} unique articles updated or inserted in the database.')
            logger_debug.info(
                f'{res.upserted_count} unique articles updated or inserted in the database.')
        except pm.errors.InvalidOperation:
            logger_debug.debug(
                'Trying an insert_or_update_articles with no articles.')
        except pm.errors.OperationFailure:
            logger_debug.exception('Update failed')

    def update_articles(self, articles: typing.List[gn_article.Article]) -> None:
        """Update articles in the database with Article objects.
        If the articles does not exists in the database, no articles will be updated."""

        try:
            filtered_articles = [article.to_filtered_dict()
                                 for article in articles]

            updates = [pm.UpdateOne({'link': article['link']}, {'$set': article})
                       for article in filtered_articles]
            res = self.articles_collection.bulk_write(updates)

            logger.info(
                f'{res.modified_count} articles updated in the database.')
            logger_debug.info(
                f'{res.modified_count} articles updated in the database.')
        except pm.errors.InvalidOperation:
            logger_debug.debug('Trying an update_articles with no articles.')
        except pm.errors.OperationFailure:
            logger_debug.exception('Update failed')

    # GET METHODS

    def get_article(self, article: gn_article.Article) -> gn_article.Article:
        """Return the article expected if it exists in the database"""

        article = article.to_filtered_dict()
        res = self.articles_collection.find_one(article)
        return res

    def get_articles_never_processed(self, n_max_articles: int) -> typing.List[gn_article.Article]:
        """Return a list of len <= n_max_articles articles
        that has never been processed."""

        raw_articles = list(self.articles_collection.find({
            'processings': {'$exists': True, '$eq': {}}
        }).limit(n_max_articles))

        articles = [gn_article.Article(raw_article)
                    for raw_article in raw_articles]
        return articles

    def get_articles_missing_process(self, processing: gn_processing.Processing, n_max_articles: int) -> typing.List[gn_article.Article]:
        """Return a list of len <= n_max_articles articles
        that miss the given processing."""

        key = 'processings.' + processing.name
        raw_articles = list(self.articles_collection.find(
            {key: {'$exists': False}}
        ).limit(n_max_articles))

        articles = [gn_article.Article(raw_article)
                    for raw_article in raw_articles]
        return articles

    def get_yesterday_articles_missing_process(self, processing: gn_processing.Processing) -> typing.List[gn_article.Article]:
        """Return a list of yesterday articles
        that miss the given processing."""

        yesterday = dt.datetime.now() - dt.timedelta(days=1)
        start_time = dt.datetime.combine(yesterday, dt.time(0,0,0))
        end_time = dt.datetime.combine(yesterday, dt.time(23,59,59))
        key = 'processings.' + processing.name
        raw_articles = list(self.articles_collection.find(
            {"$and": [
                {key: {'$exists': False}},
                {"date": {"$gte": start_time, "$lte": end_time}}
            ]}))

        articles = [gn_article.Article(raw_article)
                    for raw_article in raw_articles]
        return articles

    def get_articles_process_updated_before(self, processing: gn_processing.Processing, date: dt.datetime, n_max_articles: int) -> typing.List[gn_article.Article]:
        """Return a list of  len <= n_max_articles articles
        for which the given processing has been updated before the given date."""

        key = 'processings.' + processing.name + '.updated_at'
        raw_articles = list(self.articles_collection.find(
            {'$or': [
                {key: {'$exists': True, '$lt': date}},
                {key: {'$exists': False}}
            ]}).limit(n_max_articles))

        articles = [gn_article.Article(raw_article)
                    for raw_article in raw_articles]
        return articles

    # CHECK METHOD

    def sanity_check(self, mode: str = "localhost", fix: bool = False) -> None:
        """Scan the database for unprocessed or outdated articles.
        If fix is True the method will try to fix the issues and not only report them.
        Write a <date>_database_summary_log.csv file that contains every problematic articles.
        """

        # ----- Initialize logger -----
        now = dt.datetime.now().isoformat()
        filename = f'logs/{now}_database_summary_log.csv'
        summary_logger = gn_misc.initialize_logger(
            'database_summary_logger', filename)
        summary_logger.info(
            '-------------------------------------------------------------')
        summary_logger.info(f'--- Database sanity summary of {now} ---')
        summary_logger.info(
            '-------------------------------------------------------------')
        logger.info(
            f'Database sanity check started. See {filename} for details of the sanity check.')
        logger_debug.info(
            f'Database sanity check started. See {filename} for details of the sanity check.')

        # ----- Get articles with missing processings and reprocess them -----
        summary_logger.info('1. Checking for missing processings...')

        if mode == "localhost":
            processings = [gn_config_processing.MasculinityRateAndNames,
                           gn_config_processing.HomogenousCategory]

        else:
            processings = [gn_config_processing.Quotes]

        for processing in processings:
            processing = processing()

            articles = self.get_articles_missing_process(
                processing, 1000)
            summary_logger.info(
                f'{len(articles)} articles without {processing.name} retrieved.')

            if fix:
                # Try to fix problematic articles
                summary_logger.info('Starting to fix problematic articles...')
                articles = processing.apply_on(articles)
                self.update_articles(articles)

                # Get articles that are still problematic and report them in log file and terminal
                articles = self.get_articles_missing_process(
                    processing, 1000)
                if len(articles) > 0:
                    logger_debug.warning(
                        f'{len(articles)} articles without {processing.name} retrieved even after trying to fix them.')
                    summary_logger.warning(
                        f'{len(articles)} articles without {processing.name} retrieved even after trying to fix them:')
                    for article in articles:
                        summary_logger.warning(f'\t{article.link}')

        # ----- Get outdated articles and reprocess them -----
        summary_logger.info('2. Checking for outdated processings...')
        for processing in processings:
            processing = processing()

            articles = self.get_articles_process_updated_before(
                processing, processing.get_last_update_date(), 1000)

            summary_logger.info(
                f'{len(articles)} outdated articles found for the {processing.name} process.')

            if fix:
                summary_logger.info(f'Updating articles {processing.name}...')

                articles = processing.apply_on(articles)
                self.update_articles(articles)

                summary_logger.info(f'{len(articles)} articles updated.')

        logger.info('Database sanity check finished.')
        logger_debug.info('Database sanity check finished.')

    def re_extract_and_process_everything(self):
        """re-extract and re-process every articles in the database.
        For the reprocessing to work, the articles link, date and source_name must be correct.
        """

        raw_articles = list(self.articles_collection.find())

        logger.info(f'{len(raw_articles)} articles found.')

        articles = []
        for raw_article in raw_articles:
            try:
                collector: gn_collector.Collector = gn_config_collector.collectors[raw_article['source_name']](
                )
                article = collector.create_article_from_link(
                    raw_article['link'], raw_article['date'])

                logger.info(f'{article.link} re-extracted.')
            except:
                logger.exception(f'{raw_article["link"]} extraction failed.')
                continue
            articles.append(article)

        for processing in gn_config_processing.processings:
            try:
                processing = processing()
                articles = processing.apply_on(articles)

                logger.info(
                    f'{processing.name} processing re-applied on articles.')
            except:
                logger.exception(f'{processing.name} processing failed.')

        self.update_articles(articles)
        logger.info(
            f'{len(articles)} articles re-extracted and re-processed.')
