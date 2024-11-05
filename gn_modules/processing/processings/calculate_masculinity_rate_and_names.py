"""
Script to calculate the masculinity rate and names from an given url
"""

import os
import sys
import pandas as pd
import newspaper as np
# from nltk import RegexpTokenizer
import spacy
import gn_modules.processing.processings.masculinity_rate_and_names as masculinity
nlp = spacy.load("fr_core_news_md")

def process_text_one_article(txt: str):
    """
    Match names from the names_df to the article text and comput the masculinity_rate as the mean
    of each name masculinity.
    """
    names_df = __get_names_df()
    txt = masculinity.MasculinityRateAndNames().normalize_txt(txt)
    """
    # OLD: method without NER extraction (the found first names are matched with any tokens in the text)
    pattern = r"\b[dlnmtsj]'|qu'|\w+(?:['-]\w+)*"
    tokenizer = RegexpTokenizer(pattern)
    list_tokens = tokenizer.tokenize(txt)
    list_tokens = masculinity.MasculinityRateAndNames().filter_uppercase(list_tokens)
    txt_tokens = pd.DataFrame({'word': [word.lower() for word in list_tokens]})
    txt_tokens_with_name = pd.merge(txt_tokens, names_df, how='left')
    _names = txt_tokens_with_name.dropna(
        subset=["sexratio_prenom"], inplace=False)
    _names = _names['word']
    m_rate = txt_tokens_with_name['sexratio_prenom'].mean()"""
    # Method with NER extraction
    doc = nlp(txt)
    ents = [ent.text for ent in doc.ents if ent[0].ent_type_ == "PER"]
    if ents:
        # TODO: this assumes that the first tok of the ent is always the first name
        flattened_ents = [ent.split()[0].strip("«».").lower() for ent in ents]
        ner_tokens = pd.DataFrame(flattened_ents, columns=["word"])
        txt_tokens_with_name = pd.merge(ner_tokens, names_df, how='left').dropna(
            subset=["sexratio_prenom"], inplace=False)
        _names = txt_tokens_with_name["word"]
        m_rate = txt_tokens_with_name['sexratio_prenom'].mean()
    else:
        m_rate = None
        _names = None
    return (m_rate, _names)

def __get_names_df() -> pd.DataFrame:
    """
    Return a pandas dataframe from the data/prenoms_clean.csv file.
    """
    name_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'data/prenoms.csv')
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
    if sys.argv[1].endswith("txt"):
        with open("sys.argv[1]", "r") as f:
            text = f.readlines()
    else: # assuming an url was provided
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
