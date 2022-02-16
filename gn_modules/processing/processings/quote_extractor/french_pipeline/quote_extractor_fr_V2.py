# French quote extractor script, as changed by Ange Richard from LIG Lab (Université Grenoble-Alpes)
# See comments within the code and Readme for changes from Discourse Lab (SFU) version

import getopt

import json
import logging
import os
import sys
import traceback

from statistics import mean

import re

import stanza
from stanza.models.common.doc import Token

import gn_modules.processing.processings.quote_extractor.french_pipeline.genderization as gen

START_GUILLEMETS = set()
END_GUILLEMETS = set()

if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(filename='logs/quote-extractor.log', format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

"""

selon PERSON
d'après PERSON

argue: faire valoir
argued: a fait valoir, ont fait valoir
argues: fait valoir, font valoir
faire remarquer, (a; ont) fait remarquer; (fait; font) remarquer

laisser tomber, (a; ont) laissé tomber, laisse(nt) tomber

se questionner, (s'est; se sont) questionné(e; s; es), questionne(nt)
s'exprimer, (s'est, se sont) exprimé(e; s; es), s'exprime(nt)
se désoler, (s'est; se sont) désolé(e; s; es), se désole(nt)
se consoler, (s'est; se sont) consolé(e; s; es), se console(nt)
se lamenter, (s'est; se sont) lamenté(e; s; es), se lamente(nt)
s'interroger, (s'est; se sont) interrogé(e; s; es); s'interroge(nt)

"""

quoteVerbWhiteList = ['reconnaitre', 'ajouter', 'admettre', 'annoncer', 'prétendre', 'soutenir',
                      'conclure', 'confirmer', 'déclarer', 'décrire', 'assurer', 'expliquer', 'trouver',
                      'indiquer', 'informer', 'insister', 'noter', 'souligner', 'prédire', 'fournir',
                      'divulger', 'rappeler', 'répondre', 'dire', 'rapporter', 'répondre', 'affirmer',
                      'suggérer', 'attester', 'penser', 'gazouiller', 'tweeter', 'avertir', 'écrire'] + [
                      'révéler', 'commenter', 'avouer', 'raconter', 'prévenir', 'prédire', 'redouter',
                      'soulever', 'préciser', 'résumer', 'juger', 'estimer', 'dancer', 'lancer', 
                      'nuancer', 'relever', 'constater', 'réclamer', 'remarquer', 'confier', 'observer',
                      'réagir', 'concéder', 'témoigner', 'louanger', 'demander', 'arguer', 'protester',
                      'critiquer', 'plaider', 'poursuivre', 'trancher', 'mentionner', 'souhaiter'] + [
                      'proposer','rétorquer','marmoner','soupirer','murmurer','énoncer','exposer',
                      'exprimer','avancer','marteler','proférer','insinuer','objecter', 'déplorer','inviter', 'prêcher','défendre', 'lire', 'plaindre','recommander', 'réjouir','reconnaître','reprocher']
#Added verbs. Ambiguous verbs: ["poursuivre","juger","avouer","reconnaître", "montrer"].
#Removed "croire" because it matched mostly wrong quotes

nlp = stanza.Pipeline('fr',use_gpu=False)

# ----- Formatting Functions
def get_str(subtree, doc):
    """Gets the string corresponding to the subtree span 
    by matching the starting and end characters in the doc text"""
    docstr = doc.text
    span = get_pretty_index(subtree)
    txt = docstr[int(span[0]):int(span[1])].strip()
    txt = txt.strip(".")
    txt = txt.strip("\n")
    txt = txt.strip("-")
    txt = txt.strip(",")
    return txt.strip()

def get_pretty_index(key):
    if isinstance(key, list): #if key is a list of Tokens
        start_char = key[0].start_char
        end_char = key[-1].end_char
        return (start_char, end_char)
    elif isinstance(key, stanza.models.common.doc.Token): #if key is Token
            start_char = key.start_char
            end_char = key.end_char
            return (start_char, end_char)


def get_children(sent=None, head=None, children_list=[]):
    """ Returns the sorted dependencies subtree (a list of Tokens (Stanza type))
    with root as the given arg HEAD
    Head is a TOKEN
    Children_list is list of TOKENS
    """
    if head not in children_list:
      children_list.append(head)
    for tok in sent.tokens:
      if len(tok.words) == 1:
        if tok.words[0].head in head.id:
          get_children(sent,tok,children_list)
      elif len(tok.words) > 1: #If token is composed of several words:
        heads = set([w.head for w in tok.words if w.head not in tok.id])
        ids = set(head.id)
        if len(ids.intersection(heads)) > 0 and tok not in children_list:
          get_children(sent,tok,children_list)
      else:
        pass
    #removing unwanted punctuation at the start of the tree
    try:
      for i in range(0,len(children_list)-1):
        while children_list[i].text in [".",",",":","?","!",";",")"]:
          del children_list[i]
      return sorted(children_list, key=lambda x: x.id)
    except IndexError:
        return sorted(children_list, key=lambda x: x.id)

def prune_speaker_subtree(speaker_subtree):
  """ Removes possible "-t" from speaker subtrees
  """
  if re.search("^-",speaker_subtree[0].text) is not None and speaker_subtree[0].words[0].upos == "PART":
    return speaker_subtree[1:]
  else:
    return speaker_subtree

  
# ----- Other
def preprocess_text(txt):
    txt = txt.replace(u'\xa0', u' ')

    #fix problem of full stop inside quotes
    txt = re.sub("\.( )*»\.?",r"».", txt)

    # To fix the problem of not breaking at \n
    #txt = txt.replace("\n", ".\n ")
    # To remove potential duplicate dots
    txt = txt.replace("..\n ", ".\n ")
    txt = txt.replace(". .\n ", ".\n ")
    txt = txt.replace("  ", " ")
    # Replace double quotes
    txt = txt.replace("”",'"')
    txt = txt.replace("“",'"')
    # ---
    txt = txt.replace("〝",'"')
    txt = txt.replace("〞",'"')
    # Replace single quotes
    #txt = txt.replace("‘","'")
    #txt = txt.replace("’",''')
    # fix problem of spaces around quote signs
    txt = re.sub("( )+»","»", txt)
    txt = re.sub("«( )+","«", txt)
    # Note positions of all start and end guillemets
    # NOTE: This assumes that all quotes use the « » quotation marks which is far from being always the case
    for match in re.finditer('«', txt):
        START_GUILLEMETS.add(match.start())
    for match in re.finditer('»', txt):
        END_GUILLEMETS.add(match.end())
    
    # Replace guillemets
    txt = txt.replace("«",'"')
    txt = txt.replace("»",'"')
    return txt

# ----- Helper functions

def seenBefore(regex_match, quote_objects):
    quotations = set([eval(quote_obj['quote_index']) for quote_obj in quote_objects])
    
    for q in quotations:
        if fuzzy_match((regex_match.start(),regex_match.end()), (int(q[0]), int(q[1]))):
            # It's a match, so disregard it
            return True
    return False

def fuzzy_match(indx1, indx2):
    """ Same fuzzy_match as the evaluation script so that
    it can handle mixed quotes matched at the regex stages"""
    indx1_set = set(range(indx1[0], indx1[1]))
    indx2_set = set(range(indx2[0], indx2[1]))
    score = len(indx1_set.intersection(indx2_set)) / len(indx1_set.union(indx2_set))
    return score > 0.3

def getSentenceNumber(sentence_dict, char):
    keys_subset = [k for k in sentence_dict.keys() if k <= char]
    assert len(keys_subset) > 0
    sentence_char = max(keys_subset)
    return sentence_dict[sentence_char]

def getClosestPreceding(preceding_dict, char):
    keys_subset = [k for k in preceding_dict.keys() if k <= char]
    if len(keys_subset) > 0:
        return max(keys_subset)
    else:
        return -1

def getClosestFollowing(following_dict, char):
    keys_subset = [k for k in following_dict.keys() if k >= char]
    if len(keys_subset) > 0:
        return min(keys_subset)
    else:
        return -1
    
def hasAlpha(text):
    for letter in text:
        if letter.isalpha():
            return True
    return False

def is_quote(char):
  if char in ['"']:
    return True
  else:
    return False

def get_quote_type(doc, quote, verb, speaker):
    dc1_pos = -1
    dc2_pos = -1
    quote_starts_with_quote = False
    quote_ends_with_quote = False
    docstr = doc.text
    quote_start = get_pretty_index(quote)[0]
    quote_end = get_pretty_index(quote)[1]
    speaker_start = get_pretty_index(speaker)[0]

    #check if char is quote for: 
    # 1st and last char of quote
    # char right before or after the quote
    # 2nd char at start or end of the quote
    is_quote_start = (
      is_quote(docstr[quote_start]) 
      or is_quote(docstr[max(0,quote_start -1)]) 
      or is_quote(docstr[quote_start +1])
      )
    if len(docstr) == quote_end:
      is_quote_end = is_quote(docstr[len(docstr)-1])
    else:
      is_quote_end = (
        is_quote(docstr[min(len(docstr)-1, quote_end+1)]) 
        or is_quote(docstr[quote_end]) 
        or is_quote(docstr[quote_end -1])
        )

    #quotes on both sides
    if is_quote_start and is_quote_end:
      quote_starts_with_quote = True
      quote_ends_with_quote = True
      dc1_pos = max(0, quote_start - 1)
      dc2_pos = quote_end + 1
    #onesided quote start
    elif is_quote_start and not is_quote_end:
      #if there is another quotation mark in the rest of the quote (i.e: if it's a mixed quote)
      if re.search('"', docstr[quote_start+2:quote_end]) is not None:
        quote_starts_with_quote = True
        quote_ends_with_quote = True
        dc1_pos = max(0, quote_start - 1)
        dc2_pos = mean([quote_start, quote_end])+1  #arbitrary decision to have letters in the right order
      else:
        quote_starts_with_quote = True
        quote_ends_with_quote = False
        dc1_pos = max(0, quote_start - 1)
    #onesided quote at the end (same process)
    elif is_quote_end and not is_quote_start:
      if re.search('"', docstr[quote_start:quote_end-2]) is not None:
        quote_starts_with_quote = True
        quote_ends_with_quote = True
        dc1_pos = mean([quote_start, quote_end])-1
        dc2_pos = quote_end + 1
      else:
        quote_starts_with_quote = False
        quote_ends_with_quote = True
        dc1_pos = quote_end + 1
    elif speaker_start < quote_start and is_quote(docstr[max(0, speaker_start-1)]) and is_quote_end:
      quote_starts_with_quote = True
      quote_ends_with_quote = True
      dc1_pos = max(0, speaker_start - 1)
      dc2_pos = quote_end + 1

    content_pos = mean([quote_start, quote_end])
    verb_pos = mean([get_pretty_index(verb.parent)[0], get_pretty_index(verb.parent)[1] + len(verb.text)])
    speaker_pos = mean([speaker_start, get_pretty_index(speaker)[1]])

    if quote_starts_with_quote and quote_ends_with_quote:
        letters = ["Q", "q", "C", "V", "S"]
        indices = [dc1_pos, dc2_pos, content_pos, verb_pos, speaker_pos]
    elif (quote_starts_with_quote and not quote_ends_with_quote) or (quote_ends_with_quote and not quote_starts_with_quote):
        letters = ["Q", "C", "V", "S"]
        indices = [dc1_pos, content_pos, verb_pos, speaker_pos]
    else:
        letters = ["C", "V", "S"]
        indices = [content_pos, verb_pos, speaker_pos]
    keydict = dict(zip(letters, indices))
    letters.sort(key=keydict.get)
    return "".join(letters).replace('q', 'Q')


########################## SYNTACTIC QUOTES ############################################
""" This section contains all functions that extract quotes with a SYNTACTIC method

The main function extract_syntactic_quotes first extracts all dependency relations tagged as either:
- parataxis (ex:< L'organisation est en très bonne voie, se réjouit la présidente >)
- ccomp (clausal complement) or xcomp (open clausal complement)
Then filter to only speech verbs with the quoteVerbsWhiteList (line 53).

This function handles direct, indirect and mixed quotes.

Examples of quotes extracted by Syntactic method:
Indirect quote: Le ministre des Finances a déclaré que le pays traversait une période difficile.
Direct quote: "Le président mesure bien les conséquences de ces affaires dans l'opinion publique", a affirmé la villepiniste Marie-Anne Montchamp.
Mixed quote: Nicolas Sarkozy a procédé à un "remaniement personnel", estiment les éditorialistes
"""

def extract_syntactic_quotes(doc):
  list_quotes = []
  checklist_q = []
  for sentence in doc.sentences:
    for word in sentence.words:
      #look at possible parataxis (as in: L'organisation est en très bonne voie, se réjouit la présidente  (without quotes))
      if word.upos == "VERB" and (word.lemma.lower() in quoteVerbWhiteList) and word.deprel.split(":")[0] == "parataxis":
        verb_ = word
        #get speaker
        for child in get_children(sentence,verb_.parent,[]):
          if "nsubj" in [w.deprel for w in child.words]:
            #Note: this matches subject + attributes (i.e: "Me Jean-Pascal Boucher, porte-parole et responsable des relations avec les médias au DPCP" and not just "Me Jean-Pascal Boucher", as what has been annotated)
            speaker_subtree = get_children(sentence,child,[])
            speaker = prune_speaker_subtree(speaker_subtree)
            if speaker != []:
                #get quote content
                for w_ in sentence.words:
                  if w_.id == verb_.head:
                    # A bit rough but works okay
                    subtree_span = [W for W in get_children(sentence,w_.parent,[]) if (W not in get_children(sentence,verb_.parent,[]) and not W.text == ".")]
                    quote_str = get_str(subtree_span,doc)

                    #extracting necessary info:
                    quote_token_count = len(subtree_span)
                    quote_type = get_quote_type(doc, subtree_span, verb_, speaker)
                    is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", get_str(speaker, doc).lower()) is None)
                    is_valid_type = (not quote_type.count("Q") == 1)  #removes one-sided quotes
                    is_valid_quote = len(quote_str) > 0
                    if is_valid_quote and is_valid_type and is_valid_speaker and quote_token_count > 3 and (quote_str not in checklist_q):

                      quote_obj = {
                      'speaker': get_str(speaker, doc),
                      'speaker_index': str(get_pretty_index(speaker)),
                      'quote': quote_str,
                      'quote_index': str(get_pretty_index(subtree_span)),
                      'verb': verb_.text,
                      'verb_index': str(get_pretty_index(verb_.parent)),
                      'quote_token_count': quote_token_count,
                      'quote_type': quote_type,
                      'is_floating_quote': False,
                      'reference': get_str(speaker,doc)
                      }
                      list_quotes.append(quote_obj)
                      checklist_q.append(quote_obj["quote"])
                      continue

      #Note: matching "obj" deprel increases a bit the recall but it lowers a lot the precision a lot
      if word.deprel.split(":")[0] in ['ccomp','xcomp']:
        subtree_span = get_children(sentence,word.parent,[])
        quote_str = get_str(subtree_span, doc)        
        # ---- extracting verb
        for w in sentence.words:
          if (w.id == word.head) and (w.upos == "VERB") and (w.lemma.lower() in quoteVerbWhiteList):
            verb = w
            # ---- extracting subject/speaker
            speaker = []
            for child in sentence.words:
              if (child.head == verb. id) and (child.deprel == "nsubj"):
                speaker_subtree = get_children(sentence,child.parent,[])
                speaker = prune_speaker_subtree(speaker_subtree)

                #extracting necessary info:
                quote_token_count = len(subtree_span)
                quote_type = get_quote_type(doc, subtree_span, verb, speaker) 
                is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", get_str(speaker, doc).lower()) is None)
                is_valid_type = (not quote_type.count("Q") == 1)  #removes one-sided quotes
                is_valid_quote = len(quote_str.strip()) > 0
                if is_valid_quote and is_valid_type and is_valid_speaker and (quote_token_count > 3) and (quote_str not in checklist_q):
                  
                  quote_obj = {
                  'speaker': get_str(speaker, doc),
                  'speaker_index': str(get_pretty_index(speaker)),
                  'quote': quote_str,
                  'quote_index': str(get_pretty_index(subtree_span)),
                  'verb': verb.text,
                  'verb_index': str(get_pretty_index(verb.parent)),
                  'quote_token_count': quote_token_count,
                  'quote_type': quote_type,
                  'is_floating_quote': False,
                  'reference': get_str(speaker,doc)
                  }
                  list_quotes.append(quote_obj)
                  checklist_q.append(quote_obj["quote"])
                  continue
                               
  return list_quotes

########################## REVERSED QUOTES ############################################
""" This section contains all functions that extract quotes with a REVERSED method (matching the quote first)

The main function extract_reversed_quotes first extracts direct quotes with a regular expression then either:
- finds a pair subject + verb inside the extracted quote (see example)
- Or matches as the speaker the closest Named Entity (Person) or pronoun in the text.

This function only handles direct quotes.

Examples of quotes extracted by the Reversed method:
- «Chez une certaine partie des libéraux, il y a presque une haine du Québec français, a réagi le bloquiste Mario Beaulieu. On sent que c'est viscéral.»
"""
def extract_reversed_quotes(doc, syntactic_quotes):
    checklist_q = []
    quote_list = []
        
    # Create a dictionary of sentences, sentence numbers, indexed by start character
    sentence_dict = {}
    for i,sent in enumerate(doc.sentences):
      sentence_dict[get_pretty_index(sent.tokens[0])[0]] = i,sent

    # Named entity preprocessing
    # Create a named entity dictionary by sentence
    named_people_dict = {}
    for ent in doc.ents:
        if ent.type == 'PER':
            named_people_dict[ent.start_char] = ent
    
        
    # Noun chunk search has been removed for several reasons:
    # It was mostly matching wrong noun chunks as speakers
    # and Stanza library doesn't have a module as easy to use as Spacy's for this
    
    pronoun_dict = {}
    for sent in doc.sentences:
      for word in sent.words:
        if word.pos == 'PRON':
          pronoun_dict[get_pretty_index(word.parent)[0]] = word.parent

    # Find list of quotes with quotation marks
    regex_quotes = []

    for match in re.finditer('(?<=")[^"]+(?=")', doc.text):
        # ignore quotes that don't start or end with the right kind of quote char
        if match.start()-1 not in START_GUILLEMETS:
            continue
        if match.end()+1 not in END_GUILLEMETS:
            continue
        if not seenBefore(match, syntactic_quotes):
            regex_quotes.append(match)
    
    for q in regex_quotes:
        # Find the sentence(s) of the extracted quotes (this handles quotes with a length of one or two sentences, but not longer ones)
        sentence_number, sentence_text = getSentenceNumber(sentence_dict,
                                               q.start())
        sentence_number_end, sentence_text_end = getSentenceNumber(sentence_dict,
                                                   q.end())
        sentence_span = [sentence_text,sentence_text_end]
        quote_token_count = len(q.group(0).split(' '))

        #First: try to find if inside the quote is included a pair [speech verb + nsubj] and assume it's the cue (it is often the case for long direct quotes)
        #Of course it is not perfect and sometimes the parser will annotate wrong nsubj for the verb but it works pretty well overall
        for sent in sentence_span:
          for w in sent.words:
            if (w.upos == "VERB") and (w.deprel in ["root","parataxis"]) and (w.lemma.lower() in quoteVerbWhiteList):
              verb = w
              for child in sentence_text.words:
                if (child.head == verb.id) and (child.deprel == "nsubj") and (q.group(0) not in checklist_q) and quote_token_count > 3:
                  speaker_subtree = get_children(sentence_text,child.parent,[])
                  speaker = prune_speaker_subtree(speaker_subtree)
                  is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", get_str(speaker, doc).lower()) is None)
                  if is_valid_speaker:
                    quote_obj = {
                        'speaker': get_str(speaker, doc),
                        'speaker_index': str(get_pretty_index(speaker)),
                        'quote': q.group(0),
                        'quote_index': '({0},{1})'.format(q.start()-1, q.end()+1),
                        'verb': verb.text,
                        'verb_index': str(get_pretty_index(verb.parent)),
                        'quote_token_count': quote_token_count,
                        'quote_type': 'QCQVS',
                        'is_floating_quote': False,
                        'reference': get_str(speaker,doc)
                    }
                    checklist_q.append(q.group(0))
                    quote_list.append(quote_obj)
                    continue
                

        # If not, find the closest named person following the sentence to link if possible
        closest_person_start_char = getClosestFollowing(named_people_dict,
                                                          q.end())
        closest_person_sentence_number_end = -1 
        if closest_person_start_char != -1:
            closest_person_sentence_number, _ = getSentenceNumber(sentence_dict,
                                                              closest_person_start_char)
            closest_person_sentence_number_end, _ = getSentenceNumber(sentence_dict,
                                                                      named_people_dict[closest_person_start_char].end_char)
        
            # Best case scenario: named person and the end of quote are in the same sentence
            if closest_person_sentence_number == sentence_number_end  and quote_token_count > 3 and (q.group(0) not in checklist_q):
                person = named_people_dict[closest_person_start_char]
                quote_obj = {
                    'speaker': person.text,
                    'speaker_index': '({0},{1})'.format(person.start_char, person.end_char),
                    'quote': q.group(0),
                    'quote_index': '({0},{1})'.format(q.start()-1, q.end()+1),
                    'verb': '',
                    'verb_index': '',
                    'quote_token_count': quote_token_count,
                    'quote_type': 'QCQVS',
                    'is_floating_quote': False,
                    'reference': person.text
                }
                quote_list.append(quote_obj)
                checklist_q.append(q.group(0))
                continue
        
        # Otherwise try to find a pronoun in the sentence
        closest_pronoun_start_char = getClosestFollowing(pronoun_dict,
                                                            q.end())
        
        if closest_pronoun_start_char != -1:
            closest_pronoun_sentence_number, _ = getSentenceNumber(sentence_dict,
                                                                      closest_pronoun_start_char)
            closest_pronoun_sentence_number_end, _ = getSentenceNumber(sentence_dict,
                                                                          get_pretty_index(pronoun_dict[closest_pronoun_start_char])[1])
        
        
            # Best case scenario: pronoun and the end of quote are in the same sentence
            if closest_pronoun_sentence_number == sentence_number_end  and quote_token_count > 3 and (q.group(0) not in checklist_q):
                pronoun = pronoun_dict[closest_pronoun_start_char]
                is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", pronoun.text.lower()) is None)
                if is_valid_speaker:
                  quote_obj = {
                      'speaker': pronoun.text,
                      'speaker_index': str(get_pretty_index(pronoun)),
                      'quote': q.group(0),
                      'quote_index': '({0},{1})'.format(q.start(), q.end()),
                      'verb': '',
                      'verb_index': '',
                      'quote_token_count': quote_token_count,
                      'quote_type': 'QCQVS',
                      'is_floating_quote': False,
                      'reference': ''
                  }
                  quote_list.append(quote_obj)
                  checklist_q.append(q.group(0))
                  continue
    # Otherwise, leave it for floating quote stage
    return quote_list

########################## FLOATING QUOTES ############################################
""" This section contains all functions that extract quotes of the FLOATING kind (quotes without any direct cue or speaker)

The main function extract_floating_quotes first extracts direct quotes with a regular expression then matches the closest known speaker (of the closest quote that has already been extracted)

This function only handles direct quotes.

Examples of quotes extracted by the floating method:
TODO
"""

def extract_floating_quotes(doc, quotations):
    floating_quotes = []
    checklist_q = []
    regex_quotes = []
    for match in re.finditer('(?<=")[^"]+(?=")', doc.text):
        # ignore quotes that don't start or end with the right kind of quote char
        if match.start()-1 not in START_GUILLEMETS:
            continue
        if match.end()+1 not in END_GUILLEMETS:
            continue

        if not seenBefore(match, quotations):
            regex_quotes.append(match)
    
    # Create a dictionary of sentences, sentence numbers, indexed by start character
    sentence_dict = {}
    for i,sent in enumerate(doc.sentences):
      sentence_dict[get_pretty_index(sent.tokens[0])[0]] = i,sent
        
    # Create a dictionary of quotes, indexed by final character
    quotation_dict = {}
    for quotation in quotations:
        indices = []
        for index in ['quote_index', 'verb_index', 'speaker_index']:
            if len(quotation[index]) > 0:
                indices.append(eval(quotation[index])[1])

        quotation_dict[max(indices)] = quotation['speaker']
    
    for q in regex_quotes:
        #Note: This assumes that the speaker has been *quoted* before, which is not always the case
        previous_quotation_index = getClosestPreceding(quotation_dict, q.start())
        try:
          assert previous_quotation_index < q.start()
        except AssertionError:
          pass
        
        if previous_quotation_index != -1:
            candidate_speaker = quotation_dict[previous_quotation_index]     
            between_span = doc.text[previous_quotation_index:q.start()]
            assert between_span is not None
            if not hasAlpha(between_span) and q.group(0) not in checklist_q: # and len(between_span) > 3
                try:
                    span = q.group(0)
                    quote_token_count = len(span)
                except TypeError:
                    print(q.start(), q.end())
                is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", candidate_speaker.lower()) is None)
                if quote_token_count > 3 and is_valid_speaker:
                      quote_obj = {
                          'speaker': '',
                          'speaker_index': '',
                          'quote': span,
                          'quote_index': '({0},{1})'.format(q.start()-1, q.end()+1),
                          'verb': '',
                          'verb_index': '',
                          'quote_token_count': quote_token_count,
                          'quote_type': 'QCQ',
                          'is_floating_quote': True,
                          'reference': candidate_speaker
                      }
                      floating_quotes.append(quote_obj)
                      checklist_q.append(span)

    return floating_quotes

########################## SELON QUOTES ############################################
""" This section contains all functions that extract quotes introduced by SELON or D'APRES

The main function extract_selon_quotes first extracts sentences containing "selon" or "d'après" with a regular expression then either:
- matches the speaker as the tagged head of the token "selon" in the extracted sentence
- matches the speaker as the closest Named Entity (PER) or pronoun in the text

This function handles both direct and indirect quotes.

Examples of quotes extracted by the selon method:
TODO
"""

def stripWithIndices(string, start_index, end_index):
    _string = ''
    for i,letter in enumerate(string):
        if letter.isspace():
            continue
        _string = string[i:]
        start_index = start_index + i
        break
        
    for i,letter in enumerate(reversed(_string)):
        if letter.isspace():
            continue
        string = _string[:len(_string) - i]
        end_index = end_index - i
        break
        
    return string, start_index, end_index


def extract_selon_quotes(doc, previous_quotes):
    quote_list = []
    checklist_q = []
        
     # Create a dictionary of sentences, sentence numbers, indexed by start character
    sentence_dict = {}
    for i,sent in enumerate(doc.sentences):
      sentence_dict[get_pretty_index(sent.tokens[0])[0]] = i,sent

    # Named entity preprocessing
    # Create a named entity dictionary by sentence
    named_people_dict = {}
    for ent in doc.ents:
        if ent.type == 'PER':
            named_people_dict[ent.start_char] = ent
    
    # Noun chunk search has been removed for several reasons:
    # It was mostly matching wrong noun chunks as speakers
    # and Stanza library doesn't have a module as easy to use as Spacy's for this
    
    pronoun_dict = {}
    for sent in doc.sentences:
      for word in sent.words:
        if word.pos == 'PRON':
          pronoun_dict[get_pretty_index(word.parent)[0]] = word.parent

    
    # Find list of quotes
    selon_quotes = []
    for match in re.finditer("\s*([^\.\n]*([\s^](?:[sS]elon|[Dd]'après)\s)[^\.\n]*)\s*", doc.text):
        if not seenBefore(match, previous_quotes):
            selon_quotes.append(match)
    
    for q in selon_quotes:

        sentence_number, sentence_text = getSentenceNumber(sentence_dict,
                                               q.end())
        # Here, we're matching "selon" in the regex matches then looking for its head which would be the speaker (i.e: "selon le ministre")
        for w in sentence_text.words:
          if w.lemma.lower() in ["selon"]:
            cue = get_children(sentence_text,w.parent,[])
            for potential_head in sentence_text.words:
              if potential_head.id == w.head:
                # speaker match method is a bit rough but it works fine
                speaker_subtree = [W for W in get_children(sentence_text,potential_head.parent,[]) if (W not in cue and not W.text in [".",","])]
                speaker = get_str(speaker_subtree,doc)

                # Figuring out the quote_content
                beforeSelon = doc.text[q.start(1):q.start(2)]
                stripped, start_index, end_index = stripWithIndices(beforeSelon, q.start(1), q.start(2))
                if hasAlpha(stripped) and (stripped not in checklist_q):
                    quote_content = stripped
                    quote_content_start = start_index
                    quote_content_end = end_index
                                
                    span = doc.text[quote_content_start: quote_content_end]
                    assert span is not None
                    quote_token_count = len(span)
                    is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", speaker.lower()) is None)
                    if quote_token_count > 3 and is_valid_speaker:
                        quote_obj = {
                            'speaker': speaker,
                            'speaker_index': str(get_pretty_index(speaker_subtree)),
                            'quote': quote_content,
                            'quote_index': '({0},{1})'.format(quote_content_start, quote_content_end),
                            'verb': '',
                            'verb_index': '',
                            'quote_token_count': quote_token_count,
                            'quote_type': 'selon',
                            'is_floating_quote': False,
                            'reference': speaker
                        }
                        quote_list.append(quote_obj)
                        checklist_q.append(quote_obj["quote"])
                    continue

                afterSelon = doc.text[get_pretty_index(speaker_subtree)[1]:q.end(1)]
                stripped, start_index, end_index = stripWithIndices(afterSelon, get_pretty_index(speaker_subtree)[1], q.end(1))
                if hasAlpha(stripped) and (stripped not in checklist_q):
                    quote_content = afterSelon
                    quote_content_start = start_index
                    quote_content_end = end_index
                    
                    span = doc.text[quote_content_start: quote_content_end]
                    assert span is not None
                    quote_token_count = len(span)
                    is_valid_speaker = (re.search("(^|\b)((je|nous|moi)(\b|$)|j')", speaker.lower()) is None)
                    if quote_token_count > 3 and is_valid_speaker:
                        quote_obj = {
                            'speaker': speaker,
                            'speaker_index': str(get_pretty_index(speaker_subtree)),
                            'quote': quote_content,
                            'quote_index': '({0},{1})'.format(quote_content_start, quote_content_end),
                            'verb': '',
                            'verb_index': '',
                            'quote_token_count': quote_token_count,
                            'quote_type': 'selon',
                            'is_floating_quote': False,
                            'reference': speaker
                        }
                        checklist_q.append(quote_obj["quote"])
                        quote_list.append(quote_obj)
                        continue


        #Otherwise:  Find the closest named person following the sentence to link if possible
        closest_person_start_char = getClosestFollowing(named_people_dict,
                                                        q.start())
        # Find a pronoun in the sentence
        closest_pronoun_start_char = getClosestFollowing(pronoun_dict,
                                                            q.start())
        
        if closest_person_start_char != -1:
            person = named_people_dict[closest_person_start_char]
        elif closest_person_start_char != -1:
            person = pronoun_dict[closest_pronoun_start_char]
        else:
            continue
        # Figuring out the quote_content
        beforeSelon = doc.text[q.start(1):q.start(2)]
        stripped, start_index, end_index = stripWithIndices(beforeSelon, q.start(1), q.start(2))
        if hasAlpha(stripped) and (stripped not in checklist_q):
            quote_content = stripped
            quote_content_start = start_index
            quote_content_end = end_index

            span = doc.text[quote_content_start: quote_content_end]
            assert span is not None
            quote_token_count = len(span)
            if quote_token_count >3:
                quote_obj = {
                    'speaker': person.text,
                    'speaker_index': '({0},{1})'.format(person.start_char, person.end_char),
                    'quote': quote_content,
                    'quote_index': '({0},{1})'.format(quote_content_start, quote_content_end),
                    'verb': '',
                    'verb_index': '',
                    'quote_token_count': quote_token_count,
                    'quote_type': 'selon',
                    'is_floating_quote': False,
                    'reference': person.text
                }
                checklist_q.append(quote_obj["quote"])
                quote_list.append(quote_obj)
                continue
            
        afterSelon = doc.text[person.end_char:q.end(1)]
        stripped, start_index, end_index = stripWithIndices(afterSelon, person.end_char, q.end(1))
        if hasAlpha(stripped) and (stripped not in checklist_q):
            quote_content = afterSelon
            quote_content_start = start_index
            quote_content_end = end_index
            
            span = doc.text[quote_content_start: quote_content_end]
            assert span is not None
            quote_token_count = len(span)
            if quote_token_count >3:
                quote_obj = {
                    'speaker': person.text,
                    'speaker_index': '({0},{1})'.format(person.start_char, person.end_char),
                    'quote': quote_content,
                    'quote_index': '({0},{1})'.format(quote_content_start, quote_content_end),
                    'verb': '',
                    'verb_index': '',
                    'quote_token_count': quote_token_count,
                    'quote_type': 'QCQVS',
                    'is_floating_quote': False,
                    'reference': person.text
                }
                checklist_q.append(quote_obj["quote"])
                quote_list.append(quote_obj)
                continue
        
        # Otherwise leave it for the floating quote stage
    
    return quote_list

# ----- Quotation Extraction Functions
def extract_quotes(doc):
    syntactic_quotes = extract_syntactic_quotes(doc)
    reversed_quotes = extract_reversed_quotes(doc, syntactic_quotes)
    selon_quotes = extract_selon_quotes(doc, syntactic_quotes + reversed_quotes)
    floating_quotes = extract_floating_quotes(doc, syntactic_quotes + reversed_quotes + selon_quotes)
    #the one-sided quote stage has been removed: it was not matching anything, and now the cases where the cue + speaker is included inside the quote are handled at the reversed quote stage

    return syntactic_quotes + reversed_quotes + selon_quotes + floating_quotes

def quote_extractor_pipeline(doc):
    """main function to call to extract quotes and guess the speaker's gender"""
    doc_text = preprocess_text(doc)
    nlped_doc = nlp(doc_text)
    quotes = extract_quotes(doc=nlped_doc)
    gendered_quotes = gen.genderize_quotes(quotes=quotes)
    return gendered_quotes

if __name__ == '__main__':

    file_path = None
    folder_path = None
    OUTPUT_DIRECTORY = './output'

    # sample_command = "quote_extractor.py -u username -p password -s server [-f | --skip-human-readable | write-quote-trees-in-file]"
    man_filepath = "--file-path Run quote extractor on $file"
    man_folderpath = "--folder-path Run quote extractor on several files contained in $folder"
    man_outputdir = "--output-dir Save quote files to output path"
    sample_command = __file__ + " --file-path ./sample.txt"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:p:s:f",
                                   ["file-path=", "folder-path=", "output-dir="
                                    ])
    except getopt.GetoptError:
        print("Please enter a valid command. Use -h for accepted arguments.")
        sys.exit(2)

    #  Parse input paremeters
    for opt, arg in opts:
        print("### ", opt, " | ", arg)
        if opt in ['-h', '--help']:
            print("\nLOCAL USE ARGUMENTS:")
            print(man_filepath + "\n" + man_folderpath + "\n" + man_outputdir)
            print("\nSAMPLE COMMAND:")
            print(sample_command)
            sys.exit()
        elif opt in ("--file-path"):
            file_path = arg
        elif opt in ("--folder-path"):
            folder_path = arg
        elif opt in ("--output-dir"):
            OUTPUT_DIRECTORY = arg

    # Create output directory for quote trees if necessary
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

    # Parse input files from folder
    if folder_path is not None:
        files = [folder_path + '/' + f for f in os.listdir(folder_path) if f.endswith('.txt')]

        for file in files:
            head, file_name = os.path.split(file)
            dot_index = file_name.find('.txt')
            file_name = file_name[:dot_index]

            try:
                doc_text = open(file, 'r').read()
                doc_text = preprocess_text(doc_text)
                quotes = quote_extractor_pipeline(doc=doc_text)
                with open(os.path.join(OUTPUT_DIRECTORY, file_name + '.json'), 'w', encoding='utf-8') as fo:
                    json.dump(quotes, fo, indent=4, ensure_ascii=False)
            except:
                print('EXCEPTION', file_name)
                logging.exception("message")
                traceback.print_exc()
        sys.exit(0)

    # Parse input file
    if file_path is not None:
        head, file_name = os.path.split(file_path)
        dot_index = file_name.find('.')
        file_name = file_name[:dot_index]
        try:
            doc_text = open(file_path, 'r').read()
            doc_text = preprocess_text(doc_text)
            quotes = quote_extractor_pipeline(doc=doc_text)

            with open(os.path.join(OUTPUT_DIRECTORY, file_name + '.json'), 'w', encoding='utf-8') as fo:
                json.dump(quotes, fo, indent=4, ensure_ascii=False)

            for q in quotes:
                print(q)
                print('-' * 50)
        except:
            print('EXCEPTION')
            logging.exception("message")
            traceback.print_exc()
        sys.exit(0)
