import { Request, Response, NextFunction } from 'express';

export const validateMessage = (req: Request, res: Response, next: NextFunction): void => {
    const { message } = req.body;

    if (!message || typeof message !== 'string' || message.trim().length === 0) {
        res.status(400).json({ error: 'Valid message is required' });
        return;
    }

    if (message.length > 1000) {
        res.status(400).json({ error: 'Message too long. Maximum 1000 characters allowed.' });
        return;
    }

    next();
};