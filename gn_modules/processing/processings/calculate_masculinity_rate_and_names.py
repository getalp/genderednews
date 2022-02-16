"""
Script to calculate the masculinity rate and names from an given url
"""

import os
import sys
import pandas as pd
import newspaper as np
from nltk import RegexpTokenizer
import gn_modules.processing.processings.masculinity_rate_and_names as masculinity


def process_text_one_article(txt: str):
    """
    Match names from the names_df to the article text and comput the masculinity_rate as the mean
    of each name masculinity.
    """
    # Method without NER extraction (the found first names are matched with any token in the text)
    names_df = __get_names_df()
    txt = masculinity.MasculinityRateAndNames().normalize_txt(txt)
    pattern = r"\b[dlnmtsj]'|qu'|\w+(?:['-]\w+)*"
    tokenizer = RegexpTokenizer(pattern)
    list_tokens = tokenizer.tokenize(txt)
    list_tokens = masculinity.MasculinityRateAndNames().filter_uppercase(list_tokens)
    txt_tokens = pd.DataFrame({'word': [word.lower() for word in list_tokens]})
    txt_tokens_with_name = pd.merge(txt_tokens, names_df, how='left')
    _names = txt_tokens_with_name.dropna(
        subset=["sexratio_prenom"], inplace=False)
    _names = _names['word']
    m_rate = txt_tokens_with_name['sexratio_prenom'].mean()
    return (m_rate, _names)


def __get_names_df() -> pd.DataFrame:
    """
    Return a pandas dataframe from the data/prenoms_clean.csv file.
    """
    name_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'data/prenoms_clean.csv')
    names_df = pd.read_csv(name_file, sep=';')
    names_df = names_df.rename(columns={'preusuel': 'word'})
    return names_df


def extract_text_from_link(link: str):
    """
    Extract the text from the given link
    """
    article = np.Article(link, language='fr')
    article.download()
    article.parse()
    return article.text


def display_result():
    """
    Display results
    """
    text = extract_text_from_link(sys.argv[1])
    print("\nThe text of the article: \n\n" + text + "\n")
    (masculinity_rate, names) = process_text_one_article(text)
    print("Masculinity rate: " + str(masculinity_rate) + "\n")
    print("List of names extracted:")
    for name in names:
        print("- " + name)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Error usage: python3 " + sys.argv[0] + " <url>")
        sys.exit()
    display_result()
