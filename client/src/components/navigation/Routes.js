import React, { useState, useEffect } from 'react';
import { Switch, Route } from 'react-router-dom';

import Error404 from 'components/static/Error404.js';
import About from 'components/static/About.js';
import Home from 'components/Home.js'
import NotificationCenter from 'components/NotificationCenter.js'
import ViewActors from 'components/session/ViewActors.js';
import ComposeNote from 'components/notes/ComposeNote.js';
import InboxViewer from 'components/InboxViewer.js.js';
import OutboxViewer from 'components/OutboxViewer.js';
import Following from 'components/Following.js';
import Followers from 'components/Followers.js';
import Reply from 'components/Reply.js';
import LikedViewer from 'components/LikedViewer.js';

import { store } from 'reducer/reducer.js';



const Routes = () => {

    const [actors, setActors] = useState([]);

    useEffect(() => {
        store.subscribe(() => {
            setActors(store.getState().session.actors);
        });
    }, []);

    return (
        <Switch>
            <Route exact path="/" render={() => <Home />} />
            <Route exact path="/about" render={() => <About />} />
            <Route exact path="/actors" render={() => <ViewActors actors={actors} />} />
            <Route exact path="/compose" render={() => <ComposeNote />} />
            <Route exact path="/inbox" render={() => <InboxViewer/>} />
            <Route exact path="/notifications" render={() => <NotificationCenter />} />
            <Route exact path="/outbox" render={() => <OutboxViewer/>} />
            <Route exact path="/following" render={() => <Following />} />
            <Route exact path="/followers" render={() => <Followers />} />
            <Route exact path="/reply" render={() => <Reply />} />
            <Route exact path="/liked" render={() => <LikedViewer/>} />
            <Route render={() => <Error404 />} />
        </Switch>
    );

}

export default Routes;