"""Execute the scrape sub command from main"""
import pickle as pk
import os
import sys
from time import sleep
from book_scraper import BookScraper
from author_scraper import AuthorScraper
from mongo_manipulator import connect_to_mongo

SEP = "=" * 120  # log separator
book_scraper = BookScraper()  # scraper wrapper for books
author_scraper = AuthorScraper()  # scraper wrapper for authors


def save_progress(bfs_queue, visited_books, visited_authors, progress_dir=None):
    """
    Save scraping progress to local.
    """
    if not os.path.isdir(progress_dir):
        os.mkdir(progress_dir)
    with open(progress_dir + "bfs_queue.pkl", "wb+") as file:
        pk.dump(bfs_queue, file)
    with open(progress_dir + "visited_books.pkl", "wb+") as file:
        pk.dump(visited_books, file)
    with open(progress_dir + "visited_authors.pkl", "wb+") as file:
        pk.dump(visited_authors, file)


def load_progress(progress_dir=None):
    """Load progress from last time."""
    with open(progress_dir + "bfs_queue.pkl", "rb+") as file:
        bfs_queue = pk.load(file)
    with open(progress_dir + "visited_books.pkl", "rb+") as file:
        visited_books = pk.load(file)
    with open(progress_dir + "visited_authors.pkl", "rb+") as file:
        visited_authors = pk.load(file)

    return bfs_queue, visited_books, visited_authors


def construct_bfs_info(is_new, start_url=None, progress_dir=None):
    """
    :param is_new: whether there is a new starting url
    :param start_url: if is_new, then start url should be provided
    :param progress_dir: the progress directory to be used
    :return: bfs_queue, visited_books, visited_authors
    """
    try:
        bfs_queue, visited_books, visited_authors = load_progress(progress_dir)
        if is_new:
            assert start_url is not None
            bfs_queue.insert(0, start_url)  # scrape the new input first!
        return bfs_queue, visited_books, visited_authors

    except:  # progress not found
        if is_new:  # this is the very first time scraping
            bfs_queue = [start_url]
            visited_books, visited_authors = set(), set()
            return bfs_queue, visited_books, visited_authors
        print("Progress data not found, please start new scraping!")
        sys.exit(1)
        return None, None, None


def scrape_start(is_new, start_url, max_book=200,
                 max_author=50, progress_dir=None):
    """
    Scraping either from new url or continue last progress.
    :param is_new: whether there is a new starting url
    :param start_url: if is_new, then start url should be provided
    :param max_book: max number of books to scrape
    :param max_author: max number of author to scrape
    :param progress_dir: the directory of previously saved progress
    """
    bfs_queue, visited_books, visited_authors =\
        construct_bfs_info(is_new, start_url, progress_dir)
    book_db, author_db = connect_to_mongo()
    continuous_failure = 0
    while len(bfs_queue) != 0:
        book_recorded = book_db.count()
        author_recorded = author_db.count()
        if book_recorded >= max_book and author_recorded >= max_author:
            print(f"currently there are {book_recorded} books,"
                  f" and {author_recorded} authors recorded."
                  f" Both max criterions are reached.\n"
                  f" Set larger max_author or max_book"
                  f" to continue scraping")
            break  # scraping done
        book_url = bfs_queue.pop(0)
        if book_url in visited_books:
            continue  # book already visited

        try:
            # scrape the information of the current book
            print(f"\n\n\n\n Working on {book_recorded + 1} / {max_book} -"
                  f" Scraping {book_url}\n" + SEP)
            book_dict = book_scraper.scrape_book(book_url)
            assert book_dict is not None

            book_id = book_dict.get("book_id")
            assert book_id is not None  # use book_id as storage key
            assert book_dict.get("book_title") is not None
            author_url = book_dict.get("author_url")
            assert author_url is not None  # make sure author is found

            book_dict["_id"] = book_id
            if not list(book_db.find({"_id": book_id})):
                book_db.insert_one(book_dict)  # make sure no duplicate

            visited_books.add(book_url)
            bfs_queue.extend(book_dict["similar_book_urls"])

            # scrape the information of author of the book
            if author_url in visited_authors:
                print("Author already recorded.")
                print(f"Currently recorded {book_recorded + 1} books,"
                      f"and {author_recorded} authors.")
                continuous_failure = 0
                continue

            sleep(3)  # don't make the IP got blocked
            author_dict = author_scraper.scrape_author(author_url)
            assert author_dict is not None, "author_dict is None"
            author_id = author_dict.get("author_id")
            assert author_dict.get("author_name") is not None,\
                "author_name is None"  # indicates scraping failed
            author_dict["_id"] = author_id

            if not list(author_db.find({"_id": author_id})):  # make sure no duplicate
                author_db.insert_one(author_dict)
            visited_authors.add(author_url)

            # update bfs queue and visited records only if scraping succeeded
            save_progress(bfs_queue, visited_books, visited_authors, progress_dir)
            continuous_failure = 0  # reset failure count
            sleep(3)
            print(f"Currently recorded {book_recorded + 1} books, "
                  f"and {author_recorded + 1} authors.")

        except:
            continuous_failure += 1
            if continuous_failure >= 5:
                break  # out IP are likely to be blocked
            print("Scraping failed ...")
