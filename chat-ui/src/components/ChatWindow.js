// src/components/ChatWindow.js
import React, { useEffect } from 'react'; // Remove 'useState' since it's not used

function ChatWindow({ selectedTitle, messages }) {
    useEffect(() => {
        // This effect runs whenever 'messages' changes
    }, [messages]);

    return (
        <div>
            <h2>Chat with {selectedTitle}</h2>
            <div className="chat-messages">
                {messages.map((message, index) => (
                    <div key={index}>
                        <p><strong>User:</strong> {message.user_response || 'No response'}</p>
                        <p><strong>AI:</strong> {message.ai_response || 'No response'}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ChatWindow;
