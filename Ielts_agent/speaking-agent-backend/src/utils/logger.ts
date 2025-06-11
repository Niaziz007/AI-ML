interface LogLevel {
    ERROR: string;
    WARN: string;
    INFO: string;
    DEBUG: string;
}

interface LogEntry {
    timestamp: string;
    level: string;
    message: string;
}

class SimpleLogger {
    private levels: LogLevel = {
        ERROR: 'ERROR',
        WARN: 'WARN',
        INFO: 'INFO',
        DEBUG: 'DEBUG'
    };

    private formatMessage(level: string, message: string): string {
        const timestamp = new Date().toISOString();
        return `[${timestamp}] ${level}: ${message}`;
    }

    error(message: string): void {
        console.error(this.formatMessage(this.levels.ERROR, message));
    }

    warn(message: string): void {
        console.warn(this.formatMessage(this.levels.WARN, message));
    }

    info(message: string): void {
        console.info(this.formatMessage(this.levels.INFO, message));
    }

    debug(message: string): void {
        console.debug(this.formatMessage(this.levels.DEBUG, message));
    }
}

export const logger = new SimpleLogger();