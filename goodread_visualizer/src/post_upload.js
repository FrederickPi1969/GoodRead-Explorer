import React from 'react';
import {renderErrorReport} from './error.js';
import {renderOKReport} from "./success.js"
import {HOST, ROUTE_BOOK, ROUTE_AUTHOR,
    BOOK_ATTRS, AUTHOR_ATTRS} from "./main.js";

const FETCH_METHOD = "post";

class PostUploadDiv extends React.Component {
    /**
     * HTML component for scenes where users want to upload one instance.
     * Construct the corresponding form.
     */

    constructor(props) {
        super(props);
        this.state = this.getFormAttrs();
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    
    getFormAttrs() {
        /**
         * Since we don't want to duplicate the implementation
         * of book form and author form,
         * we will need to extract attrs to be filled in the form first.
         * @return {Object} Initialized {[attrs] : ""} pairs
         */
        let dbType;
        while (true){
            dbType = prompt('What instance are you trying to create (book/author)?', 'book');
            if (dbType === 'author' || dbType === 'book') break; 
        }
        this.formAttrs = dbType === "book"? BOOK_ATTRS : AUTHOR_ATTRS;
        let state = {}
        for (let attr of this.formAttrs) {
            state[attr] = "";
        }
        return state;
    }

    async sendUploadRequest(uploadDict) {
        /**
         * Send POST requests to remote server.
         */
        let dbName = 'book_url' in this.state ? 'Book' : 'Author';
        let route = dbName === "Book" ? ROUTE_BOOK : ROUTE_AUTHOR;
        let url = HOST + route;
        let data = JSON.stringify([uploadDict]);
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
            let info = `Successfully Created ID: ${this.state._id} in ${dbName} Database!`;
            renderOKReport(info);
        } else {
            renderErrorReport(errorStatus, responseData);
        }
    }


    handleSubmit(event) {
        /**
         * 1. Sanity check user input,
         * including whether _id is provided and
         *  numeric attrs could be parsed.
         * 2. If input in good shape, call send request
         */
        event.preventDefault();
        let uploadDict = {}; 
        for (let attr in this.state) {
            if (this.state[attr] === '') {
                if (attr === '_id') {
                    alert('_id attribute must be filled.');
                    return;
                }
                uploadDict[attr] = null;
                continue;
            }
            let numericAttrs = ['rating_value', 'review_count', 'rating_count'];
            if (numericAttrs.includes(attr)) {
                if (uploadDict[attr] === null) continue;
                let numVal = parseFloat(this.state[attr]);
                if (isNaN(numVal) || numVal < 0) {
                    alert(`Illegal numeric input in ${attr}!`)
                    return;
                }
                uploadDict[attr] = numVal;
                continue;
            }
            uploadDict[attr] = this.state[attr];
        }
        this.sendUploadRequest(uploadDict);     
        return;
    }

    constructForm() {
        /**
         * Iterative adding all attrs as empty input field in HTML.
         */
        let items = []        
        for (const attr of this.formAttrs) {
            items.push(
            <label>
                {attr}: 
                <input type="text" value={this.state[attr]}
                    onChange={event => this.setState({[attr] : event.target.value})}
                />
            </label>)
        }
        return items;
    }

    render() {
        return(
            <div id="upload_form">
                <h1>{('book_url' in this.state)? 'Book':'Author'} Creation Form</h1>
                <form id="post_upload_form" onSubmit={this.handleSubmit}>
                    {this.constructForm()}
                    <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }

} 

export default PostUploadDiv;