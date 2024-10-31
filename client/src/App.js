
import Routes from 'components/navigation/Routes.js';
import Navigation from 'components/navigation/Navigation.js';
import { BrowserRouter as Router } from 'react-router-dom';
import NotificationModal from 'components/NotificationModal.js';
import 'css/App.css';
import { store } from 'reducer/reducer.js';
import { useEffect } from 'react';
import axios from 'axios';

import LeftBar from './LeftBar.js';
import RightBar from './RightBar.js';
import SignIn from './components/session/SignIn.js';
import Loading from 'components/Loading.js';
import ComposeModal from 'components/notes/ComposeModal.js';


const App = () => {

  useEffect(() => {
    axios.get('/api/v1/session')
      .then((res) => {
        store.dispatch({ type: 'SET_SESSION', session: { ...store.getState().session, ...res.data } });
      })
      .catch((err) => { });
  }, []);

  return (
    <>
      <ComposeModal />
      <NotificationModal />
      <SignIn />
      <Loading/>
      <Router>
          <Navigation />
          <div id="container-root">
            <LeftBar />
            <div id="container-center">
              <Routes />
            </div>
            <RightBar />
          </div>
      </Router>
    </>
  );
}

export default App;
