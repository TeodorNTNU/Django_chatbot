// src/App.js
import React, { useState, useEffect } from 'react';
import ConversationList from './components/ConversationList';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import axios from 'axios';

function App() {
    const [selectedTitle, setSelectedTitle] = useState(null);
    const [conversations, setConversations] = useState([]);
    const [messages, setMessages] = useState([]); // State to store messages

    useEffect(() => {
        if (selectedTitle) {
            fetchMessagesForTitle(selectedTitle);
        }
    }, [selectedTitle]); // Fetch messages whenever a new title is selected

    const handleSelectConversation = (title) => {
        setSelectedTitle(title);
    };

    const fetchMessagesForTitle = (title) => {
        axios.get(`http://localhost:8000/chat/?title=${encodeURIComponent(title)}`, {
            headers: {
                'Authorization': `Token ${localStorage.getItem('userToken')}`,
            }
        })
        .then(response => {
            setMessages(response.data || []);
        })
        .catch(error => {
            console.error('Error fetching messages:', error);
        });
    };

    const handleNewConversation = (title) => {
        setSelectedTitle(title);
        setMessages([]); // Clear messages when starting a new conversation
        setConversations(prevConversations => [...prevConversations, { id: Date.now(), title }]);
    };

    const handleNewMessage = (newAiResponse, newMessages) => {
        setMessages(newMessages); // Update messages with the response from the backend
    };

    return (
        <div className="App">
            <ConversationList conversations={conversations} onSelectConversation={handleSelectConversation} />

            {selectedTitle && (
                <>
                    <ChatWindow selectedTitle={selectedTitle} messages={messages} />
                    <MessageInput selectedTitle={selectedTitle} onNewConversation={handleNewConversation} onNewMessage={handleNewMessage} />
                </>
            )}

            {!selectedTitle && (
                <MessageInput selectedTitle={null} onNewConversation={handleNewConversation} onNewMessage={handleNewMessage} />
            )}
        </div>
    );
}

export default App;
