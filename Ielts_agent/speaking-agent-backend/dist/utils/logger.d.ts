declare class SimpleLogger {
    private levels;
    private formatMessage;
    error(message: string): void;
    warn(message: string): void;
    info(message: string): void;
    debug(message: string): void;
}
export declare const logger: SimpleLogger;
export {};
