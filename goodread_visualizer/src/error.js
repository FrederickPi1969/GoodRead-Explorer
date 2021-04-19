import React, { createContext } from 'react';
import ReactDOM from 'react-dom';

const CODE2ERROR = {400 : 'Bad Request',
                    404 : 'Resource Not Found',
                    415 : 'Bad Application',
                }


class ErrorDiv extends React.Component {
    /**
     * Add html components for scenes where error occurs. 
     */

    constructor(props) {
        super(props);
    }

    render() {
        /**
         * Add components ErrorDiv into html - root.
         */
        return (
            <div id="error_div">
            <div style={{textAlign : "center"}}>
                <img src="/error.png" alt="Error Occurred" width={250} height={250}/>
            </div>
            <h1 style={{fontFamily : "Comic Sans MS", textAlign : "center"}}>
                {this.props.status}  {CODE2ERROR[this.props.status]}</h1>
            <h2 style={{fontFamily : "Comic Sans MS", textAlign : "center"}}>
                {this.props.errorMsg} </h2>
            </div>
        );
    } 

}

let extractErrorMsg = function(errorHTML) {
    /**
     * Given the error report (in HTML format)
     * from server, extract the error message.
     * @param errorHTML Error report responded by the Python server.
     * @return {string} error message.
     */
    let parser = new DOMParser();
    let soup = parser.parseFromString(errorHTML, 'text/html');
    let errorMsg = soup.getElementsByTagName("p")[0].innerHTML;
    return errorMsg;
}


let renderErrorReport = function(errorStatus, errorHTML) {
    /**
     * Interface to adding ErrorDiv component into HTML.
     */
    let errorMsg = extractErrorMsg(errorHTML);
    ReactDOM.render(<ErrorDiv status={errorStatus} errorMsg={errorMsg}/>,
         document.getElementById('root'));
}


export {renderErrorReport};
export default ErrorDiv;