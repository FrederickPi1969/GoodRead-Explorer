""" Test functionality of author scraper
"""
import unittest
from author_scraper import AuthorScraper


class TestAuthorScraper(unittest.TestCase):
    """
    Test functionality of author scraper
    """
    def test_scrape_valid_book_url(self):
        """
        Test that book scraper can scrape information
        from a valid book url correctly.
        """
        scraper = AuthorScraper()
        author_url = "https://www.goodreads.com/author/show/17037914.Nicole_Forsgren"
        dic = scraper.scrape_author(author_url)
        self.assertTrue(dic is not None)
        self.assertEqual(dic["rating_value"], 4.09)
        image_url = "https://images.gr-assets.com/authors/1521480284p5/17037914.jpg"
        self.assertEqual(dic["image_url"], image_url)
        related_author_url = "https://www.goodreads.com/author/show/2815.Andy_Hunt"
        self.assertTrue(related_author_url in dic["related_authors"])

    def test_scrape_invalid_book_url_wrong_format(self):
        """
        Test invalid input url does has prefix "https://www.goodreads.com/book/show/"
        """
        scraper = AuthorScraper()
        dic = scraper.scrape_author("https://www.google.com/") # bad shape
        self.assertTrue(dic is None)

    def test_scrape_invalid_book_url_non_exist(self):
        """
        Test invalid author url input with valid prefix, but actually not exists.
        """
        scraper = AuthorScraper()
        # a good shape but non-existing url
        author_url = "https://www.goodreads.com/author/show/612305-Frederick"
        dic = scraper.scrape_author(author_url)
        self.assertTrue(dic is not None)
        self.assertTrue(dic["author_name"] is None)
        self.assertTrue(dic["image_url"] is None)


if __name__ == "__main__":
    unittest.main()
