// src/components/ConversationList.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function ConversationList({ onSelectConversation }) {
    const [conversations, setConversations] = useState([]);

    useEffect(() => {
        // Fetch conversation titles from the backend
        axios.get('http://localhost:8000/chat/get-titles/', {
            headers: {
                'Authorization': `Token ${localStorage.getItem('userToken')}`, // Assuming token is stored in local storage
            }
        })
        .then(response => {
            setConversations(response.data);
        })
        .catch(error => {
            console.error('Error fetching conversations:', error);
        });
    }, []);

    return (
        <div>
            <h2>Conversations</h2>
            <ul>
                {conversations.map(conversation => (
                    <li key={conversation.id} onClick={() => onSelectConversation(conversation.title)}>
                        {conversation.title}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default ConversationList;
