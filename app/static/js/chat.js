// Initialize unique Session ID for chat session
let sessionId = localStorage.getItem('rit_chat_session_id');
if (!sessionId) {
    sessionId = 'session_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('rit_chat_session_id', sessionId);
}

// DOM Elements
const chatForm = document.getElementById('chat-input-form');
const messageInput = document.getElementById('student-message-input');
const chatMessagesLog = document.getElementById('chat-messages');
const clearChatBtn = document.getElementById('btn-clear-chat');

// Initialize event listeners
if (chatForm) {
    chatForm.addEventListener('submit', handleFormSubmit);
}

if (clearChatBtn) {
    clearChatBtn.addEventListener('click', clearChatLogs);
}

/**
 * Handles chat form submissions.
 */
function handleFormSubmit(event) {
    event.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;
    
    // Add user message to display logs
    appendMessage(text, 'student');
    
    // Clear input field
    messageInput.value = '';
    
    // Send message to server and display loading indicator
    submitQuery(text);
}

/**
 * Interface to trigger query submissions from sidebar click.
 */
function askQuickQuestion(questionText) {
    appendMessage(questionText, 'student');
    submitQuery(questionText);
}

/**
 * Submits the user query to the public chat API endpoint.
 */
function submitQuery(messageText) {
    // Inject typing indicator
    const typingIndicator = showTypingIndicator();
    
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: messageText,
            session_id: sessionId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response error');
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        typingIndicator.remove();
        
        // Append bot message response
        appendMessage(data.response, 'bot');
    })
    .catch(error => {
        console.error('Error sending message:', error);
        typingIndicator.remove();
        appendMessage("I couldn't contact the server. Please check your network and try again.", 'bot', true);
    });
}

/**
 * Appends a message bubble to the chat logs.
 */
function appendMessage(text, sender, isError = false) {
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${sender === 'student' ? 'student-msg' : 'system-msg'}`;
    
    const avatar = document.createElement('div');
    avatar.className = `msg-avatar ${sender === 'student' ? 'student-avatar-mini' : 'bot-avatar-mini'}`;
    avatar.innerHTML = sender === 'student' ? '<i class="bx bx-user"></i>' : '<i class="bx bx-bot"></i>';
    
    const wrapper = document.createElement('div');
    wrapper.className = 'msg-content-wrapper';
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    if (isError) {
        bubble.style.borderLeft = '4px solid var(--status-error)';
        bubble.style.backgroundColor = 'rgba(239, 68, 68, 0.08)';
    }
    
    const p = document.createElement('p');
    p.textContent = text;
    bubble.appendChild(p);
    
    const timestamp = document.createElement('span');
    timestamp.className = 'msg-timestamp';
    const now = new Date();
    timestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    wrapper.appendChild(bubble);
    wrapper.appendChild(timestamp);
    
    messageRow.appendChild(avatar);
    messageRow.appendChild(wrapper);
    
    chatMessagesLog.appendChild(messageRow);
    scrollToBottom();
}

/**
 * Creates and displays a typing bubble for the bot.
 */
function showTypingIndicator() {
    const indicatorRow = document.createElement('div');
    indicatorRow.className = 'message-row system-msg';
    
    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar bot-avatar-mini';
    avatar.innerHTML = '<i class="bx bx-bot"></i>';
    
    const wrapper = document.createElement('div');
    wrapper.className = 'msg-content-wrapper';
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    
    const loader = document.createElement('div');
    loader.className = 'typing-indicator';
    loader.innerHTML = '<span></span><span></span><span></span>';
    
    bubble.appendChild(loader);
    wrapper.appendChild(bubble);
    indicatorRow.appendChild(avatar);
    indicatorRow.appendChild(wrapper);
    
    chatMessagesLog.appendChild(indicatorRow);
    scrollToBottom();
    
    return indicatorRow;
}

/**
 * Scrolls the chat log screen to the bottom to display newest message.
 */
function scrollToBottom() {
    chatMessagesLog.scrollTop = chatMessagesLog.scrollHeight;
}

/**
 * Clears local chat logs.
 */
function clearChatLogs() {
    // Keep only the first welcome message
    const welcomeMsg = chatMessagesLog.querySelector('.message-row.system-msg');
    chatMessagesLog.innerHTML = '';
    if (welcomeMsg) {
        chatMessagesLog.appendChild(welcomeMsg);
    }
}
