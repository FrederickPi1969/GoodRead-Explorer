import React from 'react';
import ReactDOM from 'react-dom';
import { JsonToTable } from "react-json-to-table";
import ReactPaginate from 'react-paginate';

class JSONRender extends React.Component {
    /**
     * Add html component to convert JSON to table
     * for scenes where we get a responsive JSON file,
     * and we don't want to directly display it as string.
     */

    constructor(props) {
        super(props);
    }
    
    trimList() {
        /**
         * Place keys whose values are Array to end.
         * This will make rendered table prettier.
         */
        let listAttr = [];
        let attrValues = [];
        for (let attr in this.props.json) {
            if (Array.isArray(this.props.json[attr])) {
                let dict = {};
                for (let i = 0; i < this.props.json[attr].length; i++) {
                    dict[i] = this.props.json[attr][i];
                }
                listAttr.push(attr);
                attrValues.push(dict);
                delete this.props.json[attr];
            }
        }
        // Ordering list elements to end of json
        for (let i = 0; i < listAttr.length; i++) {
            let attr = listAttr[i]; 
            let dict = attrValues[i];
            this.props.json[attr] = dict;
        }
    }

    getTableHeader() {
        /**
         * Get title for header of rendered table.
         * @return {string} book_title or author_name
         */
        if ('book_id' in this.props.json) {
            return this.props.json['book_title'];
        } else {
            return this.props.json['author_name'];
        }
    }

    render() {
        this.trimList()
        return (
            <div className="App">
              <h2>{this.getTableHeader()}</h2>
              <JsonToTable json={this.props.json} />
            </div>
          );
    }
}

class JSONDemonstrator extends React.Component {
    constructor(props) {
        super(props);
        this.state = {currentPage : 0}
    }

    handlePageClick(clickInfo) {
        /**
         * Set currentPage in state to users' selection
         * when a different page is clicked.
         */
        this.setState({currentPage :clickInfo.selected}) // starts from  0 !!!
    }
    
    render() {
        return(
            <div id="json_demonstrator">
            <JSONRender json={this.props.json[this.state.currentPage]}/>
            <ReactPaginate
                previousLabel={"Prev"}
                nextLabel={"Next"}
                pageCount={this.props.json.length}
                onPageChange={info=>this.handlePageClick(info)}
                containerClassName={"pagination"}
                previousLinkClassName={"pagination__link"}
                nextLinkClassName={"pagination__link"}
                disabledClassName={"pagination__link--disabled"}
                activeClassName={"pagination__link--active"}
            />
            </div>
        );
    }
}


let renderJSON = function(inputJSON) {
    /**
     * Interface for adding the JSON Render into HTML.
     * @param inputJSON A JSON file in the Array form to be rendered.
     */
    if (inputJSON.length === 0) {
        const noResults = <h1> No results found in database </h1>;
        React.render(noResults, document.getElementById('root'));
    } else {
        let json = inputJSON;
        // ReactDOM.render(<JSONRender json={json}/>, document.getElementById("root"));        
        ReactDOM.render(<JSONDemonstrator json={json}/>, document.getElementById('root'));        
    }   
}


export {renderJSON};