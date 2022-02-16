"""
Convenience wrapper module for dotenv.
"""

import os
import dotenv


def load_dotenv_secure() -> str:
    """Load the .env file and throws an error if it does not exist."""

    # Check if .env file exists in root directory
    path_to_dotenv = os.path.abspath(__file__ + "/../../.env")
    if not os.path.isfile(path_to_dotenv):
        raise FileNotFoundError(
            'File \'.env\' does not exist. Create \'.env\' file from \'.env.example\'.'
        )

    dotenv.load_dotenv()

    db_addr = os.getenv('DB_ADDR')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    db_collection = os.getenv('DB_ARTICLE_COLLECTION')

    assert os.getenv('DB_GRAPHS_NAME')

    assert db_addr
    assert db_port
    assert db_name
    assert db_collection

    assert os.getenv('API_KEY')
    assert os.getenv('API_SECRET_KEY')
    assert os.getenv('ACCESS_TOKEN')
    assert os.getenv('ACCESS_TOKEN_SECRET')

    assert os.getenv('GENDEREDNEWS_HOST')
    assert os.getenv('GENDEREDNEWS_PORT')
    assert os.getenv('ssh_USER')
    assert os.getenv('ssh_PKEY')

    return f'{db_addr}:{db_port}/{db_name}.{db_collection}'
