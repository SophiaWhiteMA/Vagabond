import React, { useState } from 'react';
import { store, hideNotification } from 'reducer/reducer.js';
import {Modal, Button} from 'react-bootstrap';

const NotificationModal = () => {

    const [notifications, setNotifications] = useState([]);

    store.subscribe(() => {
        setNotifications(store.getState().notifications);
    })

    const hide = () => {
        store.dispatch(hideNotification());
    }

    return (
        <Modal show={notifications.length > 0} onHide={hide}>
            <Modal.Header>
                <Modal.Title>{notifications.length > 0 ? notifications[0].title : ''}</Modal.Title>
                <button id="close" onClick={hide}>X</button>
            </Modal.Header>
            <Modal.Body style={{width:'80%',marginLeft:'auto',marginRight:'auto'}}>{notifications.length > 0 ? notifications[0].message : ''}</Modal.Body>
            <Button className="modal-button" style={{marginBottom:'30px'}} variant="primary" onClick={hide}>OK</Button> 
        </Modal>
    );
}

export default NotificationModal;