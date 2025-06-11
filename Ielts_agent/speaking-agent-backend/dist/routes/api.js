"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setApiRoutes = setApiRoutes;
const chatController_1 = require("../controllers/chatController");
const validation_1 = require("../middleware/validation");
function setApiRoutes(app) {
    const chatController = new chatController_1.ChatController(null); // We'll pass the actual service when implementing
    app.post('/api/chat', validation_1.validateMessage, (req, res) => {
        chatController.handleUserMessage(req, res);
    });
    app.get('/api/health', (req, res) => {
        res.json({ status: 'OK', timestamp: new Date().toISOString() });
    });
}
//# sourceMappingURL=api.js.map