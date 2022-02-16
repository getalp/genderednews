"""
Script for metabase queries: updating graphs, data table,...
"""

import os
import datetime as dt
import json
import pymongo as pm
from gn_modules.misc import initialize_logger
from gn_modules.secure_dotenv import load_dotenv_secure


logger = initialize_logger(
    'genderednews', filename=f'logs/metabase_queries.log', terminal=True)


# init variables
load_dotenv_secure()

CLIENT = pm.MongoClient(os.getenv('DB_ADDR'),
                        int(os.getenv('DB_PORT')))

ARTICLES_COLLECTION = CLIENT[os.getenv(
    'DB_NAME')][os.getenv('DB_ARTICLE_COLLECTION')]

OVERTIME_MENTIONS_COL = CLIENT[os.getenv(
    'DB_GRAPHS_NAME')]['overtime_mentions']

HOMO_CAT_MENTIONS_COL = CLIENT[os.getenv(
    'DB_GRAPHS_NAME')]['homo_cat_mentions']

AVG_WEEK_MENTIONS_COL = CLIENT[os.getenv(
    'DB_GRAPHS_NAME')]['avg_week_mentions']

OVERTIME_QUOTES_COL = CLIENT[os.getenv(
    'DB_GRAPHS_NAME')]['overtime_quotes']

HOMO_CAT_QUOTES_COL = CLIENT[os.getenv(
    'DB_GRAPHS_NAME')]['homo_cat_quotes']

AVG_WEEK_QUOTES_COL = CLIENT[os.getenv(
    'DB_GRAPHS_NAME')]['avg_week_quotes']


ART_OF_WEEK_COL = CLIENT[os.getenv('DB_GRAPHS_NAME')]['articles_of_the_week']


def update_overtime_mentions_graph():
    """update changes overtime in masculinity rates in mentions graph"""
    overtime_mentions_query = [
        {"$match": {"$and": [
            {"$expr": {"$ne": [
                "$processings.masculinity_rate_and_names.indicators.masculinity_rate", None]}},
            {"$and": [
                {"$expr": {"$gte": [
                    "$processings.masculinity_rate_and_names.indicators.masculinity_rate", 0]}},
                {"$expr": {"$lte": ["$processings.masculinity_rate_and_names.indicators.masculinity_rate", 1]}}]},
            {"$expr": {"$ne": ["$source_name", "Huffington Post"]}},
            {"$expr": {"$ne": ["$source_name", "Mediapart"]}}]}},
        {"$group": {"_id": {"date~~~week": {"$let": {"vars": {"parts": {"$dateToParts": {"date": {"$subtract": ["$date", {"$multiply": [{"$subtract": [{"$let": {"vars": {"day_of_week": {"$mod": [{"$add": [{"$dayOfWeek": "$date"}, -1]}, 7]}}, "in": {"$cond": {"if": {"$eq": [
            "$$day_of_week", 0]}, "then":7, "else":"$$day_of_week"}}}}, 1]}, 86400000]}]}}}}, "in":{"$dateFromParts": {"year": "$$parts.year", "month": "$$parts.month", "day": "$$parts.day"}}}}, "source_name": "$source_name"}, "avg": {"$avg": "$processings.masculinity_rate_and_names.indicators.masculinity_rate"}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": False, "week": "$_id.date~~~week",
                      "source_name": "$_id.source_name", "masculinity_rate": "$avg"}},
        {"$sort": {"week": 1}}
    ]

    overtime_mentions_results = list(
        ARTICLES_COLLECTION.aggregate(overtime_mentions_query))
    OVERTIME_MENTIONS_COL.delete_many({})
    OVERTIME_MENTIONS_COL.insert_many(overtime_mentions_results)


