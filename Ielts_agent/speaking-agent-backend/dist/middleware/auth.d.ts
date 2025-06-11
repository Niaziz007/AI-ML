import { Request, Response, NextFunction } from 'express';
declare module 'express' {
    interface Request {
        user?: any;
    }
}
export declare const authenticateUser: (req: Request, res: Response, next: NextFunction) => void;
