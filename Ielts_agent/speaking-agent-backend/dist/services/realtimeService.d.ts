import { Socket } from 'socket.io';
export declare class RealtimeService {
    private sessions;
    private apiKey;
    constructor(apiKey: string);
    createSession(socket: Socket): Promise<void>;
    private handleRealtimeMessage;
    sendAudio(socketId: string, audioData: string): void;
    commitAudio(socketId: string): void;
    createResponse(socketId: string): void;
    sendTextMessage(socketId: string, text: string): void;
    closeSession(socketId: string): void;
}
