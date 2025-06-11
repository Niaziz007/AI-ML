import { Server } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import { RealtimeController } from '../controllers/realtimeController';

export function setWebSocketRoutes(server: Server): void {
    const io = new SocketIOServer(server, {
        cors: {
            origin: "*",
            methods: ["GET", "POST"]
        }
    });

    const realtimeController = new RealtimeController();

    io.on('connection', (socket) => {
        realtimeController.handleConnection(socket);

        socket.on('disconnect', () => {
            realtimeController.handleDisconnection(socket);
        });
    });
}