"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatController = void 0;
class ChatController {
    constructor(openAIService) {
        this.openAIService = openAIService;
    }
    async handleUserMessage(req, res) {
        try {
            const { message: userMessage } = req.body;
            if (!userMessage) {
                res.status(400).json({ error: 'Message is required' });
                return;
            }
            const response = await this.openAIService.sendMessage(userMessage);
            this.handleResponse(res, response);
        }
        catch (error) {
            console.error('Error handling user message:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }
    handleResponse(res, response) {
        res.json({
            success: true,
            data: response
        });
    }
}
exports.ChatController = ChatController;
//# sourceMappingURL=chatController.js.map