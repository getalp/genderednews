"""
Example that:
- process the quotes unprocessed articles
"""

import logging
import datetime as dt
import tracemalloc

import gn_modules.db_helper as gn_db
import gn_modules.secure_dotenv as gn_dotenv
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.processing.config_processings as gn_processing
import gn_modules.scraping_and_extraction.config_collectors as gn_collector
import gn_modules.article as gn_article
import gn_modules.misc as gn_misc

if __name__ == '__main__':
    # ----- 0. Initialization -----

    # Used to trace memory usage
    tracemalloc.start()

    # Initialize logger
    today = dt.datetime.now().date().isoformat()
    logger = gn_misc.initialize_logger(
        'genderednews', f'logs/{today}_main_log.log', terminal=True, level=logging.INFO)
    logger_debug = gn_misc.initialize_logger(
        'genderednews_debug', f'logs/{today}_main_debug_log.log', terminal=False, level=logging.DEBUG)

    # Load environment variables
    db_info = gn_dotenv.load_dotenv_secure()

    # Connect to database via ssh
    db_helper = gn_db.DbHelper(mode="ssh")
    logger.info(f'Environment file loaded and database connected: {db_info}')

    # ----- 2. Retrieve & process articles with quotes non-processed -----

    logger.info('')
    logger.info('--------------------------------------------------------')
    logger_debug.info(
        '--------------------------------------------------------')
    logger.info('----- STEP 2 - Processing of quotes unprocessed articles. -----')
    logger_debug.info('----- STEP 2 -----')
    logger.info('--------------------------------------------------------')
    logger_debug.info(
        '--------------------------------------------------------')

    # Get missing Quotes processing articles
    quotes = gn_processing.Quotes() # Instanciate the class
    articles = db_helper.get_yesterday_articles_missing_process(quotes)
    logger.info(
        f'{len(articles)} quotes unprocessed articles retrieved for processing.')
    logger_debug.info(
        f'{len(articles)} quotes unprocessed articles retrieved for processing.')

    time_start = dt.datetime.now()
    # Process the articles
    logger.info(f'Starting the {quotes.name} processing.')
    logger_debug.info(f'Starting the {quotes.name} processing.')
    articles = quotes.apply_on(articles)
    logger.info('Articles processed.')
    logger_debug.info('Articles processed.')

    time_end = dt.datetime.now()

    # Push processed articles to db
    db_helper.update_articles(articles)

    """
    # ----- 3. Sanity check of the db -----

    logger.info('')
    logger.info('-------------------------------------------------')
    logger_debug.info('-------------------------------------------------')
    logger.info('----- STEP 3 - Sanity check of the database -----')
    logger_debug.info('----- STEP 3 -----')
    logger.info('-------------------------------------------------')
    logger_debug.info('-------------------------------------------------')

    # Check database
    db_helper.sanity_check(mode="ssh", fix=False)
    """

    # Stop ssh connection
    db_helper.ssh_stop()

    # Show memory usage
    current, peak = tracemalloc.get_traced_memory()
    logger_debug.debug(
        f'Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB')
    tracemalloc.stop()

    # Show processing time
    total_time = dt.timedelta(seconds=(time_end - time_start).total_seconds())
    total_time = str(total_time).split('.', 2)[0]
    logger_debug.debug(f'Processing time: {total_time}')
