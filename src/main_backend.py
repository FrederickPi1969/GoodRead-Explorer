"""
The enter interface for backend developer.
Implements the terminal interface for BACKEND USAGE
that is, we should have direct access to the MongoDB.
It enables four subcommands: scrape, update, export, draw.
"""
import os
import re
import argparse
from gooey import Gooey
from bfs_scrape import scrape_start
from update import insert_into_db
from mongo_manipulator import dump_db
from build_graph import build_graph

PROGRESS_DIR = "../progress/"
# PROGRESS_DIR = "../progress_test/"  # for demonstration or dev only

@Gooey
def construct_parser():
    """Parsing the command line input provided by the user,
    and update constant values correspondingly.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')
    # subparser - scraper
    parser_scraper = subparsers.add_parser("scrape",
                                           help="Scrape book info."
                                                "Scraping will stop when both"
                                                "max_book or max_author are"
                                                "are both reached or exceeded.")
    parser_scraper.set_defaults(which='scrape')
    parser_scraper.add_argument('--max_book',
                                help='Stop scraping if DB book storage'
                                     ' >= max_book and author '
                                     'storage >= max_author,'
                                     ' default=200.',
                                type=int, default=200)
    parser_scraper.add_argument("--new", action="store_true",
                                help="Whether or not to start new scraping")
    parser_scraper.add_argument("--start_url", help="The start point of bfs for new book scraping.")
    parser_scraper.add_argument('--max_author',
                                help='Stop scraping if DB book storage'
                                     ' >= max_book and author'
                                     ' storage >= max_author,'
                                     ' default=50.',
                                type=int, default=50)
    # subparser  - updater
    parser_updater = subparsers.add_parser("update", help="Store new data into database.")
    parser_updater.set_defaults(which='update')
    parser_updater.add_argument("--srcJSON", required=True)
    parser_updater.add_argument("--type", choices=["book", "author"],
                                help="Flag indicating input json file"
                                     " stores book or author information")

    # subparser - exporter
    parser_exporter = subparsers.add_parser("export", help="Export existing database to json file.")
    parser_exporter.set_defaults(which='export')
    parser_exporter.add_argument("--db", choices=["book", "author", "all"], required=True,
                                 help="The database user wants to export")
    # subparser - graph_drawer
    parser_drawer = subparsers.add_parser("draw", help="Build author-book network using db data.")
    parser_drawer.set_defaults(which='draw')
    return parser


def validate_scrape_args(parser):
    """
    Error check whether input of scrape command arguments are legal
    Throw assertion errors if any breach occurs.
    :param parser: the parser object to check
    """
    args = parser.parse_args()
    if args.which == "scrape":  # action scrape
        if args.new:
            if args.start_url is None:
                parser.error("New starting book URL must be provided!")
            assert len(re.findall(r'^(https://www.goodreads.com/book/show/.*)$',
                                  args.start_url)) != 0, "URL is illegal!"
        else:
            prompt = " Please start new scraping!"
            progress_dir = os.listdir(PROGRESS_DIR)
            assert "bfs_queue.pkl" in progress_dir, "bfs_queue.pkl not found!" + prompt
            assert "visited_books.pkl" in progress_dir, "visited_books.pkl not found!" + prompt
            assert "visited_authors.pkl" in progress_dir, "visited_authors.pkl not found!" + prompt

        assert args.max_book > 0, "max_book must be a positive integer."
        assert args.max_book <= 2000, "max_book should be less than 2000."
        assert args.max_author > 0, "max_author must be a positive integer."
        assert args.max_author <= 2000, "max_author should be less than 2000."


if __name__ == "__main__":
    parser = construct_parser()
    validate_scrape_args(parser)
    args = parser.parse_args()
    if args.which == "scrape":  # run command "scrape"
        start_url = args.start_url
        max_book = args.max_book
        max_author = args.max_author
        new_scrape = args.new
        scrape_start(new_scrape, start_url, max_book,
                     max_author, PROGRESS_DIR)
    elif args.which == "update":  # run command "update"
        type_json = args.type
        src_json = args.srcJSON
        insert_into_db(src_json, type_json)
    elif args.which == "export":  # run command "export"
        db_choice = args.db
        dump_db(db_choice)
    elif args.which == "draw":  # run command "draw"
        build_graph()
    else:  # invalid input
        print("error : invalid input.")
        parser.print_help()
