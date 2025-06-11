import { Socket } from 'socket.io';
export declare class RealtimeController {
    handleConnection(socket: Socket): void;
    handleDisconnection(socket: Socket): void;
}
