"""
Interpreter for Elastic Search.
"""
import re
from mongo_manipulator import connect_to_mongo

# These are all trackable attributes for book and author db
BOOK_ATTRS = ["_id", "book_url", "book_title", "cover_url", "rating_value",
              "book_id", "rating_count", "review_count", "author_name",
              "author_url", "ISBN", "similar_book_urls"]
AUTHOR_ATTRS = ["_id", "author_name", "author_id", "author_url",
                "rating_count", "review_count", "rating_value", "image_url",
                "related_authors", "author_books"]


def parse_single_query_unit(pair):
    """
    Attempt to extract a single query pair.
    Any single query should be in the format of
    "(book/author).attr_name : (>/</NOT) query_val".
    Notice space should not matter except between "db_name.attr_name".
    :param pair: A single query pair
    :return:
    """
    match_exp = r"^(?:\s*)(book|author)\.(\S*)(?:\s*):(?:\s*)(>|<|NOT)?(?:\s*)(.*?)(?:\s*)$"
    matches = re.findall(match_exp, pair)
    # print(matches)
    assert len(matches) == 1, "Sorry, the input query string is malformatted."
    assert len(matches[0]) != 0, "Sorry, the input query string is malformatted."
    db_type, attr_name, operator, query_val = matches[0]

    # Check query is in good shape
    assert db_type != "", "DB type is missing."
    assert attr_name != "", "Query field is missing."
    assert query_val != "", "Query value is missing."
    assert ">" not in query_val and "<" not in query_val and "NOT" not in query_val, \
        "Only one comparison operator is allowed."

    # Check query field i.e. attr_name exists in db
    db_attrs = BOOK_ATTRS if db_type == "book" else AUTHOR_ATTRS
    assert ("*" in attr_name) or (attr_name in db_attrs),\
        "The query field is not tracked by the database."      # add support of "*"

    # Check for the case when ">" or "<" is given
    if operator == ">" or operator == "<":
        assert len(re.findall(r"^(\d*\.?\d*)$", query_val)) != 0, \
            "A legal input for the Query value should be a positive number."
    # Check exact matches are be properly quoted
    elif operator == "" or operator == "NOT":
        assert len(re.findall(r'^"(.*)"$', query_val)) != 0, \
            "Exact matches must be quoted."

    return db_type, attr_name, operator, query_val


def parse_query_string(query):
    """
    Assumptions
    (1) There's no nested call. e.g. (id:123 OR url:x) AND (id:321 Or url x)
    (2) There's no default field. i.e. every query must be
         in the format of "x.y:z" or "x.y:z AND/OR a.b:c".
    (3) Additionally from (2), adding comparison operator to query in (2)
        is also allowed. i.e. "x.y:(>/</NOT)z".
    (4) Each of the query value are wrapped with string.
        i.e. "z" in "x.y:z" must be quoted.
    (5) User must input full query unit i.e. "db_name.query_attr : query_value"
        around logic operator "AND" and "OR". Expression such as
        "db_name.query_attr : query_value_A OR query_value_B" is beyond the scope
        of this interpreter.
    (6) Only one logic operator "AND" or "OR is allowed in a complete query.
    This function will raise exceptions if input not parse-able.
    :param query: The query input to be parsed.
    :return:
    """
    query_units = []
    matches = re.findall(r"^(?:\s*)(.*?)(?:\s+)(AND|OR)(?:\s+)(.*?)(?:\s*)$", query)
    if len(matches) == 0:  # there's no logic connection operator
        parsed_unit = parse_single_query_unit(query)
        query_units.append(parsed_unit)
        logic_connection = "NA"
    else:  # there's matchable logic operator
        query_unit1, logic_op, query_unit2 = matches[0]
        assert "AND" not in query_unit2, "Sorry, nested logic operator is not supported."
        assert "OR" not in query_unit2, "Sorry, nested logic operator is not supported."
        query_units.append(parse_single_query_unit(query_unit1))
        query_units.append(parse_single_query_unit(query_unit2))
        assert query_unit1[0] == query_unit2[0], "Sorry, logic operator is only" \
                                                 " supported for the query of the same database."
        logic_connection = logic_op

    return query_units, logic_connection


def correct_type_query_value_of_exact_match(query_attr, query_value):
    """
    Convert exact matches string to their correct data type.
    i.e. rating_count, review_count as int, rating_value as float
    :return: converted query_value
    """
    # exact matches must be quoted.
    assert isinstance(query_value, str)
    assert query_value[0] == '"' and query_value[-1] == '"'
    query_value = query_value[1:-1]
    if query_attr == "rating_count" or query_attr == "review_count":
        return float(query_value.replace(",", ""))
    elif query_attr == "rating_value":
        return float(query_value)
    else:
        return query_value  # keep as string


