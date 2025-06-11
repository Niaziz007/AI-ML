class SpeakingAgent {
    constructor() {
        this.socket = null;
        this.isRecording = false;
        this.isSessionActive = false;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.audioContext = null;
        this.audioWorkletNode = null;
        this.audioPlayer = null;
        this.currentTranscripts = {
            user: '',
            assistant: ''
        };

        this.initializeElements();
        this.initializeSocket();
        this.setupEventListeners();
    }

    initializeElements() {
        this.elements = {
            startBtn: document.getElementById('startBtn'),
            recordBtn: document.getElementById('recordBtn'),
            stopBtn: document.getElementById('stopBtn'),
            chatWindow: document.getElementById('chatWindow'),
            transcript: document.getElementById('transcript'),
            connectionStatus: document.getElementById('connectionStatus'),
            statusIndicator: document.querySelector('.status-indicator'),
            statusText: document.querySelector('.status-text'),
            volumeBar: document.getElementById('volumeBar'),
            textInput: document.getElementById('textInput'),
            sendTextBtn: document.getElementById('sendTextBtn'),
            modeButtons: document.querySelectorAll('.mode-btn')
        };
    }

    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
            this.addMessage('System', 'Connected to server', 'system');
        });

        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
            this.addMessage('System', 'Disconnected from server', 'system');
            this.resetSession();
        });

        this.socket.on('session-started', () => {
            this.isSessionActive = true;
            this.enableControls();
            this.addMessage('Assistant', 'Hello! I\'m ready to help you practice English. How would you like to start?', 'bot');
        });

        this.socket.on('audio-response', (data) => {
            this.playAudioResponse(data.audio);
        });

        this.socket.on('transcript-update', (data) => {
            this.updateTranscript(data);
        });

        this.socket.on('text-response', (data) => {
            // Handle text responses if needed
            console.log('Text response:', data);
        });

        this.socket.on('response-complete', () => {
            console.log('Response complete');
        });

        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.addMessage('System', `Error: ${error}`, 'error');
        });
    }

    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.startSession());
        this.elements.stopBtn.addEventListener('click', () => this.stopSession());
        
        // Hold to speak functionality
        this.elements.recordBtn.addEventListener('mousedown', () => this.startRecording());
        this.elements.recordBtn.addEventListener('mouseup', () => this.stopRecording());
        this.elements.recordBtn.addEventListener('mouseleave', () => this.stopRecording());
        
        // Touch events for mobile
        this.elements.recordBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            this.startRecording();
        });
        this.elements.recordBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.stopRecording();
        });

        // Text input
        this.elements.sendTextBtn.addEventListener('click', () => this.sendTextMessage());
        this.elements.textInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextMessage();
            }
        });

        // Practice mode buttons
        this.elements.modeButtons.forEach(btn => {
            btn.addEventListener('click', () => this.selectPracticeMode(btn.dataset.mode));
        });
    }

    async startSession() {
        try {
            this.elements.startBtn.disabled = true;
            this.elements.startBtn.textContent = 'Starting...';
            
            await this.initializeAudio();
            this.socket.emit('start-session');
            
        } catch (error) {
            console.error('Error starting session:', error);
            this.addMessage('System', 'Error starting session. Please check microphone permissions.', 'error');
            this.elements.startBtn.disabled = false;
            this.elements.startBtn.textContent = 'Start Session';
        }
    }

    stopSession() {
        this.isSessionActive = false;
        this.stopRecording();
        this.cleanupAudio();
        this.socket.disconnect();
        this.resetSession();
        this.addMessage('System', 'Session ended', 'system');
    }

    resetSession() {
        this.isSessionActive = false;
        this.isRecording = false;
        this.elements.startBtn.disabled = false;
        this.elements.startBtn.textContent = 'Start Session';
        this.elements.recordBtn.disabled = true;
        this.elements.stopBtn.disabled = true;
        this.elements.textInput.disabled = true;
        this.elements.sendTextBtn.disabled = true;
        this.elements.recordBtn.classList.remove('recording');
    }

    enableControls() {
        this.elements.startBtn.disabled = true;
        this.elements.recordBtn.disabled = false;
        this.elements.stopBtn.disabled = false;
        this.elements.textInput.disabled = false;
        this.elements.sendTextBtn.disabled = false;
    }

    async initializeAudio() {
        try {
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 24000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });

            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            // Initialize audio player for responses
            this.audioPlayer = new AudioContext();

        } catch (error) {
            throw new Error('Failed to access microphone: ' + error.message);
        }
    }

    startRecording() {
        if (!this.isSessionActive || this.isRecording) return;

        this.isRecording = true;
        this.elements.recordBtn.classList.add('recording');
        this.elements.recordBtn.innerHTML = '<span class="record-icon">🔴</span>Recording...';

        try {
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.processAudioData(event.data);
                }
            };

            this.mediaRecorder.start(100); // Send chunks every 100ms

        } catch (error) {
            console.error('Error starting recording:', error);
            this.stopRecording();
        }
    }

    stopRecording() {
        if (!this.isRecording) return;

        this.isRecording = false;
        this.elements.recordBtn.classList.remove('recording');
        this.elements.recordBtn.innerHTML = '<span class="record-icon">🎤</span>Hold to Speak';

        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.socket.emit('commit-audio');
            this.socket.emit('create-response');
        }
    }

    async processAudioData(audioBlob) {
        try {
            const arrayBuffer = await audioBlob.arrayBuffer();
            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            // Convert to PCM16
            const pcmData = this.convertToPCM16(audioBuffer);
            const base64Audio = this.arrayBufferToBase64(pcmData);
            
            this.socket.emit('audio-data', base64Audio);

        } catch (error) {
            console.error('Error processing audio:', error);
        }
    }

    convertToPCM16(audioBuffer) {
        const samples = audioBuffer.getChannelData(0);
        const pcm16 = new Int16Array(samples.length);
        
        for (let i = 0; i < samples.length; i++) {
            pcm16[i] = Math.max(-32768, Math.min(32767, samples[i] * 32768));
        }
        
        return pcm16.buffer;
    }

    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    async playAudioResponse(base64Audio) {
        try {
            const audioData = atob(base64Audio);
            const audioArray = new Uint8Array(audioData.length);
            
            for (let i = 0; i < audioData.length; i++) {
                audioArray[i] = audioData.charCodeAt(i);
            }

            const audioBuffer = await this.audioPlayer.decodeAudioData(audioArray.buffer);
            const source = this.audioPlayer.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioPlayer.destination);
            source.start();

        } catch (error) {
            console.error('Error playing audio:', error);
        }
    }

    updateTranscript(data) {
        const transcriptElement = this.elements.transcript;
        
        if (data.type === 'user-transcript') {
            this.currentTranscripts.user = data.transcript;
            this.addTranscriptLine('You', data.transcript);
        } else if (data.type === 'assistant-transcript') {
            this.currentTranscripts.assistant += data.transcript;
            this.updateTranscriptLine('Assistant', this.currentTranscripts.assistant);
        }
    }

    addTranscriptLine(speaker, text) {
        const transcriptElement = this.elements.transcript;
        const line = document.createElement('div');
        line.className = 'transcript-line';
        line.innerHTML = `<span class="speaker">${speaker}:</span> <span class="text">${text}</span>`;
        transcriptElement.appendChild(line);
        transcriptElement.scrollTop = transcriptElement.scrollHeight;
    }

    updateTranscriptLine(speaker, text) {
        const transcriptElement = this.elements.transcript;
        const lines = transcriptElement.querySelectorAll('.transcript-line');
        let lastAssistantLine = null;
        
        // Find the last assistant line
        for (let i = lines.length - 1; i >= 0; i--) {
            if (lines[i].querySelector('.speaker').textContent === 'Assistant:') {
                lastAssistantLine = lines[i];
                break;
            }
        }
        
        if (lastAssistantLine) {
            lastAssistantLine.querySelector('.text').textContent = text;
        } else {
            this.addTranscriptLine(speaker, text);
        }
        
        transcriptElement.scrollTop = transcriptElement.scrollHeight;
    }

    sendTextMessage() {
        const message = this.elements.textInput.value.trim();
        if (!message || !this.isSessionActive) return;

        this.addMessage('You', message, 'user');
        this.socket.emit('send-message', message);
        this.elements.textInput.value = '';
    }

    selectPracticeMode(mode) {
        // Remove active class from all buttons
        this.elements.modeButtons.forEach(btn => btn.classList.remove('active'));
        
        // Add active class to selected button
        const selectedBtn = document.querySelector(`[data-mode="${mode}"]`);
        selectedBtn.classList.add('active');

        // Send mode-specific message
        const modeMessages = {
            conversation: "Let's have a free conversation. What would you like to talk about?",
            part1: "Let's practice IELTS Speaking Part 1. I'll ask you questions about familiar topics.",
            part2: "Let's practice IELTS Speaking Part 2. I'll give you a topic to speak about for 1-2 minutes.",
            part3: "Let's practice IELTS Speaking Part 3. We'll have a discussion about abstract topics.",
            feedback: "Please provide feedback on my speaking performance so far."
        };

        if (this.isSessionActive) {
            this.socket.emit('send-message', modeMessages[mode]);
        }
    }

    addMessage(sender, content, type = 'bot') {
        const chatWindow = this.elements.chatWindow;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type === 'user' ? 'user-message' : 'bot-message'}`;
        
        const avatar = type === 'user' ? '👤' : (type === 'system' ? '⚙️' : (type === 'error' ? '❌' : '🤖'));
        
        messageDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="content">
                <p>${content}</p>
            </div>
        `;
        
        chatWindow.appendChild(messageDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    updateConnectionStatus(connected) {
        if (connected) {
            this.elements.statusIndicator.classList.add('connected');
            this.elements.statusText.textContent = 'Connected';
        } else {
            this.elements.statusIndicator.classList.remove('connected');
            this.elements.statusText.textContent = 'Disconnected';
        }
    }

    cleanupAudio() {
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        if (this.audioPlayer) {
            this.audioPlayer.close();
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SpeakingAgent();
});