# The Gender Gap Tracker -- French

## History

### Original version (V1)
* **file:** `quote_extractor_fr_V1.py`
* **origin:** Discourse Lab - Simon Fraser University
* **NLP:** _Spacy_ model

### LIG changes (V2)
* **file:** `quote_extractor_fr_V2.py`
* **origin:** Ange Richard from GETALP Team - LIG, Université Grenoble-Alpes
* **NLP:** _Stanza_ model (https://stanfordnlp.github.io/stanza/)

**Significant changes from V1:**
* NLP library changed to Stanza Pipeline
* Extended speech verbs list
* Mixed quotes handling
* Syntactic method: extended dependency relation match
* Reversed method: added matching method
* Selon method: added matching method
* Removed speaker match with noun chunks

## Other components
**Genderization process:**
* **file:** `genderization.py`
* **use:** Estimate speaker's gender

**Gender statistics:**
* **file:** `gender_stats.py`
* **use:** Calculate proportion of speakers by gender (women, men and unknown)


---

## Setup
Clone this repo to your desktop and run `pip3 install -r requirements.txt` to install all the dependencies.

Beware that stanza dependencies weights more that 700MB. You must also download the french model by doing this:

```
python3

>>> import stanza
>>> stanza.download('fr')
>>> exit()

```

This will download the french stanza model (about 600MB).

---

## Usage

### To run the quote extractor + genderization of speakers

```
python3 ./french_pipeline/quote_extractor_fr_V2.py --file-path ./sample.txt

``` 

The output will be found in the directory `./output/` (or in the given directory if the output-dir argument is provided), in which a file named `sample.json` will be created, containing the extracted quotes in the following format:

```
{
        "speaker": "la directrice de l'agence",
        "speaker_index": "(599, 624)",
        "quote": "L'acteur aurait touché trois fois plus que sa co-star pour le tournage du film,",
        "quote_index": "(513,592)",
        "verb": "",
        "verb_index": "",
        "quote_token_count": 79,
        "quote_type": "selon",
        "is_floating_quote": false,
        "reference": "la directrice de l'agence",
        "speaker_gender": "female"
}
```


### To get the gender distribution statistics: 

```
python3 ./french_pipeline/gender_stats.py --file-path ./output/withgender/sample.json
```

The output will be found in the directory `./output/withgender/` (or given directory if the output-dir argument is provided), in which a file named `gender_statistics.json` will be created, containing the extracted statistics in the following form for each document (all processed documents in the same json file):

```
{
    "doc_id": "sample",
    "num_quotes": 9,
    "women_speakers": 1,
    "men_speakers": 5,
    "unknown_speakers": 3
}
```

---

## License

This project is licensed under the terms of the GNU General Public License v3.0 license.

The file `./french_pipeline/utils/occupations_clean.csv` is a database of 1610 French gendered job names, based on the official guide `Femme, j’écris ton nom... Guide d’aide à la féminisation des noms de métiers, titres, grades et fonctions` (Institut national de la langue française, 1999) (https://www.vie-publique.fr/rapport/25339-guide-daide-la-feminisation-des-noms-de-metiers)