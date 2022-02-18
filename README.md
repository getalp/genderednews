# GenderedNews - gender bias dashboard

GenderedNews is a dashboard of gender biases in French news created with Python, MongoDB and Metabase. **Check out [the website]()!**

## Getting Started

### Setup

To setup this project, please refer to the [initial setup](https://github.com/getalp/genderednews/wiki/Initial-setup) guide.

### Usage (simple)

Here is how to use the examples the simplest way:

```bash
# Fill the database with fake article data
python3 examples/example_fake_data.py

# Fill the database with yesterday articles from Le Monde
python3 examples/example_rss_extract_store.py
```

To see the results you can setup a Metabase dashboard connected to the database.

### Usage (with cron job)

Here is how to setup a daily cron job at 01:00 (change `script.py` to the the desired script):

```bash
# Open the cron config file
crontab -e

# Add the following line in the config file:
0 1 * * * cd /path/to/genderednews/ && /path/to/genderednews/env/bin/python3 /path/to/genderednews/main_local.py

# See the cron config file
crontab -l
```

This is based on the following folder structure (non exhaustive):

```text
~/
└── genderednews/
    ├── current -> versions/2021-XX-XX
    ├── versions/
    │   ├── 2020-XX-XX/
    │   |   └── script.py
    │   └── 2021-XX-XX/
    │       └── script.py
    ├── shared/
    └── logs/
```

### Usage (script main_local.py)

In step 1, there are 2 methods for scraping articles links, one is via rss feeds and the other is via twitter.

```python
# if you want to scrape via rss feeds
collector = collector(scraping_mode = 'rss')
# if you want to scrape via twitter
collector = collector(scraping_mode = 'twitter')
```

The step 3 will check if there is any articles with missing process. If the parameter 'fix' is set on 'True', all articles with missing process will be processed again and updated in the database.


## Built with

A list of the main technologies used within the project (see [`requirements.txt`](https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews/-/blob/master/requirements.txt) for full dependency list):

* Main tools:
  * [Metabase](https://www.metabase.com/) v0.40.5 - Dashboard
  * [MongoDB](https://www.mongodb.com/) v4.4 - Database
  * [Python](https://www.python.org/) v3.8.5 - Main language
* Main libraries:
  * [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) v4.9.3 - Parse HTML
  * [Dotenv](https://saurabh-kumar.com/python-dotenv/) v0.15.0 - For .env files
  * [Faker](https://faker.readthedocs.io/) v8.1.2 - Generate fake data
  * [Feedparser](https://pythonhosted.org/feedparser/) v6.0.2 - Parse RSS feeds
  * [Newspaper3k](https://newspaper.readthedocs.io/) v0.2.8 - Parse articles
  * [PyMongo](https://pymongo.readthedocs.io/) v3.11.3 - Database driver for Python
  * [Tweepy](https://docs.tweepy.org/en/stable/) v3.10.0 - Connect, parse tweets via twitter api
* Others:
  * [PEP8](https://www.python.org/dev/peps/pep-0008/) v1.7.1 - Formatting
  * [PyLint](https://www.pylint.org/) v2.7.1 - Linting
  * [Sshtunnel](https://github.com/pahaz/sshtunnel/) v0.4.0 - Connect via ssh

## Improvements

- The Quotation Extraction model of this project will soon be replaced from a rule-based system to a ML model!

## Data

The data was downloaded from public websites of newspapers only for non-commercial and research purposes.

List of news sources:

- Aujourd’hui en France (édition nationale du Parisien) : https://www.leparisien.fr/
- La Croix : https://www.la-croix.com/
- Le Figaro : https://www.lefigaro.fr/
- Le Monde : https://www.lemonde.fr/
- Libération : https://www.liberation.fr/
- L'Équipe : https://www.lequipe.fr/
- Les Échos: https://www.lesechos.fr/

Mentions/Quotes

The data will permit to calculate the masculinity rates in mentions and quotes which will be represented by graphs on our [website](https://gendered-news.imag.fr/).

## Similar projects

The Canadian project [GenderGapTracker](https://gendergaptracker.informedopinions.org/) ([source](https://github.com/sfu-discourse-lab/GenderGapTracker/)) has the same goal but for Canadian news.


## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [`LICENSE`](https://github.com/getalp/genderednews/blob/main/LICENSE) file for details.

## Contact

For more information about the research methodology and for questions regarding collaboration, please contact: francois.portet@imag.fr, gilles.bastin@iepg.fr or ange.richard@univ-grenoble-alpes.fr
