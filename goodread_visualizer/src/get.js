import React from 'react';
import { renderErrorReport } from './error';
import { renderJSON } from './JSONRenderer.js';
import {HOST, ROUTE_BOOK, ROUTE_AUTHOR, ROUTE_SEARCH} from './main.js';

class GetDiv extends React.Component {

    async handlerSearchBook() {
        let searchID = prompt('What is the ID of the instance you are looking for?', '3735293');
        let route = ROUTE_BOOK;
        let params =  new URLSearchParams({_id : searchID})
        let searchURL = HOST + route + "?" + params;
        let responseData, errorStatus;
        await fetch(searchURL)
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        errorStatus = response.status;
                        return response.text();
                    }
                })
                .then(data => responseData = data);

        if (errorStatus !== undefined) {
            renderErrorReport(errorStatus, responseData);
        } else {
            renderJSON(responseData);
        }
    }

    async handlerSearchAuthor() {
        let searchID = prompt('What is the ID of the instance you are looking for?', '45372');
        let route = ROUTE_AUTHOR;
        let params =  new URLSearchParams({_id : searchID})
        let searchURL = HOST + route + "?" + params;
        let responseData, errorStatus;
        await fetch(searchURL)
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        errorStatus = response.status;
                        return response.text();
                    }
                })
                .then(data => responseData = data);

        if (errorStatus !== undefined) {
            renderErrorReport(errorStatus, responseData);
        } else {
            renderJSON(responseData);
        }
    }
    
    async handlerElasticSearch(){
        // let queryString = prompt("Please input the Elastic Search query string.",
                                // 'book.book_id :  "3735293"');
        let queryString = prompt('Please input the Elastic Search query string.',
                                'book.rating_value : > 4.6');
        let params =  new URLSearchParams({q : queryString})
        let searchURL = HOST + ROUTE_SEARCH + "?" + params;
        let responseData;
        let errorStatus;
        await fetch(searchURL)
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        errorStatus = response.status;
                        return response.text();
                    }
                })
                .then(data => responseData = data);

        if (errorStatus !== undefined) {
            renderErrorReport(errorStatus, responseData);
        } else {
            renderJSON(responseData);
        }
            
    }

    render() {
        return (
            <div id="buttons">
                <h1 className="center"> GET Requests</h1>
                <button onClick={this.handlerSearchBook}>
                    Find Book
                </button>

                <button onClick={this.handlerSearchAuthor}>
                    Find Author
                </button>

                <button onClick={this.handlerElasticSearch}>
                    Elastic Search
                </button>

            </div>
        );
    }
}


export default GetDiv;