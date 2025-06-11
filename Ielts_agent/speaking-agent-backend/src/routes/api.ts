import { Express } from 'express';
import { ChatController } from '../controllers/chatController';
import { validateMessage } from '../middleware/validation';

export function setApiRoutes(app: Express): void {
    const chatController = new ChatController(null); // We'll pass the actual service when implementing

    app.post('/api/chat', validateMessage, (req, res) => {
        chatController.handleUserMessage(req, res);
    });

    app.get('/api/health', (req, res) => {
        res.json({ status: 'OK', timestamp: new Date().toISOString() });
    });
}