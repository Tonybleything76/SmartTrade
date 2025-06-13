"""
Logging utility for the multi-agent system
Provides centralized logging configuration
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """Setup logger with JSON formatting and appropriate handlers"""
    
    # Get log level from environment or default to INFO
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Create formatter
    use_json_logging = os.getenv("JSON_LOGGING", "true").lower() == "true"
    
    if use_json_logging:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    log_file = os.getenv("LOG_FILE")
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level, logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")
    
    return logger

class SystemLogger:
    """System-wide logger with additional context tracking"""
    
    def __init__(self, system_name: str = "MultiAgentContentSystem"):
        self.system_name = system_name
        self.logger = setup_logger(system_name)
        self.session_id = self.generate_session_id()
    
    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def log_system_event(self, event_type: str, message: str, metadata: Dict[str, Any] = None, level: str = "info"):
        """Log system events with structured context"""
        
        extra_fields = {
            "event_type": event_type,
            "system": self.system_name,
            "session_id": self.session_id
        }
        
        if metadata:
            extra_fields.update(metadata)
        
        # Create log record with extra fields
        log_record = logging.LogRecord(
            name=self.logger.name,
            level=getattr(logging, level.upper(), logging.INFO),
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        log_record.extra_fields = extra_fields
        
        self.logger.handle(log_record)
    
    def log_agent_communication(self, from_agent: str, to_agent: str, message_type: str, success: bool = True, metadata: Dict[str, Any] = None):
        """Log inter-agent communication"""
        
        communication_data = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "success": success
        }
        
        if metadata:
            communication_data.update(metadata)
        
        level = "info" if success else "warning"
        self.log_system_event("agent_communication", f"{from_agent} -> {to_agent}: {message_type}", communication_data, level)
    
    def log_workflow_stage(self, stage: str, status: str, metadata: Dict[str, Any] = None):
        """Log workflow stage transitions"""
        
        workflow_data = {
            "workflow_stage": stage,
            "status": status
        }
        
        if metadata:
            workflow_data.update(metadata)
        
        level = "info" if status in ["started", "completed"] else "warning" if status == "failed" else "info"
        self.log_system_event("workflow_stage", f"Workflow stage {stage}: {status}", workflow_data, level)
    
    def log_content_pipeline(self, pipeline_id: str, stage: str, status: str, metadata: Dict[str, Any] = None):
        """Log content pipeline events"""
        
        pipeline_data = {
            "pipeline_id": pipeline_id,
            "pipeline_stage": stage,
            "status": status
        }
        
        if metadata:
            pipeline_data.update(metadata)
        
        level = "info" if status == "success" else "error" if status == "failed" else "info"
        self.log_system_event("content_pipeline", f"Pipeline {pipeline_id} - {stage}: {status}", pipeline_data, level)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "", metadata: Dict[str, Any] = None):
        """Log performance metrics"""
        
        metric_data = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit
        }
        
        if metadata:
            metric_data.update(metadata)
        
        self.log_system_event("performance_metric", f"{metric_name}: {value} {unit}", metric_data)

# Global system logger instance
system_logger = SystemLogger()

def get_system_logger() -> SystemLogger:
    """Get the global system logger instance"""
    return system_logger

# Convenience functions
def log_agent_action(agent_name: str, action: str, success: bool = True, metadata: Dict[str, Any] = None):
    """Log agent actions"""
    system_logger.log_system_event("agent_action", f"{agent_name}: {action}", 
                                   {"agent": agent_name, "action": action, "success": success, **(metadata or {})},
                                   level="info" if success else "error")

def log_api_call(api_name: str, endpoint: str, status_code: int, duration_ms: float, metadata: Dict[str, Any] = None):
    """Log API calls"""
    api_data = {
        "api_name": api_name,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "success": 200 <= status_code < 300
    }
    
    if metadata:
        api_data.update(metadata)
    
    level = "info" if api_data["success"] else "error"
    system_logger.log_system_event("api_call", f"{api_name} {endpoint}: {status_code} ({duration_ms}ms)", api_data, level)

def log_error(error_type: str, error_message: str, metadata: Dict[str, Any] = None):
    """Log errors with context"""
    error_data = {
        "error_type": error_type,
        "error_message": error_message
    }
    
    if metadata:
        error_data.update(metadata)
    
    system_logger.log_system_event("error", f"{error_type}: {error_message}", error_data, level="error")
