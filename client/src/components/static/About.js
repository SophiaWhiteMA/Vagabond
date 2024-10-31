import { Button } from 'react-bootstrap';

const About = () => {

    return (
        <>
            <h1>About vagabond</h1>
            <hr />
            <p>Vagabond is a distributed, privacy-respecting social network built using the ActivityPub protocol. Vagabond is free and open source (GPLv3), and no single entity owns or controls it. This paradigm gives control and peace of mind back to the end user.</p>
            <p>Some of Vagabond's core features include a cryptographic messaging suite, anonymous registration, ephemeral identities, and the ability to erase user data at any time. </p>
            <p>Whether you're a casual user or a tech enthusist looking to create your own instance, using Vagabond is easy.</p>
            <br/>
            <Button>Get started</Button>
        </>
    );

}

export default About;