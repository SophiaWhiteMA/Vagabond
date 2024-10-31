import axios from 'axios';
import { useState, useEffect } from 'react';
import {addLoadingReason, handleError, removeLoadingReason, store} from 'reducer/reducer.js';
import {Button} from 'react-bootstrap';
import { ReactComponent as NotFound } from 'icon/404.svg';


/**
 * props:
 *  - id: str URL of OrderedCollection object
 *  - autoload: bool whether or not the entire collection should be automatically loaded when component renders for the first time
 *  - render: func Used for item mapping + rendering
 *  - visible? bool If set to false, the component renders an empty react fragment. This results in loading data but not diplaying it. Only use case so far is LeftBar.js
 */
const OrderedCollectionViewer = (props) => {

    const [collection, setCollection] = useState(store.getState().collections[props.id]);
    const [session, setSession] = useState(store.getState().session);

    /**
     * Takes a URL and removes the domain and protocol from it leaving only the target resource.
     * Required to avoid CORS issues due to development versus production having different domains.
     * @param {*} url 
     * @returns 
     */
    const stripUrl = (url) => {
        if(!url) {
            return url;
        }
        let output = '';
        let splits = url.replace('https://', '').replace('http://', '').split('/')
        for(let i = 1; i < splits.length; i++){
            output = output + '/' + splits[i]; 
        }
        return output;
    }

    store.subscribe(() => {
        setCollection(store.getState().collections[props.id]);
        setSession(store.getState().session);
    });

    /** Once we're signed in, determine the size of the collection and the max ID of the collection */
    useEffect(() => {
        if(collection === undefined && session.signedIn === true) {
            initialize();
        }
    }, [session.signedIn]);

    /**Once we fetch the size of the collection, load the first page */
    useEffect(() => {
        if((collection?.items === null && !isButtonDisabled()) || (collection?.items?.length >= 0 && props.autoload === true && !isButtonDisabled())) {
            loadNextPage();
        }
    }, [collection?.items]);

    const loadNextPage = () => {
        const loadingReason = `Fetching contents of ${props.id}`;
        store.dispatch(addLoadingReason(loadingReason));
        axios.get(`${stripUrl(collection.nextPage)}`)
            .then((res) => {
                const newCollection = {
                    ...collection,
                    items: collection.items === null ? [...res.data.orderedItems] : [...collection.items, ...res.data.orderedItems],
                    nextPage: stripUrl(res.data.next)
                };
                store.dispatch({
                    type: 'SET_COLLECTION',
                    id: props.id,
                    collection: newCollection
                });
            })
            .catch(handleError)
            .finally(() => {
                store.dispatch(removeLoadingReason(loadingReason));
            })
    }

    const initialize = () => {
        const loadingReason = `Determining size of collection: ${props.id}`;
        store.dispatch(addLoadingReason(loadingReason));
        axios.get(props.id)
        .then((res) => {
            store.dispatch({
                type: 'SET_COLLECTION',
                id: props.id,
                collection: {
                    nextPage: stripUrl(res.data.first),
                    totalItems: res.data.totalItems,
                    items: null
                }
            });
        })
        .catch(handleError)
        .finally(() => {
            store.dispatch(removeLoadingReason(loadingReason));
        });
    }

    const isButtonDisabled = () => {
        return (collection?.items?.length >= collection?.totalItems) || collection?.totalItems === 0;
    }

    const SignedOut = () => {
        return (
            <p>
                
            </p>
        )
    }

    const EmptyCollection = () => {
        return (
            <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                <NotFound style={{width:'90%',margin:'20px 0 20px 0'}}/>
                <p style={{color: 'white',textAlign:'center',margin:'30px 20px 30px 20px'}}>There don't appear to be any items in the collection {`${props.id}`}.</p>
            </div>

        );
    }

    if(props.visible === false) {
        return (<></>);
    }

    /** Return different components depending on whether or not the person is signed or and if the data has been loaded. **/
    if(session.signedIn !== true) {
        return <SignedOut/>
    } 
    else if(collection?.items?.length >= 1) {
        return (
            <>
                {
                    collection.items.map((item) => {
                        return props.render(item);
                    })
                }
                {
                    !props.autoload &&
                    <Button
                        onClick={loadNextPage}
                        disabled={isButtonDisabled()}
                        style={{ display: 'flex', margin: '16px auto', width: '92%'}}
                        variant={isButtonDisabled() ? 'secondary' : 'primary'}
                    >
                        <div style={{width: '100%', textAlign: 'center'}}>
                            {isButtonDisabled() ? 'No more to load' : 'Load more'}
                        </div>
                    </Button>
                }
            </>
        )
    } else {
        return <EmptyCollection/>
    }

}

export default OrderedCollectionViewer;