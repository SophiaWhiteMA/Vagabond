import React from 'react';

const ViewActors = (props) => {

    return (
        <>
            <h1>My Actors</h1>
            {
                props.actors.map(
                    (actor, index) =>
                        <>
                            <div className="user-on-list" style={{height:"90px"}}>
                                <div id="user-url">
                                    Username: {JSON.stringify(actor.username, null, 2).replace(/\"/g,"")}
                                    <br/>
                                    Preferred Name: {JSON.stringify(actor.preferredUsername, null, 2).replace(/\"/g,"")}
                                </div>
                                <button style={{backgroundColor:'lightGray'}} className="unfollow">Current</button>
                            </div> 
                        </>
                )
            }
        </>
    );
}

export default ViewActors;