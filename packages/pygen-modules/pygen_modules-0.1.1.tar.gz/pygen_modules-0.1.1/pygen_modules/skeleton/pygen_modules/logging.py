import logging
import win32evtlog
import win32evtlogutil
import win32security
from logging.handlers import RotatingFileHandler
import os
import sys
import socket


class PygenLogger:
    def __init__(self, app_name="PygenLogger", log_dir="logs"):
        self.app_name = app_name
        self.log_dir = log_dir
        self.hostname = socket.gethostname()
        self.username = self._get_current_user()

        # Create log directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Initialize all loggers
        self._init_file_loggers()
        self._register_event_sources()

    def _get_current_user(self):
        """Get current Windows username"""
        try:
            return win32security.GetUserNameEx(win32security.NameSamCompatible)
        except Exception:
            return "Unknown"

    def _register_event_sources(self):
        """Register application as event source for all log types"""
        try:
            # Register for Application log
            win32evtlogutil.AddSourceToRegistry(
                self.app_name, "%SystemRoot%\\System32\\EventCreate.exe", "Application"
            )
        except Exception as e:
            self._fallback_log(f"Failed to register event source: {e}")

    def _init_file_loggers(self):
        """Initialize all file-based loggers"""
        # Main application logger
        self.app_logger = self._create_file_logger(
            "application", os.path.join(self.log_dir, "application.log")
        )

        # Security logger
        self.sec_logger = self._create_file_logger(
            "security", os.path.join(self.log_dir, "security.log")
        )

        # System logger
        self.sys_logger = self._create_file_logger(
            "system", os.path.join(self.log_dir, "system.log")
        )

        # Custom/audit logger
        self.audit_logger = self._create_file_logger(
            "audit", os.path.join(self.log_dir, "audit.log")
        )

        # Debug logger (verbose)
        self.debug_logger = self._create_file_logger(
            "debug", os.path.join(self.log_dir, "debug.log"), level=logging.DEBUG
        )

    def _create_file_logger(self, name, log_path, level=logging.INFO):
        """Create a configured file logger"""
        logger = logging.getLogger(f"{self.app_name}_{name}")
        logger.setLevel(level)

        # Prevent adding multiple handlers
        if logger.handlers:
            return logger

        # Create rotating file handler (10MB max, keep 5 backups)
        handler = RotatingFileHandler(
            log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )

        # Custom formatter with more details
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(hostname)s][%(user)s] - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add context information
        handler.addFilter(ContextFilter(self.hostname, self.username))

        logger.addHandler(handler)
        return logger

    def _fallback_log(self, message):
        """Fallback logging if event logging fails"""
        print(f"FALLBACK: {message}", file=sys.stderr)

    def _log_to_windows_event(self, message, level, log_type, event_id=1, category=0):
        """
        Core method to log to Windows Event Viewer

        Parameters:
        - message: The log message
        - level: info, warning, error, success_audit, failure_audit
        - log_type: Application, Security, System
        - event_id: Custom event ID
        - category: Event category
        """
        # Map level to Windows event type
        level_map = {
            "info": win32evtlog.EVENTLOG_INFORMATION_TYPE,
            "warning": win32evtlog.EVENTLOG_WARNING_TYPE,
            "error": win32evtlog.EVENTLOG_ERROR_TYPE,
            "success_audit": win32evtlog.EVENTLOG_SUCCESS,
            "failure_audit": win32evtlog.EVENTLOG_AUDIT_FAILURE,
        }

        event_type = level_map.get(level.lower(), win32evtlog.EVENTLOG_INFORMATION_TYPE)

        try:
            # Include additional context in message
            full_message = f"[User: {self.username}] [Host: {self.hostname}] {message}"

            win32evtlogutil.ReportEvent(
                appName=self.app_name,
                eventID=event_id,
                eventCategory=category,
                eventType=event_type,
                strings=[full_message],
                data=None,
                logType=log_type,
            )
            return True
        except Exception as e:
            self._fallback_log(f"Windows Event Log failed: {e}")
            return False

    def log_application(self, message, level="info", event_id=1000):
        """Log to Application log"""
        success = self._log_to_windows_event(message, level, "Application", event_id)

        # Also log to file
        log_method = getattr(self.app_logger, level, self.app_logger.info)
        log_method(message)

        # Debug logger gets everything
        self.debug_logger.debug(f"APP[{level.upper()}]: {message}")

        return success

    def log_system(self, message, level="info", event_id=2000):
        """Log to System log"""
        success = self._log_to_windows_event(message, level, "System", event_id)

        log_method = getattr(self.sys_logger, level, self.sys_logger.info)
        log_method(message)

        self.debug_logger.debug(f"SYS[{level.upper()}]: {message}")

        return success

    def log_security(self, message, level="info", event_id=3000):
        """Log to Security log - use success_audit/failure_audit for auth events"""
        success = self._log_to_windows_event(message, level, "Security", event_id)

        log_method = getattr(self.sec_logger, level, self.sec_logger.info)
        log_method(message)

        self.debug_logger.debug(f"SEC[{level.upper()}]: {message}")

        return success

    def log_audit(self, message, event_type="info", user=None, resource=None):
        """Custom audit logging for business events"""
        audit_message = f"ACTION[{event_type}]"
        if user:
            audit_message += f" USER[{user}]"
        if resource:
            audit_message += f" RESOURCE[{resource}]"
        audit_message += f" - {message}"

        # Log to custom audit log file
        self.audit_logger.info(audit_message)

        # Also log to debug
        self.debug_logger.debug(f"AUDIT: {audit_message}")

        return True

    def log_debug(self, message):
        """Detailed debug logging"""
        self.debug_logger.debug(message)
        return True

    def log_performance(self, operation, duration_ms, details=""):
        """Specialized performance logging"""
        perf_message = f"PERF: {operation} took {duration_ms}ms"
        if details:
            perf_message += f" - {details}"

        self.debug_logger.info(perf_message)
        return True


