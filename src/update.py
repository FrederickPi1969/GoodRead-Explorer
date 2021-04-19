"""
Handles the main-subcommand update.
Takes in json file and insert/update in database.
"""
import json
import sys
from mongo_manipulator import connect_to_mongo

BOOK_ATTRS = ["_id", "book_url", "book_title", "cover_url", "rating_value",
              "book_id", "rating_count", "review_count", "author_name",
              "author_url", "ISBN", "similar_book_urls"]
AUTHOR_ATTRS = ["_id", "author_name", "author_id", "author_url",
                "rating_count", "review_count", "rating_value", "image_url",
                "related_authors", "author_books"]
JSON_PATH = "../JSON/"


def find_missing_attrs(dictionaries, attrs):
    """
    Find all missing attributes of every dictionary in a given dict list,
    and make the result as a set.
    :param dictionaries: a list of dictionary
    :attrs attributes: to be checked (BOOK_ATTRS or AUTHOR_ATTRS)
    :return: a list of missing attributes
    """
    missing_attrs = set()
    for dic in dictionaries:
        for attr in attrs:
            if attr not in dic:
                missing_attrs.add(attr)
    return list(missing_attrs)


def load_json_file(src_json, root=JSON_PATH):
    """
    Load json file specified by the given path.
    :param src_json: Name of the json file (File name only)
    :param root: root directory of JSON file.
    :return: loaded json file as a LIST OF DICTS if successfully loaded else raise error.
    """
    try:
        with open(root + src_json, "r+") as file:  # make sure src_json exists
            loaded_json = json.load(file)   # can be both dict or list!
            if isinstance(loaded_json, dict):
                loaded_json = [loaded_json]  # make single dict a list
            return loaded_json
    except:
        print("Input json file is not legal!")
        sys.exit(1)


def check_missing_attributes(dictionary_list, attrs_to_check):
    """
    Check whether all given instances have all required attributes.
    Raise error if any attr is missing.
    :param dictionary_list: a list of dict converted from json.
    :param attrs_to_check: attributes to check (see constants above.
    """
    missing_attrs = find_missing_attrs(dictionary_list, attrs_to_check)
    if missing_attrs:
        print(f"Attributes: {missing_attrs} are missing in provided in Json file.")
        sys.exit(1)


def write_given_dict_list_to_db(dictionary_list, db):
    """
    Not enter interface!
    Helper function for insert list of dicts to target db.
    Notice any dicts that list passed to this function
    should complete the sanity check.
    :param dictionary_list: the list of dicts to be inserted
    :param db: the target db to insert
    """
    for dic in dictionary_list:
        item_id = dic["_id"]
        query_dic = {"_id": item_id}
        if list(db.find(query_dic)):  # non empty
            new_values = {"$set": dic}
            db.update_one(query_dic, new_values)
            print(f"Value of id: {item_id} Successfully updated.")
            continue
        db.insert_one(dic)  # insert new
        print(f"Object with id: {item_id} Successfully inserted into database.")


def insert_into_db(src_json, db_type):
    """
    Safely insert the entities from json file into remote mongoDB.
    Json files are required to:
    (1) The json file exists;
    (2) Be in good shape, parse-able (either one dic or list of dic);
    (3) Every single stored object has no missing keys as stated above;
    (4) Not existed in the database;
    to be inserted into the database.
    :param src_json: the NAME json file, stored in the ../JSON directory. Do not add path!
    :param db_type: either book or author
    """
    book_db, author_db = connect_to_mongo()
    attrs_to_check = BOOK_ATTRS if db_type == "book" else AUTHOR_ATTRS
    db_to_update = book_db if db_type == "book" else author_db

    dictionary_list = load_json_file(src_json)

    # make sure there are no missing attributes
    check_missing_attributes(dictionary_list, attrs_to_check)

    # Write into target db
    write_given_dict_list_to_db(dictionary_list, db_to_update)


