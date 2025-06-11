export declare class OpenAIService {
    private client;
    constructor(apiKey: string);
    sendMessage(message: string): Promise<string>;
}
