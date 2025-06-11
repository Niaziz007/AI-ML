"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.logger = void 0;
class SimpleLogger {
    constructor() {
        this.levels = {
            ERROR: 'ERROR',
            WARN: 'WARN',
            INFO: 'INFO',
            DEBUG: 'DEBUG'
        };
    }
    formatMessage(level, message) {
        const timestamp = new Date().toISOString();
        return `[${timestamp}] ${level}: ${message}`;
    }
    error(message) {
        console.error(this.formatMessage(this.levels.ERROR, message));
    }
    warn(message) {
        console.warn(this.formatMessage(this.levels.WARN, message));
    }
    info(message) {
        console.info(this.formatMessage(this.levels.INFO, message));
    }
    debug(message) {
        console.debug(this.formatMessage(this.levels.DEBUG, message));
    }
}
exports.logger = new SimpleLogger();
//# sourceMappingURL=logger.js.map