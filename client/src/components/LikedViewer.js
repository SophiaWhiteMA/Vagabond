
import OrderedCollectionViewer from 'components/OrderedCollectionViewer.js';
import Note from 'components/notes/Note.js';

import {useState} from 'react';
import {store} from 'reducer/reducer.js';

const LikedViewer = () => {

    const [session, setSession] = useState(store.getState().session);

    store.subscribe(() => {
    
        setSession(store.getState().session);
    })

    const render = (item) => {
        if(item.object?.id !== undefined && item.object?.type == 'Note') {
            return <Note note={item.object} like={item} key={item.id} />

        }
    }

    if(session.currentActor?.username !== undefined) {
        return (
            <>
                <h1>My Likes</h1>
                <OrderedCollectionViewer id={`/api/v1/actors/${session.currentActor.username}/liked`} render={render} />
            </>
        )
    } else {
        return <></>
    }



}

export default LikedViewer;