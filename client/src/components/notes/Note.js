import { ReactComponent as Heart } from 'icon/heart.svg';
import { ReactComponent as MessageSquare } from 'icon/message-square.svg';
import { ReactComponent as ArrowUpRight } from 'icon/arrow-up-right.svg';
import { ReactComponent as MoreVertical } from 'icon/more-vertical.svg';
import { ReactComponent as Trash2 } from 'icon/trash-2.svg';
import { ReactComponent as ThumbsDown } from 'icon/thumbs-down.svg';


import React, { useState } from 'react';
import { addLoadingReason, handleError, removeLoadingReason, updateReply } from 'reducer/reducer.js';
import { store } from 'reducer/reducer.js';

import { Link } from 'react-router-dom';

import axios from 'axios';
import config from 'config/config.js';


import sanitizeHtml from 'sanitize-html';

/**
 * 
 * @param {*} props
 * @param {Note} props.note - The ActivityStreams Note object being displayed by this component
 * @param {Like=} props.like - The Like activity associated with this object performed by the user. 

 * @returns 
 */
const Note = (props) => {

    const [currentActor, setCurrentActor] = useState(store.getState().session.currentActor);
    const [invisible, setInvisible] = useState(false);
    const [liked, setLiked] = useState(false);

    store.subscribe(() => {
        setCurrentActor(store.getState().session.currentActor);
    });


    const style = {
        fontSize: '13px'
    };

    const handleLike = () => {
        const currentActor = store.getState().session.currentActor;

        axios.post(`/api/v1/actors/${currentActor.username}/outbox`, {
            ['@context']: 'https://www.w3.org/ns/activitystreams',
            type: 'Like',
            object: props.note,
            to: ['https://www.w3.org/ns/activitystreams#Public'],
            cc: [props.note.attributedTo, `${config.apiUrl}/actors/${currentActor.username}/followers`]
        })
        .then((res) => {
            setLiked(true)
        })
        .catch(handleError)
    }

    const handleComment = () => {
        store.dispatch(updateReply(props.note));
    }

    const handleDelete = () => {

        const args = {
            ['@context']: ['https://www.w3.org/ns/activitystreams'],
            type: 'Delete',
            object: props.note.id,
            published: new Date().toISOString(),
            to: ['https://www.w3.org/ns/activitystreams#Public'],
            cc: [`${config.apiUrl}/actors/${currentActor.username}/followers`]
        };



        if (props.note.inReplyTo?.attributedTo !== undefined) {
            args.cc.push(props.note.inReplyTo.attributedTo);
        }

        console.log(args);

        const loadingReason = 'Deleting note'
        store.dispatch(addLoadingReason(loadingReason))
        axios.post(`/api/v1/actors/${currentActor.username}/outbox`, args)
            .then((res) => {
                setInvisible(true);
            })
            .catch(handleError)
            .finally(() => {
                store.dispatch(removeLoadingReason(loadingReason))
            })
    }

    const undoLike = () => {
        const loadingReason = 'Undoing like activity'
        store.dispatch(addLoadingReason(loadingReason));
        axios.post(`/api/v1/actors/${currentActor.username}/outbox`, {
            ['@context']: 'https://www.w3.org/ns/activitystreams',
            type: 'Undo',
            object: props.like,
            to: ['https://www.w3.org/ns/activitystreams#Public'],
            cc: [`${config.apiUrl}/actors/${currentActor.username}/followers`]
        })
        .then((res) => {
            setInvisible(true);
        })
        .catch(handleError)
        .finally(() => {
            store.dispatch(removeLoadingReason(loadingReason));
        });
    }


    const processUsername = (url) => {
        if (!url) return undefined
        let length = url.length;
        if (url.charAt(length - 1) === '/') { url = url.substring(0, length - 1); }
        const parts = url.split('/');
        return parts[parts.length - 1]
    }

    if (invisible === true) {
        return (
            <></>
        )
    }

    return (
        <div className="vagabond-tile note" style={{ padding: '15px' }}>
            <div className="pfp-container">
                <img
                    src="https://i.ibb.co/dgh810w/Ellipse-6-2.png"
                    width="100%"
                    height="auto"
                    style={{ borderRadius: '50%' }}
                    alt="PFP"
                />
            </div>
            <div className="content-container">
                <div className="user-and-time">

                    <div className="handle">{processUsername(props.note?.attributedTo)}</div>

                    <div className="time">{new Date(props.note?.published).toUTCString()}</div>
                </div>
                <div className="note-content" dangerouslySetInnerHTML={{ __html: sanitizeHtml(props.note?.content), style: { color: 'black' } }}>
                </div>
                <div className="icon-bar-horizontal" style={{ justifyContent: 'space-between' }}>
                    {
                        props.like === undefined &&
                        <div style={style}>
                            <Heart style={liked ? {fill:'red'} : {fill:'white'}} onClick={handleLike} className="note-icon" />
                        </div>
                    }
                    {
                        props.like !== undefined &&
                        <div style={style}>
                            <ThumbsDown onClick={undoLike} className="note-icon"/>
                        </div>
                    }

                    <div style={style}>
                        <Link to="/reply" title="Comment" onClick={handleComment}>
                            <MessageSquare className="note-icon" />
                        </Link>
                    </div>
                    <div style={style}>
                        <ArrowUpRight className="note-icon" />
                    </div>
                    {
                        props.note.attributedTo == `${config.apiUrl}/actors/${currentActor?.username}` &&
                        <div style={style}>
                            <Trash2 onClick={handleDelete} className="note-icon" />
                        </div>
                    }
                </div>
            </div>
            <div className="icon-bar-vertical" style={{ justifyContent: 'flex-start' }}>
                <MoreVertical className="note-icon" style={{ width: '20px', height: '20px' }} />
            </div>
        </div>
    );
}

export default Note;