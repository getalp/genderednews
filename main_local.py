"""
Example that:
- scraps articles published yesterday's links from a news source
- extracts relevant data from each article
- stores the data in the database
- process the unprocessed articles
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

    # Connect to database
    db_helper = gn_db.DbHelper()
    logger.info(f'Environment file loaded and database connected: {db_info}')

    # ----- 1. Scrape, Extract & Push new articles to db -----

    logger.info('')
    logger.info('--------------------------------------------------------------')
    logger_debug.info(
        '--------------------------------------------------------------')
    logger.info('- STEP 1 - Scraping, extracting and storing to the database. -')
    logger_debug.info('- STEP 1 -')
    logger.info('--------------------------------------------------------------')
    logger_debug.info(
        '--------------------------------------------------------------')

    for collector in gn_collector.collectors.values():
        # Instanciate class
        # There are 2 methods for scraping: via rss feeds or via twitter tweets
        collector = collector(scraping_mode="twitter")
        logger.info(
            f'Scraping and extracting yesterday\'s articles from \'{collector.source.name}\'... (this may take a while)')
        logger_debug.info(
            f'Scraping and extracting yesterday\'s articles from \'{collector.source.name}\'...')

        # Scrape and extract articles
        articles = collector.scrape_and_extract_articles_of_yesterday()
        logger.info(
            f'{len(articles)} articles scraped and extracted (there may be duplicates).')
        logger_debug.info(
            f'{len(articles)} articles scraped and extracted (there may be duplicates).')

        # Insert extracted articles
        db_helper.insert_or_update_articles(articles)

    # ----- 2. Retrieve & process non-processed articles -----

    logger.info('')
    logger.info('--------------------------------------------------------')
    logger_debug.info(
        '--------------------------------------------------------')
    logger.info('----- STEP 2 - Processing of unprocessed articles. -----')
    logger_debug.info('----- STEP 2 -----')
    logger.info('--------------------------------------------------------')
    logger_debug.info(
        '--------------------------------------------------------')

    # Get never processed articles
    articles = db_helper.get_articles_never_processed(1000)
    logger.info(
        f'{len(articles)} unprocessed articles retrieved for processing.')
    logger_debug.info(
        f'{len(articles)} unprocessed articles retrieved for processing.')

    time_start = dt.datetime.now()
    # Process the articles
    for processing in [gn_processing.MasculinityRateAndNames, gn_processing.HomogenousCategory]:
        processing = processing()  # Instanciate the class
        logger.info(f'Starting the {processing.name} processing.')
        logger_debug.info(f'Starting the {processing.name} processing.')
        articles = processing.apply_on(articles)
    logger.info('Articles processed.')
    logger_debug.info('Articles processed.')

    time_end = dt.datetime.now()

    # Push processed articles to db
    db_helper.update_articles(articles)

    # ----- 3. Sanity check of the db -----

    logger.info('')
    logger.info('-------------------------------------------------')
    logger_debug.info('-------------------------------------------------')
    logger.info('----- STEP 3 - Sanity check of the database -----')
    logger_debug.info('----- STEP 3 -----')
    logger.info('-------------------------------------------------')
    logger_debug.info('-------------------------------------------------')

    # Check database
    db_helper.sanity_check(fix=False)

    # Show memory usage
    current, peak = tracemalloc.get_traced_memory()
    logger_debug.debug(
        f'Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB')
    tracemalloc.stop()

    # Show processing time
    total_time = dt.timedelta(seconds=(time_end - time_start).total_seconds())
    total_time = str(total_time).split('.', 2)[0]
    logger_debug.debug(f'Processing time: {total_time}')
