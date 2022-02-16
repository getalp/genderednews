"""Project setup."""

import os
from setuptools import setup, find_packages
import nltk
import stanza

setup(name='genderednews', version='0.1', packages=find_packages())

DIRNAME = "logs"
try:
    os.makedirs(DIRNAME)
except FileExistsError:
    pass

nltk.download('punkt')
stanza.download("fr")
