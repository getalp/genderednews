"""
Simple example to extract an article when logged in.
Based on: https://linuxhint.com/logging_into_websites_python/
"""

import datetime as dt
import requests
from bs4 import BeautifulSoup

from gn_modules.scraping_and_extraction.collectors.le_monde import LeMonde


with requests.Session() as s:
    # Download and parse the login page
    site = s.get('https://secure.lemonde.fr/sfuser/connexion')
    bs_content = BeautifulSoup(site.content, 'html.parser')

    # Fill the username and password inputs and send
    token = bs_content.find('input', {'name': 'connection[_token]'})['value']
    login_data = {'connection[mail]': 'your_login',
                  'connection[password]': 'your_password', 'connection[_token]': token}
    s.post('https://secure.lemonde.fr/sfuser/connexion', login_data)

    # Get the content of a free article while logged in
    FREE_LINK = 'https://www.lemonde.fr/les-decodeurs/article/2019/07/02/precarite-menstruelle-combien-coutent-ses-regles-dans-la-vie-d-une-femme_5484140_4355770.html'
    free_article = LeMonde().create_article_from_link(
        FREE_LINK, date=dt.datetime.now(),  html=s.get(FREE_LINK).text)
    print('---------------------------------------------------------')
    print(f'{free_article.link}:\n\t{free_article.get_text()}')

    # Get the content of a premium article while logged in
    PREMIUM_LINK = 'https://www.lemonde.fr/planete/article/2021/02/23/la-justice-saisie-pour-faire-barrage-au-retour-des-neonicotinoides_6070945_3244.html'
    premium_article = LeMonde().create_article_from_link(
        PREMIUM_LINK, date=dt.datetime.now(), html=s.get(PREMIUM_LINK).text)
    print('---------------------------------------------------------')
    print(f'{premium_article.link}:\n\t{premium_article.get_text()}')
