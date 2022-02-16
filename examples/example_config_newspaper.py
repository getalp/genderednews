"""
Short example that shows how to use a configuration with newspaper.
"""

import feedparser
import newspaper

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
config = newspaper.Config()
config.browser_user_agent = USER_AGENT


def process_article(link):
    """"From a given link, download and parse the article."""
    article = newspaper.Article(link, config=config, language='fr')
    article.download()
    article.parse()
    print(f'{article.url}: {article.title}')
    return article


news_feed = feedparser.parse('https://www.lemonde.fr/rss/en_continu.xml')
links = []

for entry in news_feed.entries:
    links.append(entry.link)

for link in links:
    process_article(link)
