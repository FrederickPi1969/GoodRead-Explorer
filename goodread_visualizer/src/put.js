
import React from 'react';
import {renderErrorReport} from './error.js';
import {renderOKReport} from "./success.js"
import {HOST, ROUTE_BOOK, ROUTE_AUTHOR} from "./main.js";


const FETCH_METHOD = "put";

class PutDiv extends React.Component {
    /**
     * HTML component for scenes where users are trying to update
     * value of existing instances in DB.
     */
    constructor(props) {
      super(props);
      this.state = {dbType: 'book', idUpdate : '3735293',
                 updateDict: '{"book_id" : "3735293"}', updateVal : {}};
      this.handleSubmit = this.handleSubmit.bind(this);
    }

    async resetInputBox() {
        /**
         * Reinitialize input box value & state to default.
         */
        await this.setState({dbType: 'book', idUpdate : '3735293',
            updateDict: '{"book_id" : "3735293"}', updateVal : {}});
    }

    async sendPutRequest() {
        /**
         * Send PUT request to server to update value of indicated instance.
         */
        let route = this.state.dbType === 'book' ? ROUTE_BOOK : ROUTE_AUTHOR;
        this.state.updateVal['_id'] = this.state.idUpdate;
        let data = JSON.stringify(this.state.updateVal);
        let url = HOST + route;
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
            let dbName = this.state.dbType === 'book'? 'Book DB' : 'Author DB';
            let info = `Successfully Updated ID: ${this.state.idUpdate} in ${dbName}!`;
            renderOKReport(info);
        } else {
            renderErrorReport(errorStatus, responseData);
        }
    }
  
    
    async handleSubmit(event) {
        /**
         * Sanity check user input upon their submissions,
         * including shape of update dict and attempt of changing _id.
         * Send post request if all good.
         */
        event.preventDefault();
        if (this.state.dbType !== 'book' && this.state.dbType !== 'author') {
            alert('Input database should either be "book" or "author".');
            await this.resetInputBox();
            return;
        }
    
        try {
            let parsedJSON = JSON.parse(this.state.updateDict);
            await this.setState({updateVal: parsedJSON}); // await is necessary here.
            
        } catch {
            await this.resetInputBox();
            alert('Input update Dict is mal-formatted.')
            return;
        }
        
        if ('_id' in this.state.updateVal) {
            alert('Bad attempt to update instance _id.');
            return;
        }
    
        this.sendPutRequest();

            
        // await this.sendDeleteRequest();
    }
  
    render() {
        return (
            <div id="update_form">
                <h1>Update Form</h1>
                <form onSubmit={this.handleSubmit}>
                    <label>
                        Database:
                        <input type="text" value={this.state.dbType}
                            onChange={event => this.setState({dbType: event.target.value})} />
                    </label>

                    <label>
                        ID to Update:
                        <input type="text" value={this.state.idUpdate}
                            onChange={event => this.setState({idUpdate: event.target.value})} />
                    </label>

                    <label>
                        Update Dict:
                        <input type="text" value={this.state.updateDict}
                            onChange={event => this.setState({updateDict: event.target.value})} />
                    </label>
                
                <input type="submit" value="Submit" />
                </form>
            </div>
        );
    }
}

export default PutDiv