import React, { createContext } from 'react';
import ReactDOM from 'react-dom';

class SuccessDiv extends React.Component {
    /**
     * HTML component for scenes where we get a 200 response from server.
     */
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div id="success_div">
            <div style={{textAlign : "center"}}>
                <img src="/ok.png" alt="Success" width={250} height={250}/>
            </div>
            <h2 style={{fontFamily : "Comic Sans MS", textAlign : "center"}}>
                {this.props.info} </h2>
            </div>
        );
    }

}

let renderOKReport = function(info) {
    /**
     * Interface for adding the SuccessDiv into HTML.
     */
    ReactDOM.render(<SuccessDiv info={info}/>,
         document.getElementById('root'));
}


export {renderOKReport};