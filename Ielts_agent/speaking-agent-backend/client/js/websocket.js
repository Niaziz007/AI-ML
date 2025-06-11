const socket = new WebSocket('ws://localhost:3000'); // Adjust the URL as needed

socket.onopen = function(event) {
    console.log('WebSocket connection established');
};

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    displayMessage(message);
};

socket.onclose = function(event) {
    console.log('WebSocket connection closed');
};

function sendMessage(message) {
    const messageData = JSON.stringify({ text: message });
    socket.send(messageData);
}

function displayMessage(message) {
    const chatBox = document.getElementById('chat-box'); // Ensure you have an element with this ID
    const messageElement = document.createElement('div');
    messageElement.textContent = message.text; // Adjust based on your message structure
    chatBox.appendChild(messageElement);
}

// Example usage: sending a message when a button is clicked
document.getElementById('send-button').addEventListener('click', function() {
    const userInput = document.getElementById('user-input').value; // Ensure you have an input element with this ID
    sendMessage(userInput);
});