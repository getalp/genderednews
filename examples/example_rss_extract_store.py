"""
Example that:
- scraps articles published yesterday's links from a news source
- extracts relevant data from each article
- stores the data in the database
"""

import time
import datetime as dt

import gn_modules.db_helper as gn_db
import gn_modules.secure_dotenv as gn_dotenv
import gn_modules.scraping_and_extraction.collector as gn_collector
import gn_modules.scraping_and_extraction.collectors.le_monde as gn_le_monde
import gn_modules.scraping_and_extraction.rss_source as gn_rss
import gn_modules.misc as gn_misc


if __name__ == '__main__':
    # Initialize logger
    today = dt.datetime.now().date().isoformat()
    logger = gn_misc.initialize_logger(
        'rss_exctract_store', f'logs/{today}_example_rss_exctract_store.log', terminal=True)

    # Load environment variables
    gn_dotenv.load_dotenv_secure()

    # Connect to the database & get the articles collection
    db_helper = gn_db.DbHelper()

    # Create the collector
    le_monde = gn_le_monde.LeMonde()

    # Scrape and extract yesterday's articles from multiple RSS feeds in the collector config
    articles = le_monde.scrape_and_extract_articles_of_yesterday()

    # Store article in the database
    db_helper.insert_or_update_articles(articles)

    logger.info(
        f'{len(articles)} new articles from {le_monde.source.name} added to the database!')
