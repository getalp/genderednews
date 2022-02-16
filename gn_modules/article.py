"""
Module containing functions for the exctraction.
"""

import typing
import enum
import random
import logging
import datetime as dt
import newspaper as np
import faker

import gn_modules.misc as gn_misc
from gn_modules.category import Category

logger = logging.getLogger('genderednews.article')
logger_debug = logging.getLogger('genderednews_debug.article')


class Article():
    """Article class."""

    class Access(gn_misc.AutoName):
        """Describes if an article is free or if it needs a subscription."""
        INDEFINI = enum.auto()
        PAYANT = enum.auto()
        GRATUIT = enum.auto()

        def to_string(self) -> str:
            """From Access to string."""
            return self.value

        @staticmethod
        def from_string(key) -> 'Access':
            """From string to Access."""
            return Article.Access(key)

    def __init__(self, art_dict: typing.Dict) -> None:
        """Constructor of the Article class (uses a dictionary)."""

        self.link: str = art_dict['link']
        self.title: str = art_dict['title']
        if not isinstance(art_dict['date'], dt.datetime):
            raise TypeError('The date should always be of type datetime.')
        else:
            self.date: dt.datetime = art_dict['date']
        if 'text' in art_dict.keys():
            self._text: str = art_dict['text']
        else:
            self._text = None
        self.authors: typing.List[str] = art_dict['authors']
        self.category: str = art_dict['category']
        # self.keywords: typing.List[str] = art_dict['keywords']
        self.word_count: int = art_dict['word_count']
        self.source_name: str = art_dict['source_name']
        if 'hero_image' in art_dict.keys():
            self.hero_image: str = art_dict['hero_image']
        self.access: Article.Access = Article.Access.from_string(
            art_dict['access'])
        if 'processings' in art_dict.keys():
            self.processings = art_dict['processings']
        else:
            self.processings = {}

        try:
            self.check_valid()
        except AssertionError:
            import gn_modules.db_helper as gn_db
            logger_debug.debug(
                f'This article is invalid! It will be removed from the database')
            db_helper = gn_db.DbHelper(test=False)
            db_helper.delete_article(self)

    def check_valid(self) -> None:
        """Check if the necessary values are correct and not empty."""

        logger_debug.debug(f'Checking article: {self.link}')

        # Link must be provided
        assert self.link
        # Title must be provided
        assert self.title
        # Date must be in the past
        assert self.date
        assert self.date <= dt.datetime.now()
        # Text is not mandatory
        # Authors must contain at least 1 author
        assert self.authors
        assert self.authors[0]
        # Category must be provided
        assert self.category
        # Keywords are not mandatory
        # Word count must be a positive integer
        assert self.word_count > 0
        # Source_name must be a string
        assert self.source_name
        assert isinstance(self.source_name, str)
        # Hero_image is not mandatory
        # Metadata is not mandatory
        # Access must be a valid Access
        assert self.access
        assert isinstance(self.access, Article.Access)
        # Processings must be a dict (empty or not)
        assert self.processings or self.processings == {}
        assert isinstance(self.processings, dict)

    def to_raw_dict(self) -> typing.Dict:
        """Format an article to a dictionnary (ex: to store in the database)."""

        # Transform the basic info  (link, date, title, etc.) in the right format
        return {
            'link': self.link,
            'title': self.title,
            'date': self.date,  # format in string
            'text': self._text,  # No text stored in database
            'authors': self.authors,
            'category': self.category,
            'word_count': self.word_count,
            # 'keywords': self.keywords,
            'source_name': self.source_name,
            'hero_image': self.hero_image,
            'access': self.access.to_string(),
            'processings': self.processings
        }

    def to_filtered_dict(self) -> typing.Dict:
        """
        Return a raw dict (useful for storing it into a database) without
        the information we don't want to store permanently:
        - text
        """

        res = self.to_raw_dict()
        res.pop('text', None)
        return res

    def add_processing(self, processing_name: str, indicators: typing.Dict, date: dt.datetime) -> 'Article':
        """Add or update a processing in the Article."""

        # Inform if the indcator already exists in the Article
        if processing_name in self.processings.keys():
            logger_debug.debug(f'{processing_name} updated in {self.link}')
        else:
            logger_debug.debug(f'{processing_name} added in {self.link}')

        # Add or update the processing
        self.processings[processing_name] = {
            'updated_at': date,
            'indicators': indicators
        }

        return self

    def get_text(self) -> str:
        """Method that downloads the text of the article if not present and returns it."""

        if self._text is None:
            art = np.Article(self.link, language='fr')
            art.download()
            try:
                art.parse()
            except np.article.ArticleException:
                logger.exception(
                    f'Error occured during the parsing of {self.link}.')
                logger_debug.exception(
                    f'Error occured during the parsing of {self.link}.')
                return ''
            self._text = art.text
        return self._text

    @staticmethod
    def create_random_article(_fake: faker.Factory) -> 'Article':
        """Given a faker Factory, generate and return a random article."""

        link = str(_fake.url())
        date = _fake.date_time_between(start_date='-10y', end_date='now')
        title = _fake.sentence(nb_words=5)
        source_name = ' '.join(_fake.words(nb=2))
        authors = [_fake.name(), _fake.name()]
        category = _fake.word(ext_word_list=Category)
        # keywords = _fake.words(nb=3)
        word_count = random.randrange(3000, 5000)
        hero_image = str(_fake.image_url())
        access = _fake.word(ext_word_list=Article.Access)
        processings = {}

        return Article({
            'link': link,
            'title': title,
            'date': date,
            # No text stored in database
            'authors': authors,
            'category': category.value,
            # 'keywords': keywords,
            'word_count': word_count,
            'source_name': source_name,
            'hero_image': hero_image,
            'access': access.to_string(),
            'processings': processings,
        })

    def clear_text(self) -> None:
        """Clears text field (not tested)."""
        self._text = None
