import React from 'react';
import 'css/App.css';

const TextArea = (props) => {

    const _props = {...props}
    _props.className = "vagabond " + (props.className ? props.className : "");

    return (
        <textarea{..._props} >
            {props.children}
        </textarea>
    );

}

export default TextArea;