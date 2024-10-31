import React, { useEffect, useState } from "react"
import axios from 'axios';
import { store, handleError, addLoadingReason, removeLoadingReason, updateReply } from "reducer/reducer";
import Note from "components/notes/Note.js"
import ComposeNote from "components/notes/ComposeNote.js"
import OrderedCollectionViewer from "./OrderedCollectionViewer";


const Reply = () => {

    const [reply, setReply] = useState(store.getState().reply);

    useEffect(() => {
        if(store.getState().reply === undefined) {  setReply(JSON.parse(localStorage.getItem('URL'))) }
        else { 
            setReply(store.getState().reply); 
            localStorage.setItem('URL', JSON.stringify(reply)) 
        }
    }, []);

    return (
        <>
            <h1>New Reply</h1>
            <div id="replier" style={{backgroundColor:'lightgray',padding:'10px 0 10px 0',display:'flex',flexDirection:'column',alignItem:'center',justifyContent:'center',margin:'0 20px 0 20px',borderRadius:'10px'}}>
                { reply === undefined &&  <Note note={JSON.parse(localStorage.getItem('URL'))}/> }
                { reply !== undefined &&  <Note note={reply}/> }
                <div style={{height:'30px',backgroundColor:'gray',width:'15px',margin:'0px 0 0px 50px'}} ></div>
                <div style={{width:'90%',margin:'0 auto 0 auto'}}>
                    { reply === undefined && <ComposeNote inReplyTo={JSON.parse(localStorage.getItem('URL'))} cancel={false}/>}
                    { reply !== undefined && <ComposeNote inReplyTo={reply} cancel={false}/> }    
                </div>
            </div>
            {
                reply?.replies !== undefined &&
                <>
                    <h1>Existing Replies</h1>
                    <OrderedCollectionViewer id={reply.replies} render={(item) => { return <Note note={item} id={item.id} />}} />
                </>
            } 
        </> 
    );
}

export default Reply;