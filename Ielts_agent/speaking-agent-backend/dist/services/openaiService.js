"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpenAIService = void 0;
const openai_1 = __importDefault(require("openai"));
class OpenAIService {
    constructor(apiKey) {
        this.client = new openai_1.default({
            apiKey: apiKey,
        });
    }
    async sendMessage(message) {
        try {
            const completion = await this.client.chat.completions.create({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: "You are a helpful English speaking tutor focused on improving conversational skills."
                    },
                    {
                        role: "user",
                        content: message
                    }
                ],
                max_tokens: 500,
                temperature: 0.7,
            });
            return completion.choices[0]?.message?.content || "I'm sorry, I couldn't generate a response.";
        }
        catch (error) {
            console.error('OpenAI API error:', error);
            throw new Error('Failed to get response from OpenAI');
        }
    }
}
exports.OpenAIService = OpenAIService;
//# sourceMappingURL=openaiService.js.map