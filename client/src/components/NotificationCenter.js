import React, { useEffect, useState } from "react"
import axios from 'axios';

import {Button} from 'react-bootstrap'; 

import { ReactComponent as UserPlus } from 'icon/user-plus.svg'
import { ReactComponent as Heart } from 'icon/heart.svg';
import { ReactComponent as ThumbsDown } from 'icon/thumbs-down.svg';
import { ReactComponent as MessageSquare } from 'icon/message-square.svg';
import { ReactComponent as AtSign } from 'icon/at-sign.svg';
import { ReactComponent as NotFound } from 'icon/404.svg';


import { store, handleError, addLoadingReason, removeLoadingReason } from "reducer/reducer";


const NotificationCenter = () => {

    const [interactions, setInteractions] = useState([]);
    const [mentions, setMentions] = useState([])
    const [showInteractions, setShowInteractions] = useState(true);

    useEffect(() => {
        const loadingReason = 'Fetching notifications';
        store.dispatch(addLoadingReason(loadingReason));
        axios.get('/api/v1/notifications')
            .then((res) => {
                let interactions = [];
                let mentions = [];
                res.data.forEach((element) => {
                    if (element.type.toLowerCase() === 'mention') {
                        mentions.push(element);
                    } else {
                        interactions.push(element);
                    }
                });
                setMentions(mentions);
                setInteractions(interactions);
            })
            .catch(handleError)
            .finally(() => {
                store.dispatch(removeLoadingReason(loadingReason));
            });
    }, []);

    const deleteNotification = (notification) => {
        axios.post('/api/v1/notifications', {
            action: 'delete',
            id: notification.id
        })
        .then((res) => {
            let newMentions = [];
            mentions.forEach((mention) => {
                if (mention.id !== notification.id) {
                    newMentions.push(mention)
                }
            });
            let newInteractions = [];
            interactions.forEach((interaction) => {
                if (interaction.id !== notification.id) {
                    newInteractions.push(interaction)
                }
            });
            setMentions(newMentions);
            setInteractions(newInteractions);
        })
        .catch(handleError);
    }

    const deleteAllNotifications = () => {
        axios.post('/api/v1/notifications', {
            action: 'delete_all'
        })
        .then((res) => {
            setMentions([]);
            setInteractions([]);
        })
        .catch(handleError);
    }

    const SelectView = () => {

        const styleInteractionsSelected = {
            backgroundColor: '#339CFE',
            marginRight: '10px',
            color: 'white'
        };

        const styleInteractionsUnselected = {
            backgroundColor: 'white',
            marginRight: '10px',
            color: 'black'
        };

        const styleMentionsSelected = {
            backgroundColor: 'white',
            color: 'black'
        };

        const styleMentionsUnselected = {
            backgroundColor: '#339CFE',
            color: 'white'
        };

        return (
            <div style={{ display: 'flex', flexDirection: 'row', width: '90%', margin: '0 auto 20px auto', justifyContent: 'space-between' }}>
                <Button
                    onClick={() => setShowInteractions(true)}
                    className="notification-option btn btn-primary"
                    style={showInteractions ? styleInteractionsSelected : styleInteractionsUnselected}
                >
                    Interactions
                </Button>
                <Button
                    onClick={() => setShowInteractions(false)}
                    className="notification-option"
                    style={showInteractions ? styleMentionsSelected : styleMentionsUnselected}>Mentions</Button>
            </div>
        );
    }

    const Mention = (props) => {
        return (
            <div className="mention">
                <div className="interaction">
                    <div id="interaction-icon-parent" style={{ margin: 'auto 20px auto 20px' }}>
                        {props.notification.type.toLowerCase() === "mention" && <AtSign className="notification-icon" style={{ fill: 'none' }} />}
                        {props.notification.type.toLowerCase() === "comment" && <MessageSquare className="notification-icon" />}
                    </div>
                    <div style={{ width: '100%' }}>
                        {props.notification.content}
                    </div>
                    <div style={{ margin: 'auto 20px auto 20px', color: 'gray', fontSize: '13px' }}>
                        {props.notification.date}
                    </div>
                    <div style={{margin: '10px'}}>
                        <Button variant="danger" onClick={() => deleteNotification(props.notification)}> X </Button>
                    </div>
                </div>    
            </div>
        );
    }

    const Interaction = (props) => {
        return (
            <div className="interaction">
                <div id="interaction-icon-parent" style={{ margin: 'auto 20px auto 20px' }}>
                    {props.notification.type.toLowerCase() === "follow" && <UserPlus className="notification-icon" />}
                    {props.notification.type.toLowerCase() === "like" && <Heart className="notification-icon" style={{ fill: '#FF6464', stroke: '#E70000' }} />}
                    {props.notification.type.toLowerCase() === "dislike" && <ThumbsDown className="notification-icon" style={{ fill: '#454545', stroke: '#363636' }} />}
                </div>
                <div style={{ width: '100%' }}>
                    {props.notification.content}
                </div>
                <div style={{ margin: 'auto 20px auto 20px', color: 'gray', fontSize: '13px' }}>
                    {props.notification.date}
                </div>

                <div style={{margin: '10px'}}>
                        <Button variant="danger" onClick={() => deleteNotification(props.notification)}> X </Button>
                </div>
            </div>
        );
    }

    return (
        <>
            <h1>Notifications</h1>
            <SelectView />
            <div style={{ width: '90%', margin: '0 auto 0 auto' }}>
                {showInteractions && interactions.length === 0 && 
                    <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                        <NotFound style={{width:'90%',margin:'20px 0 20px 0'}}/>
                        <p style={{color: 'white',textAlign:'center',margin:'30px 0 30px 0'}}>No interactions found.</p>
                    </div>
                }
                {showInteractions && interactions.length > 0 && interactions.map(notification => <Interaction notification={notification} />)}
                {!showInteractions && mentions.length === 0 && 
                    <div style={{display:'flex',flexDirection:'column',alignItems:'center'}}>
                        <NotFound style={{width:'90%',margin:'20px 0 20px 0'}}/>
                        <p style={{color: 'white',textAlign:'center',margin:'30px 0 30px 0'}}>No mentions found.</p>
                    </div>
                }
                {!showInteractions && mentions.map(notification => <Mention notification={notification} />)}
                {interactions.length > 0 || mentions.length > 0 && <Button variant="danger" className="w-100" onClick={deleteAllNotifications}> Delete All</Button> }   
            </div>
        </>
    );
}

export default NotificationCenter;