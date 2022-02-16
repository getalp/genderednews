"""
Define the MasculinityRateAndNames class.
"""

import os
import typing
import unicodedata
import re
import pandas as pd
from nltk import RegexpTokenizer
#import stanza


import gn_modules.processing.processing as gn_processing
#from gn_modules.processing.processings.quote_extractor.french_pipeline.genderization import remove_titles, extract_first_name, clean_ne
#nlp = stanza.Pipeline("fr",use_gpu=False)


class MasculinityRateAndNames(gn_processing.Processing):
    """
    The MasculinityRateAndNames compute the masculinity rate
    and extracted name from the article text.
    The extraction is done by looking for names from the data/prenoms_clean.csv file into the article.
    """

    MASCULINITY_RATE = 'masculinity_rate'

    def __init__(self) -> None:
        self.name = 'masculinity_rate_and_names'
        self.indicators = [self.MASCULINITY_RATE]
        self.names_df = self.__get_names_df()

    def process_text_one_article(self, txt: str) -> typing.Dict:
        """
        Match names from the names_df to the article text and comput the masculinity_rate as the mean
        of each name masculinity.
        """
        # Method without NER extraction (the found first names are matched with any token in the text)
        txt = self.normalize_txt(txt)
        pattern = r"\b[dlnmtsj]'|qu'|\w+(?:['-]\w+)*"
        tokenizer = RegexpTokenizer(pattern)
        list_tokens = tokenizer.tokenize(txt)
        list_uppercase = self.filter_uppercase(list_tokens)
        txt_tokens = pd.DataFrame(
            {'word': [word.lower() for word in list_uppercase]})
        txt_tokens_with_name = pd.merge(txt_tokens, self.names_df, how='left')
        m_rate = txt_tokens_with_name['sexratio_prenom'].mean()

        # Method with NER extraction (the found first names are only matched with extracted named entities)
        """
        #a dictionnary containing a list of all Named Entities (who are people)
        nlped_txt = nlp(txt)
        fnames_dict = {"word":["filler"]} #filler to have at least one entry in the dictionary
        for ent in nlped_txt.entities:
            if ent.type == "PER":
                clean_fname = extract_first_name(remove_titles(clean_ne(ent.text))).lower()
                if clean_fname != "":
                    fnames_dict["word"].append(clean_fname)

        txt_fnames = pd.DataFrame.from_dict(fnames_dict)
        txt_fnames['id'] = txt_fnames.index
        gendered_names = pd.merge(txt_fnames, self.names_df, how='left')
        m_rate = gendered_names['sexratio_prenom'].mean()
        """
        return {self.MASCULINITY_RATE: m_rate}

    def __get_names_df(self) -> pd.DataFrame:
        """
        Return a pandas dataframe from the data/prenoms_clean.csv file.
        """

        name_file = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'data/prenoms_clean.csv')

        names_df = pd.read_csv(name_file, sep=';')
        names_df = names_df.rename(columns={'preusuel': 'word'})

        return names_df

    def normalize_txt(self, txt, rm_new_lines=False, lower=False):
        """
        Normalize text
        """

        # Convert txt to unicode
        if isinstance(txt, bytes):
            txt = txt.decode(encoding='utf-8', errors='strict')
        elif isinstance(txt, str):
            pass
        else:
            raise TypeError("not expecting type '%s'" % type(txt))

        # Normalize unicode
        txt = unicodedata.normalize("NFC", txt)

        # Normalize whitespace characters and remove carriage return
        if rm_new_lines:
            remap = {ord('\f'): ' ', ord('\r'): '',
                     ord('\n'): '', ord('\t'): ''}
            txt = txt.translate(remap)
        else:
            remap = {ord('\f'): ' ', ord('\r'): ''}
            txt = txt.translate(remap)

        # Remove URLs in text
        pattern = re.compile(r'(?:www|http)\S+|<\S+|\w+\/*>')
        txt = re.sub(pattern, '', txt)

        # Remove multiple spaces
        pattern = re.compile(r'( ){2,}')
        txt = re.sub(pattern, r' ', txt)

        # to lowercase
        if lower:
            txt = txt.lower()

        return txt

    def filter_uppercase(self, list_tokens: list):
        """
        Filter tokens that start with an uppercase letter
        """
        res = []
        for tokens in list_tokens:
            if tokens[0].isupper():
                res.append(tokens)
        return res
