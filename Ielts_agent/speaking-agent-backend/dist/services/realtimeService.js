"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RealtimeService = void 0;
const ws_1 = __importDefault(require("ws"));
class RealtimeService {
    constructor(apiKey) {
        this.sessions = new Map();
        this.apiKey = apiKey;
    }
    async createSession(socket) {
        const url = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2025-06-03';
        const ws = new ws_1.default(url, {
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'OpenAI-Beta': 'realtime=v1'
            }
        });
        return new Promise((resolve, reject) => {
            ws.on('open', () => {
                console.log('OpenAI Realtime connection established');
                // Configure the session for IELTS speaking practice
                const sessionConfig = {
                    type: 'session.update',
                    session: {
                        modalities: ['text', 'audio'],
                        instructions: `You are an expert IELTS speaking tutor and English conversation partner. Your role is to:

1. Help users improve their English speaking skills through natural conversation
2. Conduct IELTS speaking practice sessions (Parts 1, 2, and 3)
3. Ask authentic IELTS speaking questions when requested
4. Listen carefully to the user's responses and provide constructive feedback on:
   - Pronunciation and fluency
   - Grammar and vocabulary usage
   - Task achievement and coherence
   - Estimated band score when appropriate

Be encouraging, patient, and provide specific suggestions for improvement. Speak clearly and at an appropriate pace for language learners. Engage in natural conversation and adapt to the user's level.`,
                        voice: 'alloy',
                        input_audio_format: 'pcm16',
                        output_audio_format: 'pcm16',
                        input_audio_transcription: {
                            model: 'whisper-1'
                        },
                        turn_detection: {
                            type: 'server_vad',
                            threshold: 0.5,
                            prefix_padding_ms: 300,
                            silence_duration_ms: 500
                        }
                    }
                };
                ws.send(JSON.stringify(sessionConfig));
                this.sessions.set(socket.id, {
                    socket,
                    ws,
                    sessionId: socket.id
                });
                resolve();
            });
            ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data.toString());
                    this.handleRealtimeMessage(socket.id, message);
                }
                catch (error) {
                    console.error('Error parsing message:', error);
                }
            });
            ws.on('error', (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            });
            ws.on('close', () => {
                console.log('OpenAI connection closed');
                this.sessions.delete(socket.id);
            });
        });
    }
    handleRealtimeMessage(socketId, message) {
        const session = this.sessions.get(socketId);
        if (!session)
            return;
        switch (message.type) {
            case 'response.audio.delta':
                // Send audio chunks to the client
                session.socket.emit('audio-response', {
                    audio: message.delta,
                    type: 'audio-delta'
                });
                break;
            case 'response.audio_transcript.delta':
                // Send transcription updates
                session.socket.emit('transcript-update', {
                    transcript: message.delta,
                    type: 'assistant-transcript',
                    item_id: message.item_id
                });
                break;
            case 'conversation.item.input_audio_transcription.completed':
                // Send user's transcription
                session.socket.emit('transcript-update', {
                    transcript: message.transcript,
                    type: 'user-transcript',
                    item_id: message.item_id
                });
                break;
            case 'response.text.delta':
                // Handle text responses
                session.socket.emit('text-response', {
                    text: message.delta,
                    type: 'text-delta'
                });
                break;
            case 'response.done':
                session.socket.emit('response-complete');
                break;
            case 'session.created':
                console.log('Session created:', message.session);
                break;
            case 'session.updated':
                console.log('Session updated:', message.session);
                break;
            case 'error':
                console.error('Realtime API error:', message);
                session.socket.emit('error', message.error);
                break;
            default:
                // Log other message types for debugging
                console.log('Received message type:', message.type);
        }
    }
    sendAudio(socketId, audioData) {
        const session = this.sessions.get(socketId);
        if (!session)
            return;
        const message = {
            type: 'input_audio_buffer.append',
            audio: audioData
        };
        session.ws.send(JSON.stringify(message));
    }
    commitAudio(socketId) {
        const session = this.sessions.get(socketId);
        if (!session)
            return;
        const message = {
            type: 'input_audio_buffer.commit'
        };
        session.ws.send(JSON.stringify(message));
    }
    createResponse(socketId) {
        const session = this.sessions.get(socketId);
        if (!session)
            return;
        const message = {
            type: 'response.create',
            response: {
                modalities: ['text', 'audio']
            }
        };
        session.ws.send(JSON.stringify(message));
    }
    sendTextMessage(socketId, text) {
        const session = this.sessions.get(socketId);
        if (!session)
            return;
        const message = {
            type: 'conversation.item.create',
            item: {
                type: 'message',
                role: 'user',
                content: [
                    {
                        type: 'input_text',
                        text: text
                    }
                ]
            }
        };
        session.ws.send(JSON.stringify(message));
        this.createResponse(socketId);
    }
    closeSession(socketId) {
        const session = this.sessions.get(socketId);
        if (session) {
            session.ws.close();
            this.sessions.delete(socketId);
        }
    }
}
exports.RealtimeService = RealtimeService;
//# sourceMappingURL=realtimeService.js.map