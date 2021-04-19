import React from 'react';
import ReactDOM from 'react-dom';
import {renderErrorReport} from './error.js';
import PostUploadDiv from './post_upload.js';
import PostScrapeDiv from './post-scrape.js';


class PostDiv extends React.Component {
    /**
     * HTML component for scenes where users want to send a
     * post request {upload_one, upload_many, scrape} to server.
     * Notice this is just a selection component.
     */
    constructor(props) {
      super(props);

    }
    handleUploadOne() {
        ReactDOM.render(<PostUploadDiv />, document.getElementById('root'));
    }
    
    handleUploadMany() {
        let status = 400;
        let errorHTML = '<html><header><header/><body><p>Please ' +
                    'directly send POST request to api/{books, authors}!</p></body></html>';
        renderErrorReport(status, errorHTML);
    }

    handleScrape() {
        ReactDOM.render(<PostScrapeDiv />, document.getElementById('root'));
    }
  
    render() {
        return (
            <div id="post_div">
                <h1 class="center">POST Requests</h1>
                <button onClick={() => this.handleUploadOne()}>
                Upload One
                </button>
                
                <button onClick={() => this.handleUploadMany()}>
                Upload Many
                </button>
                
                <button onClick={() => this.handleScrape()}>
                Scrape
                </button>
                
            </div>
        );
    }
}

export default PostDiv;