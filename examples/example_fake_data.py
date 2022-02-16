""""
Fill a database with fake data.
"""

import time
import argparse
import datetime as dt
import pymongo as pm
import faker

import gn_modules.db_helper as gn_db
import gn_modules.article as gn_article
import gn_modules.secure_dotenv as gn_dotenv
import gn_modules.misc as gn_misc


gn_dotenv.load_dotenv_secure()

# 20 articles * 10 sources * 365 days * 10 years
DEFAULT_N_ARTICLES = 20 * 10 * 365 * 10
BULK_SIZE = 10000


def create_arg_parser():
    """A simple function creating an arg parser for command line argument."""

    _arg_parser = argparse.ArgumentParser(
        description='Fill the database with random articles.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _arg_parser.add_argument('-n', metavar='narticles', type=int,
                             help='The number of articles to create', default=DEFAULT_N_ARTICLES)
    _arg_parser.add_argument('--no_text', default=False, action='store_true',
                             help='Remove the text column from the articles. Resulting in faster generation and less memory consumption.')
    return _arg_parser


if __name__ == '__main__':
    today = dt.datetime.now().date().isoformat()
    logger = gn_misc.initialize_logger(
        'fake_data', f'logs/{today}_fake_data.log', terminal=True)

    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    logger.info(
        f'Starting to fill the database with {args.n} random articles.')

    fake = faker.Factory.create('fr_FR')  # using french names, cities, etc.

    db_helper = gn_db.DbHelper()

    # Bacth size and bulk size
    batch_size = args.n

    operations = []
    # Let's insert some articles
    for i in range(batch_size):
        if i % BULK_SIZE == 0:  # log every bulk write
            logger.info('%s - records %s ' % (time.strftime("%H:%M:%S"), i))

        if i % BULK_SIZE >= (BULK_SIZE-1):  # bulk write
            try:
                db_helper.articles_collection.bulk_write(operations)
            except pm.errors.BulkWriteError:
                logger.exception()
            operations = []

        # Fake article info
        article = gn_article.Article.create_random_article(fake)

        # Create article record
        try:
            operations.append(pm.InsertOne(article.to_raw_dict()))
        except (pm.errors.WriteError, pm.errors.WriteConcernError):
            logger.exception('insert failed:', i, ' error : ')

    # write remaining articles
    try:
        db_helper.articles_collection.bulk_write(operations)
    except pm.errors.BulkWriteError:
        logger.exception()

    logger.info('Done!')
