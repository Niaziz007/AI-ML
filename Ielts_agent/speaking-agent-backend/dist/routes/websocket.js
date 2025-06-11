"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setWebSocketRoutes = setWebSocketRoutes;
const socket_io_1 = require("socket.io");
const realtimeController_1 = require("../controllers/realtimeController");
function setWebSocketRoutes(server) {
    const io = new socket_io_1.Server(server, {
        cors: {
            origin: "*",
            methods: ["GET", "POST"]
        }
    });
    const realtimeController = new realtimeController_1.RealtimeController();
    io.on('connection', (socket) => {
        realtimeController.handleConnection(socket);
        socket.on('disconnect', () => {
            realtimeController.handleDisconnection(socket);
        });
    });
}
//# sourceMappingURL=websocket.js.map