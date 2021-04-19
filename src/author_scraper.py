"""Author Scraper"""
import re
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.goodreads.com"


class AuthorScraper():
    """
    Interface wrapper class for scraping author information, one at a time.
    """

    def parse_author_info(self, author_url, soup_html):
        """
        Extract the author information (name, url) from a given book page html.
        :param soup_html: the result of injecting src_html into bs4
        :param author_url: the url of author to extract
        :return: a dictionary of author attributes as required in the rubric
        """
        author_attrs = ["author_name", "author_id", "author_url", "rating_count", "review_count",
                        "rating_value", "image_url", "related_authors", "author_books"]
        author_dict = {attr: None for attr in author_attrs}
        try:
            author_dict["author_url"] = author_url  # url of author
            author_dict["author_name"] = soup_html.select("h1.authorName > span")[0].text.strip()
            author_dict["author_id"] = re.findall(r"https://www.goodreads.com/author/show/(\d*).*",
                                                  author_url)[0]
            rating_selector = "div.hreview-aggregate > span.rating > span.average"
            author_dict["rating_value"] = float(soup_html.select(rating_selector)[0].text.strip())

            rating_count_selector = "div.hreview-aggregate > span.votes"
            rating_count = soup_html.select(rating_count_selector)[0].text.strip()
            author_dict["rating_count"] = int(rating_count.replace(",", ""))
            # author_dict["rating_count"] = soup_html.select(rating_count_selector)[0].text.strip()

            review_count_selector = "div.hreview-aggregate > span.count"
            review_count = soup_html.select(review_count_selector)[0].text.strip()
            author_dict["review_count"] = int(review_count.replace(",", ""))
            # author_dict["review_count"] = soup_html.select(review_count_selector)[0].text.strip()

            author_dict["author_books"] = self.extract_author_book_urls(author_url)
            author_dict["related_authors"] = self.extract_similar_author_urls(author_url)
            image_url_selector = f"img[alt=\"{author_dict['author_name']}\"]"
            author_dict["image_url"] = soup_html.select(image_url_selector)[0]["src"]

        except:
            for attr in author_attrs:
                if author_dict[attr] is None:
                    print(f'{attr} retrieval in AUTHOR {author_url} failed')

        return author_dict

    def construct_similar_author_url(self, author_url):
        """Construct url of related authors for target author"""
        author_suffix = re.findall(r"^https://www.goodreads.com/author/show/(.*)$",
                                   author_url)[0]
        return BASE_URL + "/author/similar/" + author_suffix

    def construct_author_book_list_url(self, author_url):
        """Construct url of book list  for target author"""
        author_suffix = re.findall(r"^https://www.goodreads.com/author/show/(.*)$",
                                   author_url)[0]
        return BASE_URL + "/author/list/" + author_suffix

    def extract_from_external_url(self, author_url, ex_url, selector, prefix=BASE_URL):
        """
        Extract the href info from external url (similar_author or book_list).
        Notice this function DO NOT HANDLE error!
        Error can occur!
        :param author_url: the url of the author
        :param ex_url: either similar_author or book_list url
        :param selector: the selector for the a.href element
        :param prefix: the prefix for constructing url
        :return: a list of similar_author or authored_book urls
        """
        ex_html = requests.get(ex_url).text
        soup_ex = BeautifulSoup(ex_html, "lxml")
        scraped_urls = set()
        for a_elem in soup_ex.select(selector):
            href = a_elem["href"]
            if href == author_url:
                continue
            scraped_urls.add(prefix + href)
        return list(scraped_urls)

    def extract_similar_author_urls(self, author_url):
        """Given the url of an author's similar authors
        (e.g. https://www.goodreads.com/author/similar/45372.Robert_C_Martin),
        extract all the authors listed in the page.
        @return list of similar authors
        """
        try:
            similar_author_page_url = self.construct_similar_author_url(author_url)
            selector = 'a[href^="https://www.goodreads.com/author/show"]'
            return self.extract_from_external_url(author_url, similar_author_page_url,
                                                  selector, "")  # error could occur!
        except:
            print("Extraction of similar author urls failed ...")
            return None

    def extract_author_book_urls(self, author_url):
        """Given the url of author's list of book
        (e.g. https://www.goodreads.com/author/list/45372.Robert_C_Martin),
        extract all the urls of books in the pagQe.
        :param: author_url as described above.
        :return: list of book urls listed in the given page
        """
        try:
            author_book_page_url = self.construct_author_book_list_url(author_url)
            selector = 'a[href^="/book/show"]'
            return self.extract_from_external_url(author_url, author_book_page_url,
                                                  selector)  # error could occur!
        except:
            print("Extraction of author book list failed ...")
            return None

    def scrape_author(self, author_url):
        """
        The enter interface that tunes the collaboration of all other methods.
        :param author_url: the url of one author from goodread.
        (e.g. "https://www.goodreads.com/author/show/45372.Robert_C_Martin")
        :return: a dictionary of required author attributes
        """
        soup_html = None
        try:
            assert len(re.findall(r'^(https://www.goodreads.com/author/show/.*)$', author_url)) != 0
        except:
            print("Input author url is illegal")
            return None
        try:
            html_src = requests.get(author_url).text
            soup_html = BeautifulSoup(html_src, "lxml")
        except:
            print(f"Connection to {author_url} failed...")
        try:
            author_dict = self.parse_author_info(author_url, soup_html)
            return author_dict
        except:
            print("Scraping failed due to parsing error.")
            return None


if __name__ == "__main__":
    AUTHOR_URL = "https://www.goodreads.com/author/show/17330820.Misha_Yurchenko"
    scraper = AuthorScraper()
    print(scraper.scrape_author(AUTHOR_URL))
