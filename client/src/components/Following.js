import React, { useState } from 'react';

import { addLoadingReason, handleError, removeLoadingReason, store } from 'reducer/reducer.js';
import OrderedCollectionViewer from './OrderedCollectionViewer';

import axios from 'axios';

const Following = () => {


    const [session, setSession] = useState(store.getState().session);

    store.subscribe(() => {
        setSession(store.getState().session)
    });

    const unfollow = (url) => {
        const loadingReason = 'Unfollowing...';
        store.dispatch(addLoadingReason(loadingReason));
        axios.post('/api/v1/unfollow', {leader: url})
        .then((res) => {
                
        })
        .catch(handleError)
        .finally(() => {
            store.dispatch(removeLoadingReason(loadingReason))
        })
    }

    const render = (item) => {
        return (
            <div className="user-on-list">
                <div id="user-url">{item}</div>
                <button onClick={() => unfollow(item)} className="unfollow">Unfollow</button>
            </div>
        )
    }

    return (
        <>
            <h1>Following</h1>
            {
                session.currentActor?.username !== undefined &&
                <OrderedCollectionViewer id={`/api/v1/actors/${session.currentActor.username}/following`} render={render} />
            }
        </>
    )

}

export default Following;