def update_homogeneous_category_mentions_graph():
    """update masculinity rates by homogenous categories graph"""
    homo_cat_mentions_query = [
        {"$project": {"date": "$date", "title": "$title", "masculinity_rate": "$processings.masculinity_rate_and_names.indicators.masculinity_rate", "homogenous_categories": "$processings.homogenous_categories.indicators.main_category",
                      "date~~~day": {"$let": {"vars": {"column": "$date"}, "in": {"___date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$$column"}}}}}, "start": {"$subtract": [dt.datetime.now(), 604800000]}, "end":dt.datetime.now()}},
        {"$match": {"$and": [{"$expr": {"$gte": ["$date", "$start"]}}, {
            "$expr": {"$lte": ["$date", "$end"]}}]}},
        {"$match": {"$and": [{"homogenous_categories": {"$ne": None}}, {
            "homogenous_categories": {"$ne": ""}}, {"masculinity_rate": {"$gte": 0, "$lte": 1}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$group": {"_id": {"main_category": "$homogenous_categories"},
                    "avg": {"$avg": "$masculinity_rate"}}},
        {"$project": {"_id": False, "main_category": "$_id.main_category",
                      "masculinity_rate": "$avg"}},
        {"$sort": {"masculinity_rate": 1}}
    ]

    homo_cat_mentions_results = list(
        ARTICLES_COLLECTION.aggregate(homo_cat_mentions_query))

    HOMO_CAT_MENTIONS_COL.delete_many({})
    HOMO_CAT_MENTIONS_COL.insert_many(homo_cat_mentions_results)


def update_week_bias_mentions_graph():
    """update weekly bias in mentions graph"""
    week_bias_mentions_query = [
        {"$project": {"date": "$date", "processings": "$processings", "date~~~day": {"$let": {"vars": {"column": "$date"}, "in": {"___date": {
            "$dateToString": {"format": "%Y-%m-%d", "date": "$$column"}}}}}, "start": {"$subtract": [dt.datetime.now(), 604800000]}, "end":dt.datetime.now()}},
        {"$match": {"$and": [{"$expr": {"$gte": ["$date", "$start"]}}, {
            "$expr": {"$lte": ["$date", "$end"]}}]}},
        {"$match": {"$and": [{"$expr": {"$gte": ["$processings.masculinity_rate_and_names.indicators.masculinity_rate", 0]}}, {
            "$expr": {"$lte": ["$processings.masculinity_rate_and_names.indicators.masculinity_rate", 1]}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$group": {"_id": None, "avg": {
            "$avg": "$processings.masculinity_rate_and_names.indicators.masculinity_rate"}}},
        {"$project": {"_id": False, "avg": True}}
    ]

    week_bias_mentions_results = list(
        ARTICLES_COLLECTION.aggregate(week_bias_mentions_query))

    AVG_WEEK_MENTIONS_COL.delete_many({})
    AVG_WEEK_MENTIONS_COL.insert_many(week_bias_mentions_results)


def update_overtime_quotes_graph():
    """"""
    overtime_quotes_query = [
        {"$project": {"date": "$date", "source_name": "$source_name",
                      "processings": "$processings"}},
        {"$match": {
            "$expr": {"$ne": ["$processings.quotes.indicators", None]}}},
        {"$match": {"$or": [{"$expr": {"$gt": ["$processings.quotes.indicators.women_count", 0]}}, {
            "$expr": {"$gt": ["$processings.quotes.indicators.men_count", 0]}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$group": {"_id": {"date~~~week": {"$let": {"vars": {"parts": {"$dateToParts": {"date": {"$subtract": ["$date", {"$multiply": [{"$subtract": [{"$let": {"vars": {"day_of_week": {"$mod": [{"$add": [{"$dayOfWeek": "$date"}, -1]}, 7]}}, "in": {"$cond": {"if": {"$eq": ["$$day_of_week", 0]}, "then":7, "else":"$$day_of_week"}}}}, 1]}, 86400000]}]}}}}, "in":{
            "$dateFromParts": {"year": "$$parts.year", "month": "$$parts.month", "day": "$$parts.day"}}}}, "source_name": "$source_name"}, "total": {"$sum": {"$sum": ["$processings.quotes.indicators.women_count", "$processings.quotes.indicators.men_count"]}}, "men_count":{"$sum": "$processings.quotes.indicators.men_count"}}},
        {"$project": {"_id": False, "week": "$_id.date~~~week", "source": "$_id.source_name",
                      "part homme": {"$divide": ["$men_count", "$total"]}}},
        {"$sort": {"week": 1}}
    ]

    overtime_quotes_results = list(
        ARTICLES_COLLECTION.aggregate(overtime_quotes_query))

    OVERTIME_QUOTES_COL.delete_many({})
    OVERTIME_QUOTES_COL.insert_many(overtime_quotes_results)


