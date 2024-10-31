import React, { useState, useEffect } from 'react';
import { Button, Form, Modal } from 'react-bootstrap';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import axios from 'axios';
import { useHistory } from 'react-router-dom';
import { store, handleError, initialState, updateSignIn, updateSignUp, addLoadingReason, removeLoadingReason } from 'reducer/reducer.js';
import 'css/App.css'
import SignUp from 'components/session/SignUp.js'

const SignIn = () => {

    const [show, setShow] = useState(initialState.showSignIn);
    const [signUp, setSignUp] = useState(initialState.showSignUp);

    // Closes the popup, including sign in and sing up, resets to sign in

    const handleClose = () => {
        store.dispatch(updateSignIn(false));
        store.dispatch(updateSignUp(false));
    }


    store.subscribe(() => {
        setShow(store.getState().showSignIn);
        setSignUp(store.getState().showSignUp);
    })


    const initialValues = {
        username: '',
        password: ''
    }

    const onSubmit = (values) => {
        const loadingReason = 'Signing in';
        store.dispatch(addLoadingReason(loadingReason))
        axios.post('/api/v1/signin', formik.values)
            .then((res) => {
                store.dispatch({ type: 'SET_SESSION', session: { ...store.getState().session, ...res.data } });
                store.dispatch(updateSignIn(false));
            }).catch(handleError)
            .finally(() => {
                store.dispatch(removeLoadingReason(loadingReason))
            });
    }

    const validationSchema = Yup.object().shape({
        username: Yup.string().required('This field is required.'),
        password: Yup.string().required('This field is required.')
    });

    const formik = useFormik({
        initialValues: initialValues,
        onSubmit: onSubmit,
        validationSchema: validationSchema,
        validateOnMount: true
    });

    return (
        <>
            <Modal show={show}>
                {
                    !signUp &&
                    <>
                        <Modal.Header>
                            <Modal.Title>Sign In</Modal.Title>
                            <button id="close" onClick={handleClose}>X</button>
                        </Modal.Header>
                        <Modal.Body>
                            <Form onSubmit={formik.handleSubmit}>
                                <Form.Group>
                                    <Form.Label htmlFor="username">Username</Form.Label>
                                    <Form.Control name="username" id="username" onChange={formik.handleChange} />
                                </Form.Group>
                                <Form.Group>
                                    <Form.Label htmlFor="password">Password</Form.Label>
                                    <Form.Control type="password" name="password" id="password" onChange={formik.handleChange} />
                                </Form.Group>
                                <Form.Group className="button-area">
                                    <Button className="modal-button" variant="primary" type="submit" disabled={Object.keys(formik.errors).length > 0}>Sign in</Button>
                                    <Form.Text style={{ marginTop: '5px' }}>Need an account? <b className="signup-toggler" onClick={() => store.dispatch(updateSignUp(true))}>Sign Up</b></Form.Text>
                                </Form.Group>
                            </Form>
                        </Modal.Body>
                    </>
                }
                {
                    signUp && <SignUp />
                }

            </Modal>


        </>
    );

}

export default SignIn;