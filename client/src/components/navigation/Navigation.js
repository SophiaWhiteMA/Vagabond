import { ReactComponent as Users } from 'icon/users.svg'
import { ReactComponent as SignIn } from 'icon/sign-in.svg'
import { ReactComponent as SignOut } from 'icon/sign-out.svg'
import { ReactComponent as Bell } from 'icon/bell.svg'
import { ReactComponent as Inbox } from 'icon/inbox.svg';
import { ReactComponent as Feather } from 'icon/feather.svg';
import { ReactComponent as Send } from 'icon/send.svg';
import { ReactComponent as UserPlus } from 'icon/user-plus.svg';
import { ReactComponent as Logo } from 'img/Vagabond_Logo.svg';
import { initialState, store, handleError, updateSignIn, updateCompose } from 'reducer/reducer.js';

import { useState, useEffect } from 'react';
import { Link, useHistory } from 'react-router-dom';
import axios from 'axios';
import SearchBar from './SearchBar.js'

const Navigation = () => {

    const [session, setSession] = useState(initialState.session);
    const [searching, setSearching] = useState(false);

    const history = useHistory();

    useEffect(() => {
        store.subscribe(() => {
            setSession(store.getState().session);
        });
    }, []);

    const signOut = () => {
        axios.post('/api/v1/signout')
            .then((res) => {
                store.dispatch({ type: 'RESET' });
                history.push('/');
            })
            .catch(handleError)
    }

    const openSignIn = () => {
        store.dispatch(updateSignIn(true));
    }

    const openCompose = () => {
        store.dispatch(updateCompose(true));
    }

    function toggleSearchBar() {
        if(searching) setSearching(false);
        else setSearching(true);
    }

    return (

        <div className="vagabond-navbar" style={{padding: '10px'}}>
            <span className="logoAndTitle" style={{width:'25%'}}>
                <Logo style={{width:'35px', height:'35px', fill:'white', margin:'auto 10px auto 0'}}/>
                <Link to="/"  title="Inbox"  style={{margin:'0'}}>
                    <div id="vagabondTitle">Vagabond</div>
                </Link>
            </span>
            <div className={searching ? "bar-parent-searching" : ""}>
                {
                    session.signedIn &&
                    searching &&
                    <div className="search-bar">
                        <button onClick={toggleSearchBar}>X</button>
                        <SearchBar/>
                    </div>
                }
            </div>
            <span className={searching ? "icon-bar-horizontal-searching" : "icon-bar-horizontal"}>
                {
                    session.signedIn &&
                    !searching &&
                    <Link>
                        <UserPlus onClick={toggleSearchBar} className="icon"/>
                    </Link>
                }
                <Link to="/"  title="Inbox">
                    <Inbox className="icon"/>
                </Link>
                {
                    session.signedIn &&
                    <Link to="/outbox" title="Outbox">
                        <Send className="icon" />
                    </Link>
                }
                {
                    session.signedIn && 
                    <Link onClick={openCompose}  to="#" title="Compose Note">
                        <Feather className="icon" />
                    </Link>
                }
                {
                    session.signedIn &&
                    <Link to="/notifications" title="Notifications">
                        <Bell className="icon" />
                    </Link>
                }
                {

                    !session.signedIn &&
                    <SignIn className="icon" onClick={openSignIn} />
                }
                {
                    session.signedIn &&
                    <Link onClick={signOut} to="#" title="Sign out">
                        <SignOut className="icon" />
                    </Link>
                }

            </span>
        </div>
    );

}

export default Navigation;
