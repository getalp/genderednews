"""
Twitter bot
"""
# twitter account: @genderednews

import os
import datetime as dt
import requests
import tweepy
import pandas as pd

import gn_modules.secure_dotenv as gn_dotenv
from gn_modules.misc import initialize_logger

logger = initialize_logger(
    'genderednews', filename=f'logs/twitter_bot.log', terminal=True)


def create_api():
    """Create an api with API key and access token"""

    gn_dotenv.load_dotenv_secure()
    api_key = os.environ.get('API_KEY')
    api_secret_key = os.environ.get('API_SECRET_KEY')
    access_token = os.environ.get('ACCESS_TOKEN')
    access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(api_key, api_secret_key)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except:
        logger.exception("Error during twitter authentication")

    return api


def make_tweet_mentions_masculinity_rate():
    """Make a tweet for masculinity rate of mentions"""

    last_week_day = dt.datetime.now() - dt.timedelta(days=7)
    start = last_week_day - dt.timedelta(days=last_week_day.weekday())
    end = start + dt.timedelta(days=6)
    start = start.strftime("%d/%m/%Y")
    end = end.strftime("%d/%m/%Y")

    url_masculinity_rate = 'https://gendered-news.imag.fr/metabase/api/public/card/776c928a-f9d1-47e9-9735-fd3623e9c946/query/json'
    response = requests.get(url_masculinity_rate)

    df = pd.DataFrame(response.json())
    df['Moyenne de Masculinity Rate'] = df['Moyenne de Masculinity Rate'].round(
        2)

    plot = df.plot.bar(
        x='Source Name', y='Moyenne de Masculinity Rate', rot=45, figsize=(10, 7),
        color=['#2f97e4', '#ffda57', '#62cc49',
               '#ff7d8c', '#79ded9', '#b67bc6', '#7767ae'],
        title='Taux de masculinité des mentions (' + start + ' - ' + end + ')')
    plot.get_legend().remove()
    plot.hlines(0.5, -0.5, 10, linestyles='dashed', color='grey')
    for p in plot.patches:
        plot.annotate(str(p.get_height()),
                      (p.get_x() + 0.1, p.get_height() * 1.005))

    fig = plot.get_figure()
    fig.savefig('logs/tweet_mentions.png')

    message = "Taux de masculinité des mentions de la semaine écoulée:"

    return message


def make_tweet_quotes_part_of_men():
    """Make a tweet for percentage of men quoted"""

    last_week_day = dt.datetime.now() - dt.timedelta(days=7)
    start = last_week_day - dt.timedelta(days=last_week_day.weekday())
    end = start + dt.timedelta(days=6)
    start = start.strftime("%d/%m/%Y")
    end = end.strftime("%d/%m/%Y")

    url_masculinity_rate = 'https://gendered-news.imag.fr/metabase/api/public/card/ee9f35fe-9e3c-4619-afd2-ac7779a62753/query/json'
    response = requests.get(url_masculinity_rate)

    df = pd.DataFrame(response.json())
    df['Part Homme'] = df['Part Homme'].round(
        2)

    plot = df.plot.bar(
        x='Source', y='Part Homme', rot=45, figsize=(10, 7), color=['#2f97e4', '#ffda57', '#62cc49', '#ff7d8c', '#79ded9', '#b67bc6', '#7767ae'],
        title='Part des hommes dans les citations (' + start + ' - ' + end + ')')
    plot.get_legend().remove()
    plot.hlines(0.5, -0.5, 10, linestyles='dashed', color='grey')
    for p in plot.patches:
        plot.annotate(str(p.get_height()),
                      (p.get_x() + 0.1, p.get_height() * 1.005))

    fig = plot.get_figure()
    fig.savefig('logs/tweet_quotes.png')

    message = "Part des hommes dans les citations de la semaine écoulée:"

    return message


def upload_messages():
    """Upload messages on Twitter"""
    api = create_api()
    message_mentions = make_tweet_mentions_masculinity_rate()
    message_quotes = make_tweet_quotes_part_of_men()

    api.update_with_media('logs/tweet_mentions.png', message_mentions)
    api.update_with_media('logs/tweet_quotes.png', message_quotes)


try:
    upload_messages()
    logger.info("messages successfully uploaded")
except:
    logger.exception("failed to upload the messages")
