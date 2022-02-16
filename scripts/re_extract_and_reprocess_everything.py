"""
A simple script that re extract and re process every articles in the database.
"""

import datetime as dt

from gn_modules.secure_dotenv import load_dotenv_secure
from gn_modules.db_helper import DbHelper
from gn_modules.misc import initialize_logger


logger = initialize_logger(
    'genderednews', filename=f'logs/{dt.datetime.now().date()}_re_extract_and_reprocess.log', terminal=True)
load_dotenv_secure()
db_helper = DbHelper(mode="localhost")

db_helper.re_extract_and_process_everything()