def convert_wildcard_query_attr_to_query_key(query_unit):
    """
    Handle the case where we got a wildcard operator in query attr
    :param query_unit:  A parsed query unit of quadra-tuple
    :return: key of query dict to be used in mongo query
    """
    db_type, attr, comp_op, query_value = query_unit
    assert "*" in attr
    assert "*" not in query_value, "Sorry, only ONE wildcard operator at a time."
    assert comp_op == "", "Sorry, we do not support combination of " \
                          "comparison operator and wildcard operator."
    attr_regex = "^(" + attr.replace("*", ".*") + ")$"
    candidate_attr = BOOK_ATTRS if db_type == "book" else AUTHOR_ATTRS
    result_attrs = []
    for a in candidate_attr:
        if re.findall(attr_regex, a):  # matches with regex
            result_attrs.append(a)
    return {"$or": [{a: correct_type_query_value_of_exact_match(a, query_value)}
                    for a in result_attrs]}


def convert_wildcard_query_value_query_key(query_unit):
    """
    Handle the case where we got a wildcard operator in query value
    :param query_unit:  A parsed query unit of quadra-tuple
    :return: key of query dict to be used in mongo query
    """
    db_type, attr, comp_op, query_value = query_unit
    assert "*" in query_value
    assert "*" not in attr, "Sorry, only ONE wildcard operator at a time."
    assert isinstance(query_value, str)
    assert query_value[0] == '"' and query_value[-1] == '"'
    assert comp_op == "", "Sorry, combined usage of comparison and" \
                          " wildcard operators is not allowed."
    query_value = query_value[1:-1]
    value_regex = "^" + query_value.replace("*", ".*") + "$"
    book_db, author_db = connect_to_mongo()
    target_db = book_db if db_type == "book" else author_db
    match_ids = []
    #  #### "$where" not supported in MongoDB Atlas free tier
    # in {"$where": f"this.amount.toString().match({value_regex})"}
    # so we will have to manually extract id of matching objects.
    for dic in target_db.find():
        instance_val = str(dic[attr])
        if re.findall(value_regex, instance_val):
            match_ids.append(dic["_id"])
    return {"_id": {"$in": match_ids}}


def convert_to_mongo_query_key(query_unit):
    """
    Convert parsed a single parsed query unit to mongo query key
    :param query_unit: A parsed query unit of quadra-tuple
    :return:  key of query dict to be used in mongo query
    """
    _, attr, comp_op, query_value = query_unit
    if "*" in attr:
        return convert_wildcard_query_attr_to_query_key(query_unit)

    if "*" in query_value:
        return convert_wildcard_query_value_query_key(query_unit)

    if comp_op == "":
        query_value = correct_type_query_value_of_exact_match(attr, query_value)
        return {attr: query_value}
    elif comp_op == "NOT":
        query_value = correct_type_query_value_of_exact_match(attr, query_value)
        return {attr: {"$ne": query_value}}
    elif comp_op == ">":
        return {attr: {"$gt": float(query_value)}}
    elif comp_op == "<":
        return {attr: {"$lt": float(query_value)}}
    else:
        return None  # Should not be reached


def execute_parsed_query(query_units, logic_op):
    """
    Given a set of parsed query units and logic connection,
    search through the MongoDB and return matches as a list.
    :param query_units: One or two unit(s) of parsed query.
    :param logic_op: logic connection for query units
    :return: matching results as a list
    """
    assert len(query_units) != 0
    book_db, author_db = connect_to_mongo()
    db_type, _, _, _ = query_units[0]
    db = book_db if db_type == "book" else author_db

    if len(query_units) == 1:
        mongo_query_key = convert_to_mongo_query_key(query_units[0])
        return list(db.find(mongo_query_key))

    assert logic_op != "NA"
    mongo_query_key1 = convert_to_mongo_query_key(query_units[0])
    mongo_query_key2 = convert_to_mongo_query_key(query_units[1])
    result_mongo_query = {"$and": [mongo_query_key1, mongo_query_key2]} \
        if logic_op == "AND" else {"$or": [mongo_query_key1, mongo_query_key2]}
    return list(db.find(result_mongo_query))


def repl_query(query_str):
    """
    The enter interface for whole interpreter.
    Organize behavior of all other functions in this module.
    :query_str: The query string following grammar of ElasticSearch.
    :return: Matching result by the query_str as a list.
    """
    query_units, logic_op = parse_query_string(query_str)
    return execute_parsed_query(query_units, logic_op)


if __name__ == "__main__":
    pass
