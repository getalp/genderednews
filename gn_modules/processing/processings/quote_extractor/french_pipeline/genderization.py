#!/usr/bin/env python
# coding: utf-8

"""
Genderization process of speaker with several indices:
- pronoun (il/elle)
- first name (with gender_detector library or the INSEE names database of /data/prenoms.csv)
- title (Monsieur/Madame,...)
- job (with utils/occupations_clean.csv, which is a list of non-ambiguous job names and the gender of each)

INPUT: the output of quote_extractor script (either a folder of Json file or database documents)
OUTPUT: Either a database update (TODO: configurate) or a folder of Json files, similar to the input but with added speaker gender for each quote

1 is completely male
0 is completely female
"""

import re
from statistics import mean
import pandas as pd
import os

import stanza
nlp = stanza.Pipeline("fr",use_gpu=False)

occupations_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../data/occupations_clean.csv')
jobs_df = pd.read_csv(occupations_file, delimiter=";",index_col=0, header=None, squeeze=True)
jobs_dict=jobs_df.to_dict()

#First names libraries
import gender_guesser.detector as gender
d = gender.Detector()

prenoms_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../../data/prenoms.csv')
names_df = pd.read_csv(prenoms_file, delimiter=";")

# --- utils
def remove_titles(txt):
    """Method to clean special titles that appear as prefixes or suffixes to
       people's names (common especially in articles from British/European sources).
       The words that are marked as titles are chosen such that they can never appear
       in any form as a person's name (e.g., "Mr", "MBE" or "Headteacher").
    """
    honorifics = ["Mr", "Ms", "Mrs", "Miss", "Dr", "Sir", "Dame", "Hon", "Professor",
                  "Prof", "Rev", "Me", "M(\.)?","Monsieur", "Madame","Mme", "Mlle", "Mademoiselle"]
    titles = ["QC", "CBE", "MBE", "BM", "MD", "DM", "BHB", "CBC",
              "Reverend", "Recorder", "Headteacher", "Councillor", "Cllr", "Father", "Fr",
              "Mother", "Grandmother", "Grandfather", "Creator", "Père", "Frère", "S(œ|oe)ur","Mère","Grand-père", "Grand-mère"]
    extras = ["et al", "www", "href", "http", "https", "Ref", "rel", "eu", "span", "Rd", "St"]
    banned_words = r'|'.join(honorifics + titles + extras)
    # Ensure only whole words are replaced (\b is word boundary)
    pattern = re.compile(r'\b({})\b'.format(banned_words)) 
    txt = pattern.sub('', txt)
    return txt.strip()

def clean_ne(name):
    """Clean named entities for standardization in encoding and name references."""
    name = re.sub('[&\"\/\(\)=+\}\{*\.#^$£!:;?,§~\[\]`<>]', ' ', name).strip()   # Remove all special characters from name except dash (to keep names such as "Jean-Christophe")
    # Remove 's from end of names. Frequent patterns found in logs.
    # the ' has been replace with space in last re.sub function
    if name.endswith(' s'):
        name = name[:-2]
    name = re.sub(r'\s+', ' ', name)
    name = remove_titles(name)
    return name.strip()

def extract_first_name(full_name):
    """Extract first names before annotating gender"""
    if full_name.strip().count(' ') == 0:
        return full_name
    else:
        return full_name.split()[0]

# --- check functions
def check_title(speaker):
    title_gender = None
    honorifics_M = r"|".join(["Mr", "M(\.)?","Monsieur","Sir", "Père", "Frère"])
    honorifics_F = r"|".join(["Ms", "Mrs", "Miss", "Madame","Mme", "Mlle", "Mademoiselle","Mère","Sœur"])
    if re.search(re.compile(r"\b({})\b".format(honorifics_M)), speaker) is not None:
        title_gender = 1
    elif re.search(re.compile(r"\b({})\b".format(honorifics_F)), speaker) is not None:
        title_gender = 0
    return title_gender


def check_pronoun(speaker):
    pron_gender = None
    if re.search("(\b|^)(-?([Ii]l(s)?)|lui)\.?(\b|$)",speaker) is not None:
        pron_gender = 1
    elif re.search("(\b|^)(-?[Ee]lle(s)?)\.?(\b|$)",speaker) is not None:
        pron_gender = 0
    return pron_gender

def check_NER(speaker):
    ner_gender = None
    speaker = clean_ne(speaker)
    doc = nlp(speaker)
    ents = [ent for ent in doc.entities if ent.type == "PER"]
    if len(ents) > 0:
        candidate_speaker = ents[0].text #assuming it's the first entity in the speaker if there is several
        speaker = remove_titles(candidate_speaker)
        first_name = extract_first_name(speaker)
        if first_name is not None:
            #Insee database method
            try:
                gender_score_name = names_df.loc[(names_df["preusuel"]==first_name.lower()),"sexratio_prenom"].values[0]
                return float(gender_score_name.replace(",","."))
            except (KeyError,IndexError):
                # Else: gender_guesser method
                gender = d.get_gender(first_name)
                if gender == "female":
                    ner_gender = 0
                elif gender=="mostly_female":
                    ner_gender = 0.2
                elif gender in ["andy"]:
                    ner_gender = 0.5
                elif gender == "mostly_male":
                    ner_gender = 0.8
                elif gender == "male":
                    ner_gender = 1
                return ner_gender
    return ner_gender

def check_job(speaker):
    #TODO: add "ambiguous" job names (e.g: "ministre") and check gender with parser feats
    job_gender = None
    doc = nlp(speaker)
    nouns = [noun.text.lower() for noun in doc.sentences[0].words if noun.upos == "NOUN"]
    for noun in nouns:
        if noun in jobs_dict.keys():
            job_gender = jobs_dict[noun]
    return job_gender

# main functions
def get_gender(speaker):
    """tries to determine the gender of the speaker from several criteria"""
    if speaker == "":
        return "unknown"
    else:
        indices_list = {
            "title":check_title(speaker),
            "pron":check_pronoun(speaker),
            "ner":check_NER(speaker),
            "jobs":check_job(speaker)
            }
        try:
            m = mean([ind for ind in indices_list.values() if ind is not None])
            if m > 0.7:
                gender = "male"
            elif m < 0.3:
                gender = "female"
            else:
                gender = "unknown"
            return gender
        except:
            return "unknown"

def genderize_quotes(quotes):
    new_quotes = []
    for q in quotes:
        g = get_gender(q["speaker"])
        q["speaker_gender"] = g
        new_quotes.append(q)
    return new_quotes
