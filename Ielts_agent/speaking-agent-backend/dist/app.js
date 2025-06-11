"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const http_1 = require("http");
const socket_io_1 = require("socket.io");
const cors_1 = __importDefault(require("cors"));
const dotenv_1 = __importDefault(require("dotenv"));
const path_1 = __importDefault(require("path"));
const realtimeService_1 = require("./services/realtimeService");
dotenv_1.default.config();
const app = (0, express_1.default)();
const server = (0, http_1.createServer)(app);
const io = new socket_io_1.Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});
// Middleware
app.use((0, cors_1.default)());
app.use(express_1.default.json());
app.use(express_1.default.static(path_1.default.join(__dirname, '../client')));
// Serve the frontend
app.get('/', (req, res) => {
    res.sendFile(path_1.default.join(__dirname, '../client/index.html'));
});
// Initialize Realtime Service
const realtimeService = new realtimeService_1.RealtimeService(process.env.API_KEY);
// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('User connected:', socket.id);
    socket.on('start-session', async () => {
        try {
            await realtimeService.createSession(socket);
            console.log('Realtime session started for:', socket.id);
            socket.emit('session-started');
        }
        catch (error) {
            console.error('Error starting session:', error);
            socket.emit('error', 'Failed to start session');
        }
    });
    socket.on('audio-data', (audioData) => {
        realtimeService.sendAudio(socket.id, audioData);
    });
    socket.on('commit-audio', () => {
        realtimeService.commitAudio(socket.id);
    });
    socket.on('create-response', () => {
        realtimeService.createResponse(socket.id);
    });
    socket.on('send-message', (message) => {
        realtimeService.sendTextMessage(socket.id, message);
    });
    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        realtimeService.closeSession(socket.id);
    });
});
const PORT = parseInt(process.env.PORT || '3000', 10);
const HOST = '172.16.14.213';
server.listen(PORT, HOST, () => {
    console.log(`🚀 IELTS Speaking Agent running on http://${HOST}:${PORT}`);
    console.log(`🎯 Ready to help users practice English speaking skills!`);
});
//# sourceMappingURL=app.js.map