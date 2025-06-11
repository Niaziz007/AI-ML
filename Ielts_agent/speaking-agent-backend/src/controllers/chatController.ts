import { Request, Response } from 'express';

export class ChatController {
    private openAIService: any;

    constructor(openAIService: any) {
        this.openAIService = openAIService;
    }

    async handleUserMessage(req: Request, res: Response): Promise<void> {
        try {
            const { message: userMessage } = req.body;
            
            if (!userMessage) {
                res.status(400).json({ error: 'Message is required' });
                return;
            }

            const response = await this.openAIService.sendMessage(userMessage);
            this.handleResponse(res, response);
        } catch (error) {
            console.error('Error handling user message:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }

    handleResponse(res: Response, response: any): void {
        res.json({
            success: true,
            data: response
        });
    }
}