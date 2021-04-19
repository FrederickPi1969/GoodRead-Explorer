import React from 'react';
import ReactDOM from 'react-dom';
import { Route, BrowserRouter as Router } from 'react-router-dom';
import GetDiv from './get.js';
import DeleteDiv from './delete.js'
import PutDiv from './put.js';
import PostDiv from './post.js';
import {renderRank} from './rankRenderer';
import './style.css';


const HOST = 'http://127.0.0.1:5000/';
const ROUTE_SEARCH = 'api/search';
const ROUTE_BOOK = 'api/book';
const ROUTE_AUTHOR = 'api/author';
const ROUTE_BOOKS = 'api/books';
const ROUTE_AUTHORS = 'api/authors';
const ROUTE_SCRAPE = 'api/scrape';
const BOOK_ATTRS = ['_id', 'book_id', 'book_title', 'book_url', 'cover_url',  'author_name', 'author_url',
    'ISBN', 'rating_value', 'rating_count', 'review_count', 'similar_book_urls'];
const AUTHOR_ATTRS = ['_id', 'author_id', 'author_name', 'author_url', 'image_url',
    'rating_value', 'rating_count', 'review_count', 'author_books', 'related_authors'];

class MainDiv extends React.Component {
    constructor(props) {
        super(props);
        this.state = {displayWelcomePage : true};
    }   

    hideWelcomePage() {
        this.setState({displayWelcomePage : false});
    }

    showWelcomePage() {
        this.setState({displayWelcomePage : true});
    }

    handleGet() {
        this.hideWelcomePage();
        ReactDOM.render(<GetDiv />, document.getElementById('root'));
    }

    handlePut() {
        this.hideWelcomePage();
        ReactDOM.render(<PutDiv />, document.getElementById('root'));
    }

    handlePost() {
        this.hideWelcomePage();
        ReactDOM.render(<PostDiv />, document.getElementById('root'));
    }

    handleDelete() {
        this.hideWelcomePage();
        ReactDOM.render(<DeleteDiv />, document.getElementById('root'));
    }

    handleBookRanking() {
        this.hideWelcomePage();
        renderRank('book');
    }

    handleAuthorRanking() {
        this.hideWelcomePage();
        renderRank('author');
    }

    render() {
        return (
            <div id="main_div"
             style={{display : this.state.displayWelcomePage ? 'block' : 'none'}}>
                <h1 className="center">GoodRead DataBase Visualizer</h1>
                <button onClick={() => {this.handleGet()}}>
                    GET
                </button>

                <button onClick={() => {this.handlePut()}}>
                    PUT
                </button>

                <button onClick={() => {this.handlePost()}}>
                    POST
                </button>

                <button onClick={() => {this.handleDelete()}}>
                    DELETE
                </button>

                <Router>
                    <Route render={({ history}) => (
                    <button onClick={() => {
                        history.push('/vis/top-books'); 
                        this.handleBookRanking();
                        }}>
                        BookRank
                    </button>
                    )} /> 
                </Router>

                <Router>
                    <Route render={({ history}) => (
                    <button onClick={() => {
                        history.push('/vis/top-authors'); 
                        this.handleAuthorRanking();
                        }}>
                        AuthorRank
                    </button>
                    )} /> 
                </Router>
            </div>

        );
    }
}
export default MainDiv;
export {HOST, ROUTE_BOOK, ROUTE_AUTHOR, ROUTE_SEARCH, ROUTE_BOOKS,
    ROUTE_AUTHORS, ROUTE_SCRAPE, BOOK_ATTRS, AUTHOR_ATTRS};