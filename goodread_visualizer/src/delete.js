
import React from 'react';
import ReactDOM from 'react-dom';
import {renderErrorReport} from './error.js';
import {renderOKReport} from "./success.js"
import {HOST, ROUTE_BOOK, ROUTE_AUTHOR} from './main.js';

const FETCH_METHOD = 'delete';

class DeleteDiv extends React.Component {
    /**
     * Add HTML component for the scene where user is trying
     * to delete one existing instance with a certain ID.
     */

    constructor(props) {
      super(props);
      this.state = {dbType: 'book', idDelete : '3735293'};
      this.handleSubmit = this.handleSubmit.bind(this);
    }

    async sendDeleteRequest() {
        /**
         * Send delete request to backend server with given ID.
         */
        let route = this.state.dbType === 'book' ? ROUTE_BOOK : ROUTE_AUTHOR;
        let params =  new URLSearchParams({_id : this.state.idDelete})
        let url = HOST + route + "?" + params;
        let errorStatus, responseData;
        await fetch(url, {
                    method: FETCH_METHOD,
                    headers: { 'Content-type': 'application/json'}     
                }
            )
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    errorStatus = response.status;
                    return response.text();
                }
            })
            .then(data => responseData = data);
        
        if (errorStatus === undefined) {
            let dbName = this.state.dbType === 'book'? 'Book DB' : 'Author DB';
            let info = `Successfully Removed ID: ${this.state.idDelete} from ${dbName}!`;
            renderOKReport(info);
        } else {
            renderErrorReport(errorStatus, responseData);
        }
        
    }

    async handleSubmit(event) {
        /**
         * @param event Submission event
         * Sanity check & update state value per user input.
         */
        if (this.state.dbType !== 'book' && this.state.dbType !== 'author') {
            alert('Input database should either be "book" or "author".');
            this.setState({dbType: '', idDelete : ''});
            return;
        }
        event.preventDefault();
        await this.sendDeleteRequest();
    }
  
    render() {
        /**
         * Function for adding DeleteDiv to HTML.
         */
        return (
            <div id="deletion_form">
                <h1>Deletion Form</h1>
                <form onSubmit={this.handleSubmit}>
                    <label>
                        Database:
                        <input type="text" value={this.state.dbType}
                            onChange={event => this.setState({dbType: event.target.value})} />
                    </label>

                    <label>
                        ID to Delete:
                        <input type="text" value={this.state.idDelete}
                            onChange={event => this.setState({idDelete: event.target.value})} />
                    </label>
                <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }
}

export default DeleteDiv