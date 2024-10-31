import React, { useState, useEffect } from 'react';
import { store, handleError, removeLoadingReason, addLoadingReason } from 'reducer/reducer.js';

import OrderedCollectionViewer from 'components/OrderedCollectionViewer.js';
import { Link } from 'react-router-dom';


const LeftBar = (props) => {

    const [visible, setVisible] = useState(true);
    const [collections, setCollections] = useState(store.getState().collections);
    const [session, setSession] = useState(store.getState().session)
    const [following, setFollowing] = useState(0);
    const [followers, setFollowers] = useState(0);

    store.subscribe(() => {
        const newState = store.getState();
        setCollections(newState.collections);
        setSession(newState.session);
    });

    useEffect(() => {
        const followingUrl = `/api/v1/actors/${session.currentActor?.username}/following`;
        const followersUrl = `/api/v1/actors/${session.currentActor?.username}/followers`;
        if(collections[followingUrl] !== undefined) {
            setFollowing(collections[followingUrl].totalItems);
        } else {
            setFollowing(0);
        }
        if(collections[followersUrl] !== undefined) {
            setFollowers(collections[followersUrl].totalItems);
        } else {
            setFollowers(0);
        }
    }, [collections]);
    

    const styleBarInvisible = {
        justifyContent: 'flex-start',
        background: '#454545',
        marginTop: '30px'
    };

    const styleButtonInvisible = {
        fontSize: '18px',
        background: 'white'
    };

    const toggleVisibility = () => { setVisible(!visible); }

    return (
        <>
            {
                session.currentActor?.username !== undefined && 
                <>
                    <OrderedCollectionViewer visible={false} id={`/api/v1/actors/${session.currentActor.username}/followers`} />
                    <OrderedCollectionViewer visible={false} id={`/api/v1/actors/${session.currentActor.username}/following`} />
                </>
            }
            <div id="sidebar-left">
                <div id="hideBarLeft" style={visible ? {} : styleBarInvisible} className="sidebar-top-bar">
                    <button id="hideButtonLeft" style={visible ? {} : styleButtonInvisible} className="visibility-button" onClick={toggleVisibility}>
                        {visible ? "-" : "Profile"}
                    </button>
                </div>
                {
                    visible &&
                    <div id="leftBar" className="bar" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-start', alignItems: 'center' }}>
                        <div className="profile-pic" style={{ backgroundImage: 'url(\"https://i.ibb.co/dgh810w/Ellipse-6-2.png\")' }}></div>
                        <h1 className="dark">{session.currentActor?.username}</h1>
                        <div id="counts-parent" style={{ display: 'flex', justifyContent: 'space-around', width: '80%' }}>
                            <div id="following-parent" style={{ display: 'flex', alignItems: 'center', flexDirection: 'column' }}>
                                <Link to="/following"><h1 className="dark">{following}</h1></Link>
                                <div>Following</div>
                            </div>
                            <div id="followers-parent" style={{ display: 'flex', alignItems: 'center', flexDirection: 'column' }}>
                                <Link to="/followers"><h1 className="dark">{followers}</h1></Link>
                                <div>Followers</div>
                            </div>
                        </div>
                        <br/>
                        <div style={{width:'100%',paddingLeft:'95px'}}>
                            <Link to="/actors"><h1 className="dark" style={{fontSize:'22px',margin:'0'}}>My Actors</h1></Link>
                            <Link to="/liked"><h1 className="dark" style={{fontSize:'22px',margin:'0'}}>My Likes</h1></Link>
                            <Link to="/settings"><h1 className="dark" style={{fontSize:'22px',margin:'0'}}>Settings</h1></Link>
                        </div>
                    </div>
                }
            </div>
        </>
    );

}

export default LeftBar;