class ContextFilter(logging.Filter):
    """Add contextual information to log records"""

    def __init__(self, hostname, username):
        super().__init__()
        self.hostname = hostname
        self.username = username

    def filter(self, record):
        record.hostname = self.hostname
        record.user = self.username
        return True


# Utility functions for easy access
def get_pygen_logger(app_name="PygenLogger", log_dir="logs"):
    """Get a configured PygenLogger instance"""
    return PygenLogger(app_name, log_dir)


# Example usage and demonstration
if __name__ == "__main__":
    # Initialize the logger
    logger = get_pygen_logger("Project", "logs")

    print("Project Logging System Demonstration")
    print("=========================================")

    # Log to different destinations
    logger.log_application("Application started successfully", "info", 1001)
    logger.log_system("System check completed", "info", 2001)
    logger.log_security("User login attempted", "success_audit", 3001)

    # Custom audit logging
    logger.log_audit(
        "Document accessed", event_type="read", user="admin", resource="report.pdf"
    )

    # Debug logging
    logger.log_debug("Detailed debug information for troubleshooting")

    # Performance logging
    logger.log_performance("Database query", 145, "SELECT * FROM users")

    # Error handling example
    try:
        # Simulate an error
        raise ValueError("This is a test error")
    except Exception as e:
        logger.log_application(f"Error occurred: {e}", "error", 1002)

    print(
        "Logging demonstration completed. Check the logs directory and Windows Event Viewer."
    )



#example usage in another script:

# from pygen_modules.logging import get_pygen_logger

# logger = get_pygen_logger("Project", "logs")

# logger.log_application("Test info event", "info")
# logger.log_system("Test warning event", "warning")
# logger.log_security("Test audit success", "success_audit")
# logger.log_audit("User downloaded file", event_type="download", user="alice")
# logger.log_debug("Debug trace here")