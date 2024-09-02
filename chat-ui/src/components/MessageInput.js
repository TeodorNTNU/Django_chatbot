// src/components/MessageInput.js
import React, { useState } from 'react';
import axios from 'axios';

function MessageInput({ selectedTitle, onNewConversation, onNewMessage }) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();

        if (message.trim()) {
            const url = 'http://localhost:8000/chat/';
            const headers = {
                'Authorization': `Token ${localStorage.getItem('userToken')}`,
                'Content-Type': 'application/json',
            };

            const requestBody = selectedTitle
                ? { title: selectedTitle, prompt: message }
                : { prompt: message };

            axios.post(url, requestBody, { headers })
                .then(response => {
                    if (!selectedTitle) {
                        // Handle new conversation creation
                        onNewConversation(response.data.title);
                    }

                    // Update messages with the new AI response
                    onNewMessage(response.data.ai_response, response.data.messages);

                    // Clear input field after sending the message
                    setMessage('');
                })
                .catch(error => {
                    console.error('Error sending message:', error);
                });
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type a message..."
            />
            <button type="submit">Send</button>
        </form>
    );
}

export default MessageInput;
