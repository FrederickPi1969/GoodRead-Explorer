"""
Build connection with remote mongoDB,
and perform data manipulator (dump db as json).
"""
import os
import json
import pymongo
from dotenv import load_dotenv

JSON_PATH = "../JSON/"


def connect_to_mongo():
    """
    Open connection to mongoDB
    :return: book_db, author_db book collection and author collection in remote mongo atlas
    """
    load_dotenv()
    key = os.getenv("MONGO_KEY")
    client = pymongo.MongoClient(key)
    client.list_database_names()
    goodread_db = client["GoodRead"]
    book_db, author_db = goodread_db["books"], goodread_db["authors"]
    # book_db, author_db = goodread_db["books_test"], goodread_db["authors_test"]
    return book_db, author_db


def dump_db(db_choice):
    """
    Dump indicated database from mongoDB to local json.
    :param db_choice: "book", "author", or "all"
    """
    book_db, author_db = connect_to_mongo()
    book_db_name = "book_db.json"
    author_db_name = "author_db.json"
    if db_choice == "book":
        dump(book_db, book_db_name)
    elif db_choice == "author":
        dump(author_db, author_db_name)
    else:
        dump(book_db, book_db_name)
        dump(author_db, author_db_name)


def dump(db_to_dump, file_name):
    """
    Helper function for dumping file and logging.
    :param db_to_dump: target db to dump
    :param file_name: output file name
    """
    path = JSON_PATH + file_name
    with open(path, "w+") as file:
        json.dump(list(db_to_dump.find({})), file)
        print(f"Successfully dumped {file_name} to {path}")


def convert_string_attr_to_numeric():
    """
    When the review_count, rating_value, rating_count are first scraped,
    they are stored in string form. i.e. "173,245".
    This function converts these attributes to numeric form.
    """
    book_db, author_db = connect_to_mongo()
    for i, dic in enumerate(book_db.find()):
        id_ = dic["_id"]
        review_count = dic["review_count"]
        update_key = {"_id": id_}
        update_dict = {"$set": {}}

        if review_count is not None:
            review_count = review_count.replace(",", "")
            update_dict["$set"]["review_count"] = int(review_count)

        rating_value = dic["rating_value"]
        if rating_value is not None:
            update_dict["$set"]["rating_value"] = float(rating_value)

        rating_count = dic["rating_count"]
        if rating_count is not None:
            rating_count = str(rating_count).replace(",", "")
            update_dict["$set"]["rating_count"] = int(rating_count)
        book_db.update_one(update_key, update_dict)

    for i, dic in enumerate(author_db.find()):
        id_ = dic["_id"]
        review_count = dic["review_count"]
        update_key = {"_id": id_}
        update_dict = {"$set": {}}

        if review_count is not None:
            review_count = str(review_count).replace(",", "")
            update_dict["$set"]["review_count"] = int(review_count)

        rating_value = dic["rating_value"]
        if rating_value is not None:
            update_dict["$set"]["rating_value"] = float(rating_value)

        rating_count = dic[" rating_count"]
        if rating_count is not None:
            rating_count = str(rating_count).replace(",", "")
            update_dict["$set"]["rating_count"] = int(rating_count)
        author_db.update_one(update_key, update_dict)


if __name__ == "__main__":
    connect_to_mongo()
