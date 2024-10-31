import { initialState, store, handleError, updateSignIn, addLoadingReason, removeLoadingReason } from '../../reducer/reducer.js';
import { useState, useEffect } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { Form, Button } from 'react-bootstrap';

import axios from 'axios';

const SearchBar = () => {

    const [session, setSession] = useState(initialState.session);
    const [currentActor, setCurrentActor] = useState(store.getState().session.currentActor);
    const [handle, setHandle] = useState('');

    store.subscribe(() => {
        setCurrentActor(store.getState().session.currentActor);
    })

    const parseHandle = (input) => {
        if (input.charAt(0) === '@') {
            input = input.substring(1, input.length);
        }
        const parts = input.split('@');
        const username = parts[0]
        const hostname = parts[1]
        return [username, hostname]
    }

    const processProxyResponse = (res) => {

        if (res.data !== undefined) {

            const params = {
                ['@context']: 'https://www.w3.org/ns/activitystreams',
                type: 'Follow',
                actor: currentActor.id,
                object: res.data.id
            }

            const loadingReason = `Sending follow request to ${res.data?.preferredUsername}`;
            store.dispatch(addLoadingReason(loadingReason));
            axios.post(`/api/v1/actors/${currentActor.username}/outbox`, params)
                .then((res) => {
                    console.log(res.data);
                })
                .catch(handleError)
                .finally(() => {
                    store.dispatch(removeLoadingReason(loadingReason));
                });
        } else {

        }
    }

    const onSubmit = (e) => {
        e.preventDefault();
        const loadingReason = 'Looking up user';
        store.dispatch(addLoadingReason(loadingReason));
        const [username, hostname] = parseHandle(handle);
        axios.get(`/api/v1/proxy?type=actor&username=${username}&hostname=${hostname}`)
            .then(processProxyResponse)
            .catch(handleError)
            .finally(() => {
                store.dispatch(removeLoadingReason(loadingReason));
            });
    }

    return (
        <Form className="input-part" onSubmit={onSubmit}>
            <Form.Control
                id="user-search"
                placeholder="e.g. user@mastodon.online"
                onChange={(e) => setHandle(e.target.value)}
                style={{ boxShadow: '0', border: '0' }}
            />
            <Button type="submit" id="search-button">Follow</Button>
        </Form>
    );

}

export default SearchBar;