def update_homogeneous_category_quotes_graph():
    """update histogram on the part of men by homogeneous categories"""
    homo_cat_quotes_query = [
        {"$project": {"date": "$date", "title": "$title", "processings": "$processings", "homogenous_categories": "$processings.homogenous_categories.indicators.main_category", "date~~~day": {"$let": {
            "vars": {"column": "$date"}, "in": {"___date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$$column"}}}}}, "start": {"$subtract": [dt.datetime.now(), 604800000]}, "end":dt.datetime.now()}},
        {"$match": {"$and": [{"$expr": {"$gte": ["$date", "$start"]}}, {
            "$expr": {"$lte": ["$date", "$end"]}}]}},
        {"$match": {
            "$expr": {"$ne": ["$processings.quotes.indicators", None]}}},
        {"$match": {"$or": [{"$expr": {"$gt": ["$processings.quotes.indicators.women_count", 0]}}, {
            "$expr": {"$gt": ["$processings.quotes.indicators.men_count", 0]}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$match": {"$and": [{"homogenous_categories": {"$ne": None}}, {
            "homogenous_categories": {"$ne": ""}}]}},
        {"$group": {"_id": {"category": "$processings.homogenous_categories.indicators.main_category"}, "total": {"$sum": {"$sum": [
            "$processings.quotes.indicators.women_count", "$processings.quotes.indicators.men_count"]}}, "men_count":{"$sum": "$processings.quotes.indicators.men_count"}}},
        {"$project": {"_id": False, "category": "$_id.category",
                      "part_homme": {"$divide": ["$men_count", "$total"]}}},
        {"$sort": {"part_homme": 1}}
    ]

    homo_cat_quotes_results = list(
        ARTICLES_COLLECTION.aggregate(homo_cat_quotes_query))

    HOMO_CAT_QUOTES_COL.delete_many({})
    HOMO_CAT_QUOTES_COL.insert_many(homo_cat_quotes_results)


