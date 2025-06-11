import { Request, Response } from 'express';
export declare class ChatController {
    private openAIService;
    constructor(openAIService: any);
    handleUserMessage(req: Request, res: Response): Promise<void>;
    handleResponse(res: Response, response: any): void;
}
