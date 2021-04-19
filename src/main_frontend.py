"""
The enter interface for frontend user.
Implements the terminal interface for FRONTEND USAGE.
that is, it should NOT have direct access to the MongoDB,
and will do all the commands by sending https requests to
backend server.
It enables four subcommands: get, search, scrape, update, create, delete
"""
import sys
import re
from gooey import Gooey, GooeyParser
import requests
import json
import update as updater
from update import BOOK_ATTRS, AUTHOR_ATTRS
from interpreter import parse_query_string

HOST = "http://127.0.0.1:5000/"  # The address of the server


@Gooey(optional_cols=2,
       default_size=(800, 600),
       navigation='SIDEBAR',
       tabbed_groups=True)
def construct_parser():
    """
    Parsing the command line input provided by the user,
    and update constant values correspondingly.
    """
    parser = GooeyParser()
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    # Search by ID
    search_by_id = subparsers.add_parser("search_by_id",
                                         help="Get one book or author from database by their id.")
    required = search_by_id.add_argument_group("Required Configs")
    required.set_defaults(which="search_by_id")
    required.add_argument('--db_type', help="Either book or author database.",
                          choices=["book", "author"], required=True)
    required.add_argument("--id", help="The id of the target instance in MongoDB.",
                          required=True)

    # Elastic Query
    elastic = subparsers.add_parser("elastic_search", help="Find book/author via elastic search")
    elastic.set_defaults(which="elastic_search")
    required = elastic.add_argument_group("Required Configs")
    optional = elastic.add_argument_group("Optional Configs")
    required.add_argument("--query_unit_1", required=True,
                          help="(Required) ElasticSearch query unit 1 used for locating objects")
    optional.add_argument("--logic_operator", choices=["AND", "OR"],
                          help="Logic relationship between two units.", required=False)
    optional.add_argument("--query_unit_2", required=False,
                          help="(Optional) ElasticSearch query unit 2 used for locating objects")

    # Update
    update = subparsers.add_parser("update", help="Update value of EXISTING instance in the database.")
    update.set_defaults(which="update")
    required = update.add_argument_group("Required Configs")
    required.add_argument('--db_type', help="Either book or author database.",
                          choices=["book", "author"], required=True)
    required.add_argument("--id", required=True,
                          help="The id of target object to update.")
    required.add_argument('--update_dict', required=True,
                          help="Enter the attribute-value pair used for updating."
                               " Please following the format of JSON (dict).")
    # Upload
    upload = subparsers.add_parser("upload", help="Create/Update one or more objects to database.")
    upload.set_defaults(which="upload")
    required = upload.add_argument_group("Required Configs")
    required.add_argument("--db_type", required=True, choices=["book", "author"],
                          help="Either book or author database.")
    required.add_argument('--json_path', required=True,
                          help="The source JSON file containing the target instance(s).",
                          widget="FileChooser")
    required.add_argument("--upload_many", default=False, action="store_true",
                          help="Upload more than one instances.")
    # Scrape
    scrape = subparsers.add_parser("scrape", help="Scrape new books & authors into the database.")
    scrape.set_defaults(which="scrape")
    required = scrape.add_argument_group("Required Configs")
    optional = scrape.add_argument_group("Optional Configs")
    optional.add_argument("--max_book", default=200, type=int,
                          help="After the scraping, there will be at least "
                               "max_book books in the database.")
    optional.add_argument("--max_author", default=200, type=int,
                          help="After the scraping, there will be at least "
                               "max_author authors in the database. ")
    required.add_argument("--start_url", help="URL to start new scraping.", required=True)

    # Delete
    delete = subparsers.add_parser("delete", help="Delete one book or authors specified by the id")
    delete.set_defaults(which="delete")
    required = delete.add_argument_group("Required Configs")
    required.add_argument("--db_type", required=True, choices=["book", "author"],
                          help="Either book or author database.")
    required.add_argument("--id", required=True, help="ID of instance to be removed.")
    return parser


if __name__ == "__main__":
    my_parser = construct_parser()
    args = my_parser.parse_args()

    # Main Body
    if args.which == "search_by_id":  # GET
        response = requests.get(HOST + f"api/{args.db_type}", params={"_id": args.id})
        print(response.json())

    elif args.which == "elastic_search":  # GET
        # query_unit_2 and logic operator must be set together.
        assert (args.query_unit_2 is None and args.logic_operator is None) or \
               (args.query_unit_2 is not None and args.logic_operator is not None), \
            "Logic operator and query_unit_2 must be provided simutaneously."

        query_unit_2 = "" if args.query_unit_2 is None else args.query_unit_2
        logic_op = "" if args.logic_operator is None else args.logic_operator
        q = args.query_unit_1 + " " + logic_op + " " + query_unit_2

        # Sanity check the query string - exit if passed query is not interpretable.
        parse_query_string(q)
        response = requests.get(HOST + f"api/search", params={"q": q})
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.content)

    elif args.which == "update":  # PUT
        try:
            update_dict = json.loads(args.update_dict)
        except:
            print("Sorry, your input is malformated and cannot be converted to JSON.")
            sys.exit(1)

        assert "_id" not in update_dict, "Instance attribute \"_id\" is immutable."
        update_dict["_id"] = args.id
        proper_attrs = BOOK_ATTRS if args.db_type == "book" else AUTHOR_ATTRS
        for key in update_dict.keys():
            assert key in proper_attrs, "Bad attempt to update non-existing attribute."
        response = requests.put(HOST + f"api/{args.db_type}", json=update_dict)
        print(response.content)

    elif args.which == "delete":  # DELETE
        response = requests.delete(HOST + f"api/{args.db_type}", params={"_id": args.id})
        print(response.content)

    elif args.which == "upload":  # POST
        dict_list = updater.load_json_file(args.json_path, root="")  # make sure json loadable
        required_attrs = updater.BOOK_ATTRS if args.db_type == "book" \
            else updater.AUTHOR_ATTRS  # make sure no missing attrs
        updater.check_missing_attributes(dict_list, required_attrs)
        if len(dict_list) > 1:  # whether or not to upload many instances
            assert args.upload_many, "Please set upload_many as true " \
                                    "when uploading multiple instances."
            response = requests.post(HOST + f"api/{args.db_type}s", json=dict_list)
        else:
            assert not args.upload_many, "Please set upload_many as false " \
                            "when uploading a single instance."
            response = requests.post(HOST + f"api/{args.db_type}", json=dict_list)
        print(response.content)

    elif args.which == "scrape":
        assert len(re.findall(r'^(https://www.goodreads.com/book/show/.*)$',
                              args.start_url)) != 0, "URL is illegal!"
        assert args.max_book > 0, "max_book must be a positive integer."
        assert args.max_book <= 2000, "max_book should be less than 2000."
        assert args.max_author > 0, "max_author must be a positive integer."
        assert args.max_author <= 2000, "max_author should be less than 2000."
        request_body = {"max_book": args.max_book, "max_author": args.max_author,
                        "start_url": args.start_url}
        response = requests.post(HOST + f"api/scrape", json=request_body)
        print(response.content)

    else:
        print("Invalid command")
        sys.exit(1)
