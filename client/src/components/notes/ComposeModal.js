

import React, { useState } from 'react';
import { Modal } from 'react-bootstrap';

import { store } from 'reducer/reducer.js';
import ComposeNote from 'components/notes/ComposeNote';

const ComposeModal = () => {

    const [show, setShow] = useState(store.getState().compose);

    store.subscribe(() => {
        setShow(store.getState().compose);
    });

    return (
        <>
            <Modal show={show}>
                <Modal.Body style={{ margin: '0', width: '100%', padding: '10px', display: 'flex', flexDirection: 'column' }}>
                    <ComposeNote cancel={true}/>
                </Modal.Body>
            </Modal>
        </>
    );

}

export default ComposeModal;