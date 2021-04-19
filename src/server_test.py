"""
Test the functionality of server.
"""
import unittest
import requests
from mongo_manipulator import connect_to_mongo
from update import load_json_file

HOST = "http://127.0.0.1:5000/"


class TestServer(unittest.TestCase):
    """
    Unit test class wrapper for server tests.
    """
    def test_client_search_with_id(self):
        """
        Test server can response to existing id correctly.
        :return:
        """
        book_db, author_db = connect_to_mongo()
        response1 = requests.get(HOST + "api/book", params={"_id": "58128"})
        expected1 = list(book_db.find({"_id": "58128"}))
        self.assertEqual(response1.json(), expected1)

        response2 = requests.get(HOST + "api/author", params={"_id": "45372"})
        expected2 = list(author_db.find({"_id": "45372"}))
        self.assertEqual(response2.json(), expected2)

    def test_client_elastic_search(self):
        """
        Test server can handle valid elastic search requests correctly.
        :return:
        """
        book_db, _ = connect_to_mongo()
        query1 = "book.rating_count : > 500 AND book.rating_count : < 1000"
        response1 = requests.get(HOST + "api/search", params={"q": query1})
        expected1 = list(book_db.find({"$and": [{"rating_count": {"$gt": 500}},
                                           {"rating_count": {"$lt": 1000}}]}))
        self.assertEqual(response1.json(), expected1)

        query2 = "book.review_count : < 30 OR book.rating_value : < 3.5"
        response2 = requests.get(HOST + "api/search", params={"q": query2})
        expected2 = list(book_db.find({"$or": [{"review_count": {"$lt": 30}},
                                           {"rating_value": {"$lt": 3.5}}]}))
        self.assertEqual(response2.json(), expected2)

    def test_server_upload_and_delete(self):
        """
        Test that server can handle upload and delete requests correctly.
        :return:
        """
        book_db, _ = connect_to_mongo()
        book_id = "3735293"
        self.assertTrue(list(book_db.find({"_id": book_id})))  # existing book

        requests.delete(HOST + "api/book", params={"_id": book_id})  # delete request
        self.assertFalse(list(book_db.find({"_id": book_id})))  # not existing after del

        post_body = load_json_file("legal_one_book.json")
        requests.post(HOST + "api/book", json=post_body)
        self.assertTrue(list(book_db.find({"_id": book_id})))  # existing after uploading

    def test_invalid_search_with_id(self):
        """
        Test server will return 400 when _id is missing for search with id
        """
        response1 = requests.get(HOST + "api/book", params={})
        self.assertEqual(response1.status_code, 400)

        response2 = requests.get(HOST + "api/author", params={})
        self.assertEqual(response2.status_code, 400)

    def test_invalid_elastic_search(self):
        """
        Test server will return 400 for bad requests (missing q, or bad query string).
        """
        # missing url parameter q
        response1 = requests.get(HOST + "api/search", params={})
        self.assertEqual(response1.status_code, 400)

        # invalid query string
        response2 = requests.get(HOST + "api/search", params={"q": "book._id > 123"})
        self.assertEqual(response2.status_code, 400)

    def test_invalid_update_value(self):
        """
        Test server can handle various bad update (PUT request) correctly.
        """
        response1 = requests.put(HOST + "api/book", data={"a": "b"})
        self.assertEqual(response1.status_code, 415)

        response2 = requests.put(HOST + "api/author", json={})  # empty json
        self.assertEqual(response2.status_code, 400)

        # Bad update key
        response3 = requests.put(HOST + "api/book", json={"_id": "58128", "a": "Q A Q"})
        self.assertEqual(response3.status_code, 400)

        # Bad id
        response4 = requests.put(HOST + "api/book", json={"_id": 58128, "book_url": "Q u Q"})
        self.assertEqual(response4.status_code, 400)

    def test_invalid_upload(self):
        """
        Test server can handle various bad upload (POST request) correctly.
        """
        # content type not JSON
        response1 = requests.post(HOST + "api/book", data={"book_id": 123})
        self.assertEqual(response1.status_code, 415)

        # content type undefined
        response2 = requests.post(HOST + "api/author")
        self.assertEqual(response2.status_code, 415)

        # empty JSON
        response3 = requests.post(HOST + "api/author", json=[])
        self.assertEqual(response3.status_code, 400)

        # upload one to api/books
        one_book = load_json_file("legal_one_book.json")
        response4 = requests.post(HOST + "api/books", json=one_book)
        self.assertEqual(response4.status_code, 400)

        # upload many to api/book
        many_books = load_json_file("legal_many_books.json")
        response5 = requests.post(HOST + "api/book", json=many_books)
        self.assertEqual(response5.status_code, 400)

    def test_bad_scrape_request(self):
        """
        Test server can handle scrape request with missing json or missing params.
        """
        # empty json file
        response1 = requests.post(HOST + "api/scrape", data={"a": "b"})
        self.assertEqual(response1.status_code, 415)

        # null json file
        response2 = requests.post(HOST + "api/scrape")
        self.assertEqual(response2.status_code, 415)

        # missing max_author and start_url
        response3 = requests.post(HOST + "api/scrape", json={"max_book": 200})
        self.assertEqual(response3.status_code, 400)

    def test_bad_request_delete(self):
        """
        Test server can respond to bad delete request correctly.
        :return:
        """
        # id not provided
        response1 = requests.delete(HOST + "api/book", params={})
        self.assertEqual(response1.status_code, 400)

        # target id not in db
        response2 = requests.delete(HOST + "api/author", params={"_id": "aaa"})
        self.assertEqual(response2.status_code, 400)


if __name__ == "__main__":
    unittest.main()