def update_week_bias_quotes_graph():
    """update weekly bias in quotes graph"""
    week_bias_quotes_query = [
        {"$project": {"date": "$date", "processings": "$processings", "date~~~day": {"$let": {"vars": {"column": "$date"}, "in": {"___date": {
            "$dateToString": {"format": "%Y-%m-%d", "date": "$$column"}}}}}, "start": {"$subtract": [dt.datetime.now(), 604800000]}, "end": dt.datetime.now()}},
        {"$match": {"$and": [{"$expr": {"$gte": ["$date", "$start"]}}, {
            "$expr": {"$lte": ["$date", "$end"]}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$group": {"_id": None, "total": {"$sum": {"$sum": ["$processings.quotes.indicators.women_count", "$processings.quotes.indicators.men_count"]}}, "men_count":{
            "$sum": "$processings.quotes.indicators.men_count"}}},
        {"$project": {"_id": False, "part_homme": {
            "$divide": ["$men_count", "$total"]}}}
    ]

    week_bias_quotes_results = list(
        ARTICLES_COLLECTION.aggregate(week_bias_quotes_query))

    AVG_WEEK_QUOTES_COL.delete_many({})
    AVG_WEEK_QUOTES_COL.insert_many(week_bias_quotes_results)


def update_articles_of_the_week_table():
    """update articles of the week table"""
    art_of_week_query = [
        {"$project": {"date": "$date", "source_name": "$source_name", "title": "$title", "masculinity_rate": "$processings.masculinity_rate_and_names.indicators.masculinity_rate", "category": "$processings.homogenous_categories.indicators.main_category", "quotes": "$processings.quotes.indicators",
                      "word_count": "$word_count", "link": "$link", "date~~~day": {"$let": {"vars": {"column": "$date"}, "in": {"___date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$$column"}}}}}, "start": {"$subtract": [dt.datetime.now(), 604800000]}, "end":dt.datetime.now()}},
        {"$match": {"$and": [{"$expr": {"$gte": ["$date", "$start"]}}, {
            "$expr": {"$lt": ["$date", "$end"]}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$sort": {"date": -1}},
        {"$project": {"_id": False, "date": "$date", "source_name": "$source_name", "title": "$title", "masculinity_rate":
                      "$masculinity_rate", "quotes": "$quotes", "category": "$category", "word_count": "$word_count", "link": "$link"}},
        {"$project": {"date": {"$let": {"vars": {"column": "$date"}, "in": {"$dateToString": {"format": "%d-%m-%Y", "date": "$$column"}}}}, "source": "$source_name", "title": "$title", "mentions_masculinity_rate": "$masculinity_rate",
                      "Quotes-Women_count|Men_count": {"$concat": [{"$substr": ["$quotes.women_count", 0, 2]}, " | ", {"$substr": ["$quotes.men_count", 0, 2]}]}, "category":"$category", "word count":"$word_count", "link":"$link"}},
    ]

    art_of_week_results = list(
        ARTICLES_COLLECTION.aggregate(art_of_week_query))
    ART_OF_WEEK_COL.delete_many({})
    ART_OF_WEEK_COL.insert_many(art_of_week_results)


def update_data_mentions():
    """Update data file - metrics in mentions"""
    data_mentions_query = [
        {"$match": {"$and": [
            {"$expr": {"$ne": [
                "$processings.masculinity_rate_and_names.indicators.masculinity_rate", None]}},
            {"$and": [
                {"$expr": {"$gte": [
                    "$processings.masculinity_rate_and_names.indicators.masculinity_rate", 0]}},
                {"$expr": {"$lte": ["$processings.masculinity_rate_and_names.indicators.masculinity_rate", 1]}}]},
            {"$expr": {"$ne": ["$source_name", "Huffington Post"]}},
            {"$expr": {"$ne": ["$source_name", "Mediapart"]}}]}},
        {"$group": {"_id": {"date": {"$let": {"vars": {"parts": {"$dateToParts": {"date": "$date"}}}, "in": {"$dateFromParts": {"year": "$$parts.year", "month": "$$parts.month",
                                                                                                                                "day": "$$parts.day"}}}}, "source_name": "$source_name"}, "avg": {"$avg": "$processings.masculinity_rate_and_names.indicators.masculinity_rate"}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": False, "date": "$_id.date",
                      "source_name": "$_id.source_name", "masculinity_rate": "$avg"}},
        {"$sort": {"date": 1}}
    ]

    data_mentions_results = list(
        ARTICLES_COLLECTION.aggregate(data_mentions_query))

    with open('website/assets/data/data_mentions.json', 'w', encoding='utf-8') as f:
        json.dump(data_mentions_results, f,
                  ensure_ascii=False, indent=4, default=str)


def update_data_quotes():
    """Update data file - metrics in quotes"""
    data_quotes_query = [
        {"$project": {"date": "$date", "source_name": "$source_name",
                      "processings": "$processings"}},
        {"$match": {
            "$expr": {"$ne": ["$processings.quotes.indicators", None]}}},
        {"$match": {"$or": [{"$expr": {"$gt": ["$processings.quotes.indicators.women_count", 0]}}, {
            "$expr": {"$gt": ["$processings.quotes.indicators.men_count", 0]}}]}},
        {"$match": {"$and": [{"source_name": {"$ne": "Huffington Post"}}, {
            "source_name": {"$ne": "Mediapart"}}]}},
        {"$group": {"_id": {"date": {"$let": {"vars": {"parts": {"$dateToParts": {"date": "$date"}}}, "in": {"$dateFromParts": {"year": "$$parts.year", "month": "$$parts.month",
                                                                                                                                "day": "$$parts.day"}}}}, "source_name": "$source_name"}, "total": {"$sum": {"$sum": ["$processings.quotes.indicators.women_count", "$processings.quotes.indicators.men_count"]}}, "men_count":{"$sum": "$processings.quotes.indicators.men_count"}}},
        {"$project": {"_id": False, "date": "$_id.date", "source_name": "$_id.source_name",
                      "percentage_men": {"$divide": ["$men_count", "$total"]}}},
        {"$sort": {"date": 1}}
    ]

    data_quotes_results = list(
        ARTICLES_COLLECTION.aggregate(data_quotes_query))

    with open('website/assets/data/data_quotes.json', 'w', encoding='utf-8') as f:
        json.dump(data_quotes_results, f,
                  ensure_ascii=False, indent=4, default=str)


try:
    update_overtime_mentions_graph()
    update_homogeneous_category_mentions_graph()
    update_week_bias_mentions_graph()

    update_overtime_quotes_graph()
    update_homogeneous_category_quotes_graph()
    update_week_bias_quotes_graph()

    logger.info('graphs successfully updated')

except:
    logger.info('failed to update graphs')


try:
    update_articles_of_the_week_table()

    logger.info('articles of the week table successfully updated')

except:
    logger.info('failed to update articles of the week table')


try:
    update_data_mentions()
    update_data_quotes()

    logger.info('data files successfully updated')

except:
    logger.info('failed to update data files')
