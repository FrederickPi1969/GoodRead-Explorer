"""
Test normal functionality of interpreter.
"""
import unittest
from interpreter import *


class TestInterpreter(unittest.TestCase):
    """
    Test that interpreter can behave robustly.
    """

    def test_single_invalid_db_type(self):
        """
        Test interpreter can detect missed db type
        """
        test1 = '.book_url : "123"'  # type cannot be ''
        self.assertRaises(Exception, parse_single_query_unit, test1)

        test2 = '       .related_authors : "123"'  # type can not be empty spaces
        self.assertRaises(Exception, parse_single_query_unit, test2)

        test2 = 'Book.related_authors : "123"'  # type can be strings other than author or book
        self.assertRaises(Exception, parse_single_query_unit, test2)

    def test_single_miss_query_field(self):
        """
        Test interpreter can detect missed query field - i.e. x in (book/author).x
        """
        test1 = 'book. : "123"'
        self.assertRaises(Exception, parse_single_query_unit, test1)

        test2 = 'author.     : "123"'
        self.assertRaises(Exception, parse_single_query_unit, test2)

    def test_single_query_field_not_in_db(self):
        """
        When the input query field is not found in database,
        interpreter should raise an error.
        """
        test1 = 'book.BOOK_url : "123"'
        self.assertRaises(Exception, parse_single_query_unit, test1)

        test2 = 'author .  author_url     : "123"'
        self.assertRaises(Exception, parse_single_query_unit, test2)

    def test_single_invalid_query_value(self):
        """
        When there's no operator (>, <, NOT) provided,
        Query value must be quoted for exact matches.
        Also, it cannot be ''.
        """
        test1 = 'book.book_url : https:google.com'  # not valid because it's not quoted
        self.assertRaises(Exception, parse_single_query_unit, test1)

        test2 = 'author.cover_url : ""'  # not valid because it's ""
        self.assertRaises(Exception, parse_single_query_unit, test2)

        test3 = 'author.cover_url : "asdad" 123 '  # not valid because it's ""
        self.assertRaises(Exception, parse_single_query_unit, test3)

    def test_single_no_operator_valid_input(self):
        """
        Test valid outputs with various spacing - test they should be all be correctly extracted.
        """
        test1 = 'book.book_url     :       "https://www.goodreads.com/book/show/3735293-clean-code"'
        expected_out1 = ["book", "book_url", "",
                         '"https://www.goodreads.com/book/show/3735293-clean-code"']
        self.assertEqual(list(parse_single_query_unit(test1)), expected_out1)

        test2 = '     book.book_url:   "https://www.goodreads.com/book/show/3735293-clean-code"'
        expected_out2 = expected_out1
        self.assertEqual(list(parse_single_query_unit(test2)), expected_out2)

        test3 = 'author.related_authors:"null"'
        expected_out3 = ["author", "related_authors", "", '"null"']
        self.assertEqual(list(parse_single_query_unit(test3)), expected_out3)

    def test_single_with_comparison_operator_invalid(self):
        """
        Test when the query string contains comparison operator (> / <),
        the interpreter can successfully block invalid inputs.
        """
        test1 = "book.rating_value : >  \"4.24\""  # query val should not be quoted
        self.assertRaises(Exception, parse_single_query_unit, test1)

        test2 = "book.rating_value : <  "  # query val should not be empty
        self.assertRaises(Exception, parse_single_query_unit, test2)

        test3 = "book.rating_value : > four "  # query val should only be positive integer
        self.assertRaises(Exception, parse_single_query_unit, test3)

        test4 = "book.rating_value : NOT > four "  # only one Comp_op is allowed.
        self.assertRaises(Exception, parse_single_query_unit, test4)

    def test_single_with_comparison_operator_valid(self):
        """
        Test when the query string contains comparison operator (> / <),
        the interpreter can successfully handles legal inputs ().
        """
        test1 = "  book.rating_value : > 4.24  "
        expected_out1 = ["book", "rating_value", ">", '4.24']
        self.assertEqual(list(parse_single_query_unit(test1)), expected_out1)

        test2 = "author.review_count   :  <   15000"
        expected_out2 = ["author", "review_count", "<", "15000"]
        self.assertEqual(list(parse_single_query_unit(test2)), expected_out2)

        test3 = "author.review_count:<15000"  # no spacing
        expected_out3 = ["author", "review_count", "<", "15000"]
        self.assertEqual(list(parse_single_query_unit(test3)), expected_out3)

    def test_single_with_NOT_operator_input(self):
        """
        Test when the query string contains NOT operator,
        the interpreter can successfully can accept legal inputs.
        """
        test1 = '  book.rating_value : NOT "4.24" '
        expected_out1 = ["book", "rating_value", "NOT", "4.24"]
        self.assertTrue(list(parse_single_query_unit(test1)), expected_out1)

        test2 = '     book.book_url: NOT  "https://www.goodreads.com/book/show/3735293-clean-code"'
        expected_out2 = ["book", "book_url", "NOT",
                         '"https://www.goodreads.com/book/show/3735293-clean-code"']
        self.assertEqual(list(parse_single_query_unit(test2)), expected_out2)

    def test_logic_connection_invalid_input(self):
        """
        When there is logic connection operator in the query,
        the interpreter should raise error for invalid inputs.
        """
        # Nested input is not supported
        test1 = 'author.review_count : < 1500 AND book.book_url : > 123 ' \
                'OR book.rating_count : < 600'
        self.assertRaises(Exception, parse_query_string, test1)

        # complete query unit of form "db.query_attr : Comp_op query_value"
        # must be provided around "AND" or "OR".
        test2 = 'book.review_count : < 1500 AND > 600'
        self.assertRaises(Exception, parse_query_string, test2)

        # Every single unit must be legal
        test3 = 'book.review_count : < 1500 AND > author.aaaaaa : "google.com"'
        self.assertRaises(Exception, parse_query_string, test3)

        # The two queried DB must be the same one
        test4 = 'book.review_count : < 1500 AND > author.author_id : "1234"'
        self.assertRaises(Exception, parse_query_string, test4)

    def test_logic_connection_valid_input(self):
        """
        Test that legal input with logic connection operators can be parsed correctly.
        """
        test1 = ' author.author_url : "aaa"   AND   author.rating_value : > 4.32    '
        expected_result1 = [("author", "author_url", "", '"aaa"'),
                            ("author", "rating_value", ">", "4.32")]
        expected_op1 = "AND"
        self.assertEqual(parse_query_string(test1), tuple([expected_result1, expected_op1]))

        test2 = ' author.author_url : "aaa"   OR   author.rating_value : > 4.32    '
        expected_result2 = [("author", "author_url", "", '"aaa"'),
                            ("author", "rating_value", ">", "4.32")]
        expected_op2 = "OR"
        self.assertEqual(parse_query_string(test2), tuple([expected_result2, expected_op2]))

    def test_mixed_valid_inputs(self):
        """
        Test that the interpreter can interpret both
        single query unit and units combined logic operator
        with legal input correctly.
        """
        test1 = "  book.book_title :  NOT \"Code Complete 5th Edition\" "  # single query unit
        expected_result1 = ["book", "rating_value", "NOT", '"Code Complete"']
        expected_op1 = "NA"
        self.assertTrue(list(parse_single_query_unit(test1)),
                        tuple([expected_result1, expected_op1]))

        test2 = ' book.book_url : "duckduckgo"   AND   book.rating_count : > 123    '
        expected_result2 = [("book", "book_url", "", '"duckduckgo"'),
                            ("book", "rating_count", ">", "123")]
        expected_op2 = "AND"
        self.assertEqual(parse_query_string(test2), tuple([expected_result2, expected_op2]))

    def test_mongo_query_conversion(self):
        """
        Test interpreter can correctly convert
        single units of query to mongo query key.
        Notice we should assume the input units are always valid.
        """
        test1 = ["book", "book_url", "", '"https://www.duckduckgo.com"']
        expected1 = {"book_url": "https://www.duckduckgo.com"}
        self.assertEqual(convert_to_mongo_query_key(test1), expected1)

        test2 = ["author", "rating_value", ">", "4.23"]
        expected2 = {"rating_value": {"$gt": 4.23}}
        self.assertEqual(convert_to_mongo_query_key(test2), expected2)

        test3 = ["book", "book_title", "NOT", '"Code Complete"']
        expected3 = {"book_title": {"$ne": "Code Complete"}}
        self.assertEqual(convert_to_mongo_query_key(test3), expected3)

        test4 = ["author", "review_count", "<", "1969"]
        expected4 = {"review_count": {"$lt": 1969}}
        self.assertEqual(convert_to_mongo_query_key(test4), expected4)

    def test_repl_single_query_unit(self):
        """
        Test repl by interpreter can retrieve correct result from MongoDB.
        """
        book_db, author_db = connect_to_mongo()
        test1 = repl_query('book.rating_value : NOT "4.34"')
        expected1 = list(book_db.find({"rating_value": {"$ne": 4.34}}))
        self.assertEqual(test1, expected1)

        test2 = repl_query("book.review_count : > 10000")
        expected2 = list(book_db.find({"review_count": {"$gt": 10000}}))
        self.assertEqual(test2, expected2)

        test3 = repl_query("author.rating_count : < 100")
        expected3 = list(author_db.find({"rating_count": {"$lt": 100}}))
        self.assertEqual(test3, expected3)

        test4 = repl_query('author.author_url :'
                           '"https://www.goodreads.com/author/show/45372.Robert_C_Martin"')
        url = "https://www.goodreads.com/author/show/45372.Robert_C_Martin"
        expected4 = list((author_db.find({"author_url": url})))
        self.assertEqual(test4, expected4)

    def test_repl_logic_connected_query_units(self):
        """
        Test that repl can retrieve correct data for query with logic operators.
        """
        book_db, author_db = connect_to_mongo()
        test1 = repl_query("book.rating_value : > 4.25 AND book.rating_value : < 4.50")
        expected1 = list(book_db.find({"$and": [{"rating_value": {"$gt": 4.25}},
                                            {"rating_value": {"$lt": 4.50}}]}))
        self.assertEqual(test1, expected1)

        test2 = repl_query("author.review_count : < 200 OR author.rating_count : < 150")
        expected2 = list(author_db.find({"$or": [{"review_count": {"$lt": 200}},
                                            {"rating_count": {"$lt": 150}}]}))
        self.assertEqual(test2, expected2)

    def test_repl_wildcard_in_query_attr(self):
        """
        Test that repl can correctly find matching value when
        a "*" occurs in query_attr - e.g. book.*_count
        :return:
        """
        book_db, author_db = connect_to_mongo()
        test1 = repl_query('book.*_count :  "412"')
        expected1 = list(book_db.find({"$or": [{"rating_count": 412},
                                               {"review_count": 412}]}))
        self.assertEqual(test1, expected1)

        book_db, author_db = connect_to_mongo()
        test2 = repl_query('book.*_count :  "412" OR book.rating_* : "4.28"')
        test2_id = sorted([dic["_id"] for dic in test2])
        expected2_match1 = list(book_db.find({"$or": [{"rating_count": 412},
                                               {"review_count": 412}]}))
        expected2_match2 = list(book_db.find({"rating_value": 4.28}))
        expected2 = expected2_match1 + expected2_match2
        expected2_id = sorted([dic["_id"] for dic in expected2])
        self.assertEqual(test2_id, expected2_id)

    def test_repl_wildcard_in_query_value(self):
        """
        Test that repl can correctly find matching value when
        a "*" occurs in query_value - e.g. book.book_title : "Code*"
        """
        book_db, author_db = connect_to_mongo()
        test1 = repl_query('book.author_name :  "David*"')
        test1_id = sorted([dic["_id"] for dic in test1])
        expected1_id = []
        for dic in book_db.find():
            if dic["author_name"][:5] == "David":
                expected1_id.append(dic["_id"])
        self.assertEqual(test1_id, sorted(expected1_id))

        test2 = repl_query('author.author_name : "Martin*" OR author.rating_value : "4.5*"')
        test2_id = sorted([dic["_id"] for dic in test2])
        expected2_id = []
        for dic in author_db.find():
            if dic["author_name"][:6] == "Martin":
                expected2_id.append(dic["_id"])
                continue
            if str(dic["rating_value"])[:3] == "4.5":
                expected2_id.append(dic["_id"])
        self.assertEqual(test2_id, sorted(expected2_id))


if __name__ == "__main__":
    unittest.main()
