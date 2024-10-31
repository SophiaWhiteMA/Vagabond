import { useState } from 'react';

import { store } from 'reducer/reducer.js';

import OrderedCollectionViewer from 'components/OrderedCollectionViewer.js';
import Note from 'components/notes/Note.js';

const OutboxViewer = () => {

    const [session, setSession] = useState(store.getState().session);

    store.subscribe(() => {
        setSession(store.getState().session);
    });

    const render = (item) => {
        if (item.type === 'Create') {
            return <Note note={item.object} key={item.id} />
        }
    }

    return (
        <>
            <h1>Outbox</h1>
            {
                session.currentActor?.username !== undefined &&
                <OrderedCollectionViewer id={`/api/v1/actors/${session.currentActor.username}/outbox`} render={render} />
            }
        </>
    )

}

export default OutboxViewer;