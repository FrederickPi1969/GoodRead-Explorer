"""
Backend server that accepts requests from client,
and directly interact with remote Database.
"""
import flask
from flask import request, jsonify, abort
from mongo_manipulator import connect_to_mongo
import interpreter
import update as updater
import bfs_scrape as scraper
from main_backend import PROGRESS_DIR
from flask_cors import CORS

app = flask.Flask(__name__)
app.config["DEBUG"] = True
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def check_json_in_body(request):
    """
    Check a json format file is properly included in request body.
    raise status code 415 if not.
    :param request: The request to check
    """
    if request.headers.get("Content-Type") == ""\
            or request.headers.get("Content-Type") is None:
        abort(415, "Unsupported Media Type"
                   " - content should be JSON file")
    if request.headers.get("Content-Type") != "application/json":
        abort(415, "Unsupported Media Type"
                   " - content should be JSON file")
    if request.json == [] or request.json is None or request.json == {}:
        abort(400, "Please include a"
                   " non-empty JSON file in the request body!")


@app.route("/api/book", methods=["GET", "POST", "PUT", "DELETE"])
def api_book():
    """
    Users can send GET/POST/PUT/DELETE requests to https://host/api/book?{_id, update_attr*}
    This function handles the backend behavior to response to these requests.
    """
    book_db, _ = connect_to_mongo()
    if request.method == "GET":
        try:
            query_id = request.args["_id"]
            result = list(book_db.find({"_id": query_id}))
        except:
            abort(400, "ID not provided.")
        if not result:  # no matching
            abort(400, "No matching results in book database.")
        return jsonify(result)  # invalid id will return []


    elif request.method == "POST":
        check_json_in_body(request)  # check json properly included
        dict_list = request.json  # This must be valid json as sanity test is done.
        if len(dict_list) > 1:
            abort(400, "Please send POST request"
                       " to /api/books to upload many books.")
        updater.write_given_dict_list_to_db(dict_list, book_db)
        return """Status Code [200] : Upload succeeded."""

    elif request.method == "PUT":
        check_json_in_body(request)
        try:
            update_key = {"_id": request.json["_id"]}
        except:
            abort(400, "_id not provided.")
        matches = list(book_db.find(update_key))
        if not matches:
            abort(400, "Input instance ID not found in DB.")

        update_val = {k: v for k, v in request.json.items() if k != "_id"}
        for key in update_val.keys():  # check to-be-updated attribute exists
            if key not in updater.BOOK_ATTRS:
                abort(400, "Bad attempt to update non-existing attribute.")
        if update_val == {}:
            abort(400, "Empty update value.")
        book_db.update_one(update_key, {"$set": update_val})
        return """Status code [200] : Update succeeded."""

    elif request.method == "DELETE":
        try:
            query_id = request.args["_id"]
        except:
            abort(400, "ID not provided.")
        if not list(book_db.find({"_id": query_id})):
            abort(400, "Target ID not in book_DB.")
        book_db.delete_one({"_id": query_id})
        return """Status code [200] : Delete succeeded."""


    else:
        abort(404, "Related resource not found")


@app.route("/api/author", methods=["GET", "POST", "PUT", "DELETE"])
def api_author():
    """
    Users can send GET/POST/PUT/DELETE requests to https://host/api/author?{_id, update_attr*}
    This function handles the backend behavior to response to these requests.
    """
    _, author_db = connect_to_mongo()
    if request.method == "GET":
        try:
            query_id = request.args["_id"]
            result = list(author_db.find({"_id": query_id}))
        except:
            abort(400, "ID not provided.")
        if not result:  # no matching
            abort(400, "No matching results in author database.")
        return jsonify(result)

    elif request.method == "POST":
        check_json_in_body(request)  # check json is properly passed
        dict_list = request.json  # This must be valid json as sanity test is done.
        if len(dict_list) > 1:
            abort(400, "Please send POST request"
                       " to /api/authors to upload many authors.")
        updater.write_given_dict_list_to_db(dict_list, author_db)
        return """Status Code [200] : Upload succeeded."""

    elif request.method == "PUT":
        check_json_in_body(request)
        try:
            update_key = {"_id": request.json["_id"]}
        except:
            abort(400, "_id not provided.")

        matches = list(author_db.find(update_key))
        if not matches:
            abort(400, "Target instance ID not found in DB.")
        update_val = {k: v for k, v in request.json.items() if k != "_id"}
        for key in update_val.keys():  # check to-be-updated attribute exists
            if key not in updater.AUTHOR_ATTRS:
                abort(400, "Bad attempt to update non-existing attributes.")
        if update_val == {}:
            abort(400, "Empty update value.")
        author_db.update_one(update_key, {"$set": update_val})
        return """Status code [200] : Update succeeded."""

    elif request.method == "DELETE":
        try:
            query_id = request.args["_id"]
        except:
            abort(400, "ID not provided.")
        if not list(author_db.find({"_id": query_id})):
            abort(400, "Target ID not in author_DB.")
        author_db.delete_one({"_id": query_id})
        return """Status code [200] : Delete succeeded."""

    else:
        abort(404, "Related resource not found")


@app.route('/api/books', methods=["POST"])
def api_books():
    """
    Handles clients requests to upload multiple books at a time.
    """
    book_db, _ = connect_to_mongo()
    check_json_in_body(request)  # check json properly included
    dict_list = request.json  # This must be valid json as sanity test is done.
    if len(dict_list) == 1:
        abort(400, "Please send POST request"
                   " to /api/book to upload a single book.")
    updater.write_given_dict_list_to_db(dict_list, book_db)
    return """Status Code [200] : Upload succeeded."""


@app.route('/api/authors', methods=["POST"])
def api_authors():
    """
    Handles clients requests to upload multiple authors at a time.
    """
    _, author_db = connect_to_mongo()
    check_json_in_body(request)  # check json is properly passed
    dict_list = request.json  # This must be valid json as sanity test is done.
    if len(dict_list) == 1:
        abort(400, "Please send POST request"
                   " to /api/author to upload a single author.")
    updater.write_given_dict_list_to_db(dict_list, author_db)
    return """Status Code [200] : Upload succeeded."""


@app.route('/api/search', methods=["GET"])
def api_search():
    """
    Users can send GET requests to https://host/api/book?{q}
    This function handles the backend behavior to response to requests.
    """
    try:
        query_str = request.args["q"]
    except:
        abort(400, 'Query string "q" is not'
                   ' included in request parameters')
    try:
        matches = interpreter.repl_query(query_str)
    except:
        abort(400, "Input query string is not interpretable.")

    if not matches:
        abort(400, 'No matching results. Try new query!')
    return jsonify(matches)


@app.route('/api/scrape', methods=["POST"])
def api_scrape():
    """
    Users can send POST requests to https://host/api/scrape?{max_author, max_book, start_url, new}
    This function handles the backend behavior to response to these requests.
    :return:
    """
    check_json_in_body(request)
    try:
        params = request.json
        max_book, max_author = params["max_book"], params["max_author"]
        start_url = params["start_url"]
    except:
        abort(400, "max_book, max_author, start_url"
                   " should all be provided in the request body (JSON).")
    scraper.scrape_start(is_new=False, max_author=max_author, max_book=max_book,
                         start_url=start_url, progress_dir=PROGRESS_DIR)
    return "Status Code [200]: Scrape succeeded."


def run_server():
    """
    Run the backend server
    :return:
    """
    # app.run(host="0.0.0.0")  # run on remote server
    app.run()


if __name__ == "__main__":
    run_server()
