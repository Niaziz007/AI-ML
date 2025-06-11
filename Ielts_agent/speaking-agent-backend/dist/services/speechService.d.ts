export declare class SpeechService {
    constructor();
    processAudioBuffer(audioBuffer: ArrayBuffer): Promise<string>;
    convertToBase64(buffer: ArrayBuffer): string;
    convertFromBase64(base64: string): ArrayBuffer;
}
