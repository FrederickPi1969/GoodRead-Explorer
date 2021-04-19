import React from 'react';
import {renderErrorReport} from './error.js';
import {renderOKReport} from './success.js'
import {HOST, ROUTE_BOOK, ROUTE_AUTHOR,
    BOOK_ATTRS, AUTHOR_ATTRS, ROUTE_SCRAPE} from './main.js';

const FETCH_METHOD = 'post';
class PostScrapeDiv extends React.Component {
    /**
     * HTML component for scenes where users are trying to
     * ask server to scrape new data. Construct the scrape form.
     */
    constructor(props) {
        super(props);
        this.state = {maxAuthor : 200, maxBook : 200,
            startURL : 'https://www.goodreads.com/book/show/3735293-clean-code'};
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    async sendScrapeRequest(scrapeDict) {
        /**
         * Send POST request to server to inform server of new scraping.
         */
        let url = HOST + ROUTE_SCRAPE;
        let data = JSON.stringify(scrapeDict);
        let errorStatus, responseData;
        await fetch(url, {
            method: FETCH_METHOD,
            headers: {'Content-Type': 'application/json'},
            body: data
        })
        .then(response => {
            if (response.ok) {
                return response.text();
            } else {
                errorStatus = response.status;
                return response.text();
            }
        })
        .then(data => {
            responseData = data;
        });
        
        if (errorStatus === undefined) {
            let info = `Scraping done successfully!`;
            renderOKReport(info);
        } else {
            renderErrorReport(errorStatus, responseData);
        }
    }

    handleSubmit(event) {
        /**
         * Sanity check user input upon their submission -
         * including whether max_book and max_author can be parsed
         * into integers, and whether start_url is in good shape.
         * Send POST request if all good.
         */

        event.preventDefault();
        let scrapeDict = {};
        let maxBook = parseInt(this.state.maxBook)
        if (isNaN(maxBook) || maxBook < 0) {
            alert('Input of maxBook should be a positive integer.')
            return;
        }
        scrapeDict['max_book'] = maxBook;

        let maxAuthor = parseInt(this.state.maxAuthor)
        if (isNaN(maxAuthor) || maxAuthor < 0) {
            alert('Input of maxAuthor should be a positive integer.')
            return;
        }
        scrapeDict['max_author'] = maxAuthor
        
        let urlRegex = new RegExp('^https://www.goodreads.com/book/show/.*$')
        if (!urlRegex.test(this.state.startURL)) {
            alert('Input start URL is mal-formatted.')
            return;
        }
        scrapeDict['start_url'] = maxAuthor;
        this.sendScrapeRequest(scrapeDict);
    }

    render() {
        return(
            <div id="upload_form">
                <h1>Scrape Form</h1>
                <form id="post_scrape_form" onSubmit={this.handleSubmit}>
                    <label>Max Book: <input type="text" value={this.state.maxBook}
                    onChange={event => this.setState({maxBook : event.target.value})}/>
                    </label>

                    <label>Max Author: <input type="text" value={this.state.maxAuthor}
                    onChange={event => this.setState({maxAuthor : event.target.value})}/>
                    </label>

                    <label>Start URL: <input type="text" value={this.state.startURL}
                    onChange={event => this.setState({startURL : event.target.value})}/>
                    </label>

                    <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }

} 

export default PostScrapeDiv;