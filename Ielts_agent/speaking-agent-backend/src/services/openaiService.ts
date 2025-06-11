import OpenAI from 'openai';

export class OpenAIService {
    private client: OpenAI;

    constructor(apiKey: string) {
        this.client = new OpenAI({
            apiKey: apiKey,
        });
    }

    async sendMessage(message: string): Promise<string> {
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
        } catch (error) {
            console.error('OpenAI API error:', error);
            throw new Error('Failed to get response from OpenAI');
        }
    }
}