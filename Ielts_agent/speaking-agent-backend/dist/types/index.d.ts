export interface UserMessage {
    userId: string;
    content: string;
    timestamp: Date;
}
export interface AgentResponse {
    agentId: string;
    content: string;
    timestamp: Date;
}
export interface RealtimeSession {
    socket: any;
    ws: any;
    sessionId: string;
}
export interface AudioData {
    audio: string;
    type: string;
}
export interface TranscriptData {
    transcript: string;
    type: 'user-transcript' | 'assistant-transcript';
    item_id?: string;
}
export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
}
