document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const micBtn = document.getElementById('mic-btn');
    const statusDiv = document.getElementById('status');
    
    // IMPORTANT: Change this to your deployed backend URL
    const API_URL = '/chat'; // <-- CHANGE THIS LINE
    // --- Voice Recognition Setup ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let isRecording = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        recognition.onstart = () => {
            isRecording = true;
            micBtn.classList.add('recording');
            updateStatus('Listening...');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userInput.value = transcript;
            sendMessage(transcript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            updateStatus('Mic error. Please try again.');
        };

        recognition.onend = () => {
            isRecording = false;
            micBtn.classList.remove('recording');
            updateStatus('');
        };

        micBtn.addEventListener('click', () => {
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });

    } else {
        micBtn.style.display = 'none';
        updateStatus('Voice recognition not supported in this browser.');
    }

    // --- Main Functions ---
    function updateStatus(message) {
        statusDiv.textContent = message;
    }

    function displayMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        
        if (sender === 'bot') {
            const speakerIcon = document.createElement('span');
            speakerIcon.classList.add('material-icons', 'speaker-icon');
            speakerIcon.textContent = 'campaign';
            messageElement.appendChild(speakerIcon);
        }

        const textElement = document.createElement('span');
        textElement.textContent = message;
        messageElement.appendChild(textElement);
        
        chatLog.appendChild(messageElement);
        chatLog.scrollTop = chatLog.scrollHeight;
        return messageElement;
    }

    function speak(text, messageElement) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onstart = () => {
            messageElement.classList.add('speaking');
        };
        utterance.onend = () => {
            messageElement.classList.remove('speaking');
        };
        window.speechSynthesis.speak(utterance);
    }

    async function sendMessage(messageText) {
        if (messageText.trim() === '') return;

        displayMessage(messageText, 'user');
        userInput.value = '';
        updateStatus('AI is thinking...');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            const botMessageElement = displayMessage(data.reply, 'bot');
            speak(data.reply, botMessageElement);

        } catch (error) {
            console.error('Error fetching bot response:', error);
            displayMessage('Sorry, something went wrong. Please check the connection and try again.', 'bot');
        } finally {
            updateStatus('');
        }
    }

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        sendMessage(userInput.value);
    });

    // Initial bot message
    const initialMessage = "Hello! I am Yash Sojitra's AI assistant. You can ask me questions about his resume by typing or using the microphone.";
    const initialElement = displayMessage(initialMessage, 'bot');
    speak(initialMessage, initialElement);
});