import React, { useState } from 'react';

import { store } from 'reducer/reducer.js';
import OrderedCollectionViewer from './OrderedCollectionViewer';


const Following = () => {

    const [session, setSession] = useState(store.getState().session);

    store.subscribe(() => {
        setSession(store.getState().session)
    });

    const render = (item) => {
        return (
            <div className="user-on-list">
                <div id="user-url">{item}</div>
            </div>
        )
    }

    return (
        <>
            <h1>Followers</h1>
            {
                session.currentActor?.username !== undefined &&
                <OrderedCollectionViewer id={`/api/v1/actors/${session.currentActor.username}/followers`} render={render} />
            }
        </>
    )

}

export default Following;
