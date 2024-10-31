import { Form, Modal, Button } from 'react-bootstrap';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { username as usernameRegex, actor as actorRegex, password as passwordRegex } from 'util/regex.js';
import axios from 'axios';
import { handleError, store, updateSignIn, updateSignUp, addLoadingReason, removeLoadingReason } from 'reducer/reducer.js';
import 'css/App.css'

const SignUp = () => {

    const initialValues = {
        username: '',
        password: '',
        passwordConfirm: '',
        actorName: ''
    }

    const validationSchema = Yup.object().shape({
        username: Yup.string()
            .required('Required')
            .max(32)
            .matches(usernameRegex, 'Usernames can only contain letters, numbers, hypens, and underscores.'),

        password: Yup.string()
            .required('Required')
            .matches(passwordRegex, 'Passwords must be between 12 and 255 characters'),

        passwordConfirm: Yup.string()
            .required('Required')
            .oneOf([Yup.ref('password')], 'Passwords don\'t match!')
            .matches(passwordRegex, 'Passwords must be between 12 and 255 characters'),

        actorName: Yup.string()
            .required('Required')
            .max(32, 'Display name must be at most 32 characters')
            .matches(actorRegex, 'Display names can only contain letters, numbers, hypens, and underscores.')
    });

    const handleClose = () => {
        store.dispatch(updateSignIn(false));
        store.dispatch(updateSignUp(false));
    }

    const onSubmit = () => {
        const loadingReason = 'Creating account';
        store.dispatch(addLoadingReason(loadingReason));
        axios.post('/api/v1/signup', formik.values)
            .then((res) => {
                store.dispatch({ type: 'SET_SESSION', session: { ...store.getState().session, ...res.data } });
            })
            .catch(handleError)
            .finally(() => {
                handleClose();
                store.dispatch(removeLoadingReason(loadingReason));
            });

    }

    const formik = useFormik({
        initialValues: initialValues,
        validationSchema: validationSchema,
        onSubmit: onSubmit
    });

    return (
        <>
            <Modal.Header>
                <Modal.Title >Sign Up</Modal.Title>
                <button id="close" onClick={handleClose}>X</button>
            </Modal.Header>
            <Modal.Body>
                <Form onSubmit={formik.handleSubmit}>
                    <Form.Group>
                        <Form.Label htmlFor="username">Username</Form.Label>
                        <Form.Control onBlur={formik.handleBlur} id="username" name="username" placeholder="e.g., SteamTrainMaury" onChange={formik.handleChange} />
                        <Form.Text className="text-danger">{formik.getFieldMeta('username').touched && formik.errors.username}</Form.Text>
                    </Form.Group>
                    <Form.Group>
                        <Form.Label htmlFor="password">Password</Form.Label>
                        <Form.Control onBlur={formik.handleBlur} id="password" name="password" type="password" placeholder="Password..." onChange={formik.handleChange} />
                        <Form.Text className="text-danger">{formik.getFieldMeta('password').touched && formik.errors.password}</Form.Text>
                    </Form.Group>
                    <Form.Group>
                        <Form.Label htmlFor="passwordConfirm">Confirm password</Form.Label>
                        <Form.Control onBlur={formik.handleBlur} id="passwordConfirm" name="passwordConfirm" type="password" placeholder="Password..." onChange={formik.handleChange} />
                        <Form.Text className="text-danger">{formik.getFieldMeta('passwordConfirm').touched && formik.errors.passwordConfirm}</Form.Text>
                    </Form.Group>
                    <Form.Group>
                        <Form.Label htmlFor="actorName">Display name</Form.Label>
                        <Form.Control onBlur={formik.handleBlur} id="actorName" name="actorName" placeholder="e.g., Maury" onChange={formik.handleChange} />
                        <Form.Text className="text-danger">{formik.getFieldMeta('actorName').touched && formik.errors.actorName}</Form.Text>
                    </Form.Group>
                    <Form.Group className="button-area">
                        <Button className="modal-button" type="submit" disabled={Object.keys(formik.errors).length > 0}>Sign up</Button>
                        <Form.Text style={{ marginTop: '5px' }}>Already have an account? <b className="signup-toggler" onClick={() => store.dispatch(updateSignUp(false))}>Sign In</b></Form.Text>
                    </Form.Group>
                </Form>
            </Modal.Body>
        </>
    );

}

export default SignUp;