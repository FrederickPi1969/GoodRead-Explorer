"""
Handles the main-subcommand draw graph
"""
from matplotlib import pyplot as plt
import networkx as nx
import numpy as np
from mongo_manipulator import connect_to_mongo


def find_author_index(book_dic, author2index):
    """
    Locate the author of a book.
    :param book_dic: the a dict info of target book
    :return: the author index if found, None otherwise
    """
    author = book_dic["author_url"]
    author_index = author2index.get(author, None)
    return author_index


def find_similar_books_indices(book_dic, book2index):
    """
    Extract indices of similar books in matrix.
    :param book_dic: info of target book
    :return: np array of indices of similar books
    """
    similar_books = book_dic["similar_book_urls"]
    if similar_books is None:
        return np.array([], dtype=int)
    indices = []
    for book_url in similar_books:
        book_index = book2index.get(book_url, None)
        if book_index is not None:
            indices.append(book_index)
    return np.array(indices, dtype=int)


def find_related_authors_indices(author_dic, author2index):
    """
    Extract indices of related authors in matrix
    :param author_dic : info of target author
    :return: np array of indices of related authors
    """
    related_authors = author_dic["related_authors"]
    if related_authors is None:
        return np.array([], dtype=int)
    indices = []
    for author_url in related_authors:
        author_index = author2index.get(author_url, None)
        if author_index is not None:
            indices.append(author_index)
    return np.array(indices, dtype=int)


def build_adjacency_matrix(books, authors, dict_wrapper):
    """
    Build the book-author adjacency matrix.
    :param books: list of dict for book info
    :param authors: list of dict for author info
    :return: a matrix of shape [book_num + author_num, book_num + author_num]
    previous book_num indices are nodes for books,
    and latter author_num indices indices for authors.
    """
    total_nodes = len(books) + len(authors)
    # first total_books indices are book nodes
    adj_mat = np.zeros([total_nodes, total_nodes])
    index2book, book2index, index2author, author2index = dict_wrapper
    for i,book_dic in enumerate(books):
        author_idx = find_author_index(book_dic, author2index)  # author matrix index
        if author_idx is not None:
            adj_mat[i, len(books) + author_idx] = 1  # add book-author edge
        similar_book_idx = find_similar_books_indices(book_dic, book2index)
        adj_mat[i, similar_book_idx] = 1  # add book-book edge

    for i,author_dic in enumerate(authors):
        author_dic = authors[i]
        similar_author_idx = find_related_authors_indices(author_dic, author2index)
        adj_mat[len(books) + i, similar_author_idx] = 1  # add author-author edge

    return adj_mat


def truncate_str(index, input_str, max_len=20):
    """
    Truncate overly long string to 20 chars at most
    :param index: the index of input in the matrix
    :param input_str: input string
    @param max_len: maximum len to be truncated
    :return: f"{index} - {truncated_string}"
    """
    prefix = str(index) + "-"
    return prefix + (input_str if len(input_str) <= max_len
                     else input_str[:20] + "...")


def extract_graph_label(books, authors):
    """
    Extract the book_title / author_name for books / authors
    :param books: authors list of dic
    :return: the dictionary of labels to be used in graph
    """

    book_labels = [truncate_str(i, books[i]["book_title"]) for i in range(len(books))]
    author_labels = [truncate_str(i, authors[i]["author_name"]) for i in range(len(authors))]
    labels = book_labels + author_labels
    label_dic = {i: labels[i] for i in range(len(labels))}
    return label_dic


def draw_graph(adj_mat, books, authors):
    """
    Given the adjency matrix, pretty-draw the network.
    Result saved to ../graph_image/graph.jpg
    :param adj_mat: complete adjency matrix
    :param books: list of dict of books
    :param authors: list of dict of authors
    """
    num_books, num_authors = len(books), len(authors)
    colors = ["blue"] * num_books + ["red"] * num_authors
    graph = nx.from_numpy_matrix(adj_mat)
    isolate_idx_num = list(nx.isolates(graph))
    label_dict = extract_graph_label(books, authors)
    graph = nx.relabel_nodes(graph, label_dict)
    isolate_idx_str = list(nx.isolates(graph))
    graph.remove_nodes_from(isolate_idx_str)  # remove isolated
    colors = [c for i, c in enumerate(colors) if i not in isolate_idx_num]

    plt.figure(figsize=(100, 100))
    nx.draw(graph, node_color=colors, pos=nx.spring_layout(graph),
            node_size=1200, with_labels=True)
    plt.savefig("../graph_image/graph.jpg")
    plt.show()


def build_graph():
    """
    The enter interface for main-subcommand draw.
    :return:
    """
    book_db, author_db = connect_to_mongo()
    books, authors = list(book_db.find({})), list(author_db.find({}))
    index2book = {i: books[i]["book_url"] for i in range(len(books))}
    book2index = {book: i for i, book in index2book.items()}
    index2author = {i: books[i]["author_url"] for i in range(len(authors))}
    author2index = {author: i for i, author in index2author.items()}
    index_dict_wrapper = tuple([index2book, book2index, index2author, author2index])
    adjacency_matrix = build_adjacency_matrix(books, authors, index_dict_wrapper)
    draw_graph(adjacency_matrix, books, authors)
