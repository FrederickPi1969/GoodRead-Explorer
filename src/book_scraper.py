"""
Scraper for book information.
"""
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.goodreads.com"


class BookScraper:
    """
    A wrapper interface class for extracting book information from goodread.com.
    Notice it's designed for collecting one book at a time.
    """

    def parse_book_info(self, book_url, html_soup):
        """
        Extract the book info (name, url) from a given book page html.
        :param html_soup: the result of injecting src_html into bs4
        :param book_url: the source url from which html_soup is generated
        :return: a dictionary of book attributes as required in the rubric
        """
        book_attrs = ["book_url", "book_title", "cover_url", "rating_value", "book_id",
                      "rating_count", "review_count", "author_name", "author_url",
                      "ISBN", "similar_book_urls"]
        book_dict = {key: None for key in book_attrs}

        try:
            book_dict["book_url"] = book_url
            book_dict["book_title"] = html_soup.select("#bookTitle")[0].text.strip()  # title
            # book_dict["rating_value"] = \
            #     html_soup.select('span[itemprop="ratingValue"]')[0].text.strip()  # rating value
            rating_value = html_soup.select('span[itemprop="ratingValue"]')[0].text.strip()
            book_dict["rating_value"] = float(rating_value)
            book_dict["cover_url"] = html_soup.select("#coverImage")[0]["src"]  # cover image url
            book_dict["book_id"] = html_soup.select("#book_id")[0]["value"]  # book_id
            for child in html_soup.select("#reviewControls >"
                                          " div.reviewControls--left.greyText")[0].children:
                if "ratings" in child:
                    rating_count = re.findall(r"([0-9,]*)", child.replace("\n", "").strip())[0]
                    book_dict["rating_count"] = int(rating_count.replace(",", ""))
                    # book_dict["rating_count"] = \
                    #     re.findall(r"([0-9,]*)", child.replace("\n", "").strip())[0]

                if "reviews" in child:
                    review_count = re.findall(r"([0-9,]*)", child.replace("\n", "").strip())[0]
                    book_dict["review_count"] = int(review_count.replace(",", ""))
                    # book_dict["review_count"] = \
                    #     re.findall(r"([0-9,]*)", child.replace("\n", "").strip())[0]

            author_profile = html_soup.select("div.bookAuthorProfile__name")[0].a
            book_dict["author_url"] = BASE_URL + author_profile["href"]  # url of author
            book_dict["author_name"] = html_soup.select("div.bookAuthorProfile__name")[0].\
                a.text.strip()  # name of author
            book_dict["similar_book_urls"] = self.parse_similar_books(html_soup)
            isbn, _ = self.parse_isbn(html_soup)
            book_dict["ISBN"] = isbn
        except:
            for attr in book_attrs:
                if book_dict[attr] is None:
                    # logging failed
                    print(f"{attr} extraction in BOOK {book_url} failed...")
        return book_dict

    def parse_similar_books(self, html_soup):
        """
        Retrieve all similar book recommendations from the soup html.
        :param html_soup: soup object generated with bs4 from src_html
        :return: a list of urls of similar recommended books stated in the source html
        """
        similar_book_urls = []
        for li_elem in html_soup.select("div.bookCarousel > div.carouselRow > ul > li"):
            try:
                book_info = li_elem.a
                book_url = book_info["href"]
                similar_book_urls.append(book_url)
            except:
                continue
        return similar_book_urls

    def parse_isbn(self, html_soup):
        """
        Retrieving the ISBN of books can be a bit tricky.
        This function is designed to robustly extract ISBN.
        :param html_soup: the souped html of src html from book_url
        :return: ISBN, ISBN13
        """
        isbn, isbn13 = None, None
        max_depth = 5  # ISBN number shouldn't be far from the following element!
        try:
            # could be navigable string or tag
            elem_iter = html_soup.find_all("div", string="ISBN")[0].nextSibling
            current_depth = 0
            while current_depth < max_depth:
                if elem_iter is None:
                    break
                try:
                    elem_text = elem_iter.text.replace("\n", "").strip()
                except:
                    elem_iter = elem_iter.nextSibling  # visit next tag
                    current_depth += 1
                    continue

                isbn, isbn13 = self.extract_isbn_from_tag_text(elem_text)
                if isbn is not None or isbn13 is not None:
                    break

                elem_iter = elem_iter.nextSibling  # visit next tag
                current_depth += 1
                if current_depth == max_depth:
                    print("This ISBN of the book is not applicable.")

        except:
            # error in find the starting point ISBN tag
            print("This ISBN of the book is not applicable.")

        return isbn, isbn13

    def extract_isbn_from_tag_text(self, elem_text):
        """
        Given the text inside a tag, this function tries to extract ISBNs.
        :return ISBN: ISBN13 if found else None, None
        """
        assert elem_text is not None
        isbn, isbn13 = None, None
        isbns = re.findall(r"(\d{10,13})", elem_text)  # try to extract ISBNs
        if 0 < len(isbns) <= 2:
            for iter_isbn in isbns:
                if len(iter_isbn) == 10:
                    isbn = iter_isbn
                elif len(iter_isbn) == 13:
                    isbn13 = iter_isbn
        return isbn, isbn13

    def scrape_book(self, book_url):
        """
        The enter interface of this whole class. It will organize the interaction of all methods
        :param book_url: url of a book page.
         (e.g. "https://www.goodreads.com/book/show/108986.Introduction_to_Algorithms")
        :return: a dictionary containing all required book attribute information
        """
        try:
            assert len(re.findall(r'^(https://www.goodreads.com/book/show/.*)$', book_url)) != 0
        except:
            print("Input URL is illegal")
            return None

        try:
            html_src = requests.get(book_url).text
            html_soup = BeautifulSoup(html_src, "lxml")
        except:
            print(f"connection to {book_url}failed")
            return None

        try:
            book_dict = self.parse_book_info(book_url, html_soup)
            return book_dict
        except:
            print("Error encountered in scraping due to parsing errors.")
            return None


if __name__ == "__main__":
    BOOK_URL = "https://www.goodreads.com/book/show/3735293-clean-code"  # (OK)
    scraper = BookScraper()
    print(scraper.scrape_book(BOOK_URL))
