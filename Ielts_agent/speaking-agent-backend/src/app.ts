import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { RealtimeService } from './services/realtimeService';

dotenv.config();

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../client')));

// Serve the frontend
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../client/index.html'));
});

// Initialize Realtime Service
const realtimeService = new RealtimeService(process.env.API_KEY!);

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  socket.on('start-session', async () => {
    try {
      await realtimeService.createSession(socket);
      console.log('Realtime session started for:', socket.id);
      socket.emit('session-started');
    } catch (error) {
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