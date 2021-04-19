"""For testing behavior of book scraper"""
import unittest
from book_scraper import BookScraper


class TestBookScraper(unittest.TestCase):
    """
    Test book scraper can scrape information correctly.
    """
    def test_scrape_valid_book_url(self):
        """
        Test that book scraper can scrape information
        from a valid book url correctly.
        """
        scraper = BookScraper()
        book_url = "https://www.goodreads.com/book/show/108986.Introduction_to_Algorithms"
        dic = scraper.scrape_book(book_url)
        self.assertEqual(dic["rating_value"], 4.34)
        img_url = "https://i.gr-assets.com/images/S/compressed.photo." \
                  "goodreads.com/books/1387741681l/108986.jpg"
        self.assertEqual(dic["cover_url"], img_url)
        author_url = "https://www.goodreads.com/author/show/60841.Thomas_H_Cormen"
        self.assertEqual(dic["author_url"], author_url)
        similar_book_url = "https://www.goodreads.com/book/show/515601.The_C_Programming_Language"
        self.assertTrue(similar_book_url in dic["similar_book_urls"])

    def test_scrape_valid_book_no_isbn(self):
        """
        Given a url of a book without ISBN,
        the scraper should be able to retrieve other information correctly.
        """
        scraper = BookScraper()
        book_url = "https://www.goodreads.com/book/show/25008661-the-rust-programming-language"
        dic = scraper.scrape_book(book_url)
        self.assertTrue(dic is not None)
        self.assertEqual(dic["rating_value"], 4.43)
        self.assertTrue(dic["ISBN"] is None)
        img_url = "https://i.gr-assets.com/images/S/compressed.photo." \
                  "goodreads.com/books/1518920310l/25008661._SX318_.jpg"
        self.assertEqual(dic["cover_url"], img_url)
        author_url = "https://www.goodreads.com/author/show/7048888.Steve_Klabnik"
        self.assertEqual(dic["author_url"], author_url)
        similar_book_url = "https://www.goodreads.com/book/show/25550614-programming-rust"
        self.assertTrue(similar_book_url in dic["similar_book_urls"])

    def test_scrape_invalid_book_url_wrong_format(self):
        """
        Test invalid input url does has prefix "https://www.goodreads.com/book/show/"
        """
        scraper = BookScraper()
        dic = scraper.scrape_book("https://www.google.com/")  # bad shape
        self.assertTrue(dic is None)

    def test_scrape_invalid_book_url_non_exist(self):
        """
        Test invalid input with the prefix, but actually not exists.
        """
        scraper = BookScraper()
        book_url = "https://www.goodreads.com/book/show/373a91"  # good shape but non-exist
        dic = scraper.scrape_book(book_url)
        self.assertTrue(dic is not None)
        self.assertTrue(dic["book_id"] is None)


if __name__ == "__main__":
    unittest.main()
