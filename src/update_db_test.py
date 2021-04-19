"""
Test whether update module can update info in db properly.
"""
import json
import unittest
from update import insert_into_db
from mongo_manipulator import connect_to_mongo

JSON_PATH = "../JSON/"


class TestJsonUpdater(unittest.TestCase):
    """
    Test whether update module can update info in db properly.
    """

    def test_malformatted_json(self):
        """
        Test non-parseable JSON file will cause error
        """
        path = JSON_PATH + "malformed_author.json"
        try:
            insert_into_db(path, db_type="author")
            self.assertTrue(False)  # An error should be thrown
        except:
            self.assertTrue(True)

    def test_author_missing_key(self):
        """
        Test book json file with missing url will be blocked.
        """
        path = JSON_PATH + "book_miss_book_url.json"
        try:
            insert_into_db(path, db_type="book")
            self.assertTrue(False)  # An error should be thrown
        except:
            self.assertTrue(True)

    def test_book_missing_key(self):
        """
        Test author with missing related authors will be blocked
        """
        path = JSON_PATH + "author_miss_related_authors.json"
        try:
            insert_into_db(path, "author")
            self.assertTrue(False)  # An error should be thrown
        except:
            self.assertTrue(True)

    def test_valid_single_dict_create(self):
        """
        Test valid json file that contains a single dictionary could be inserted,
        by deleting one existing author and reinsert it.
        """
        path = JSON_PATH + "legal_one_author.json"
        _, author_db = connect_to_mongo()
        with open(path, "r+") as file:
            author_dic = json.load(file)

        author_id = author_dic["_id"]
        self.assertTrue(list(author_db.find({"_id": author_id})) != [])
        author_db.delete_one({"_id": author_id})
        self.assertTrue(list(author_db.find({"_id": author_id})) == [])

        insert_into_db(path, db_type="author")
        self.assertTrue(list(author_db.find({"_id": author_id})) != [])

    def test_valid_many_dict_create(self):
        """
        Test valid json file that contains a list of dictionaries could be inserted,
        by deleting many existing books and reinserting.
        """
        path = JSON_PATH + "legal_many_books.json"
        book_db, _ = connect_to_mongo()
        with open(path, "r+") as file:
            book_dics = json.load(file)

        for _, book_dic in enumerate(book_dics):
            book_id = book_dic["_id"]
            self.assertTrue(list(book_db.find({"_id": book_id})) != [])
            book_db.delete_one({"_id": book_id})
            self.assertTrue(list(book_db.find({"_id": book_id})) == [])

        insert_into_db(path, "book")
        for _, book_dic in enumerate(book_dics):
            book_id = book_dic["_id"]
            self.assertTrue(list(book_db.find({"_id": book_id})) != [])

    def test_valid_one_dict_update(self):
        """
        Test valid json file of a single dict can be used to
        update value of existing object in database.
        First modify one author's url and then recover it.
        """
        path = JSON_PATH + "legal_one_author.json"
        _, author_db = connect_to_mongo()
        with open(path, "r+") as file:
            author_dic = json.load(file)

        author_id = author_dic["_id"]
        true_author_url = author_dic["author_url"]
        query_key = {"_id": author_id}
        update_val = {"$set": {"author_url": "duckduckgo.com"}}
        self.assertTrue(list(author_db.find(query_key)) != [])

        # modify author url to duckduckgo
        author_db.update_one(query_key, update_val)
        author_url_modified = author_db.find_one(query_key)["author_url"]
        self.assertEqual(author_url_modified, "duckduckgo.com")

        # recover author url
        insert_into_db(path, db_type="author")
        author_url_recovered = author_db.find_one(query_key)["author_url"]
        self.assertEqual(author_url_recovered, true_author_url)

    def test_valid_many_dict_update(self):
        """
        Test valid json file of a list of dicts can be used to
        update value of existing object in database.
        First modify books' url and then recover them.
        """
        path = JSON_PATH + "legal_many_books.json"
        book_db, _ = connect_to_mongo()
        with open(path, "r+") as file:
            book_dics = json.load(file)

        true_book_urls = []
        # first modify all target book_urls in db
        for book_dic in book_dics:
            book_id = book_dic["_id"]
            true_book_urls.append(book_dic["book_url"])
            query_key = {"_id": book_id}
            update_val = {"$set": {"book_url": "duckduckgo.com"}}
            book_db.update_one(query_key, update_val)
            self.assertTrue(list(book_db.find(query_key)) != [])

        # recover book url
        insert_into_db(path, db_type="book")
        for i, book_dic in enumerate(book_dics):
            book_id = book_dic["_id"]
            true_url = true_book_urls[i]
            query_key = {"_id": book_id}
            self.assertTrue(book_db.find_one(query_key)["book_url"], true_url)


if __name__ == "__main__":
    unittest.main()
