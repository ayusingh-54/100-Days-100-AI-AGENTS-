"""
Utilities module for the AutoGen Web Info Agent
"""
import logging
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

# Configure logging
logger = logging.getLogger(__name__)


class Logger:
    """Custom logger for the application"""
    
    @staticmethod
    def setup(name: str, level: str = "INFO") -> logging.Logger:
        """Setup logger with formatting"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


class MessageProcessor:
    """Process and format agent messages"""
    
    @staticmethod
    def extract_code(content: str) -> Optional[str]:
        """Extract code blocks from message"""
        pattern = r'```(?:python)?\s*\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        return matches[0] if matches else None
    
    @staticmethod
    def clean_message(content: str) -> str:
        """Clean and format message content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\n+', '\n\n', content)
        content = content.strip()
        return content
    
    @staticmethod
    def extract_key_findings(content: str) -> List[str]:
        """Extract key findings from content"""
        findings = []
        
        # Look for bullet points or numbered lists
        bullet_pattern = r'[•\-\*]\s+(.+?)(?=\n|$)'
        bullets = re.findall(bullet_pattern, content)
        findings.extend(bullets)
        
        # Look for numbered items
        num_pattern = r'\d+\.\s+(.+?)(?=\n|$)'
        numbers = re.findall(num_pattern, content)
        findings.extend(numbers)
        
        return findings[:10]  # Return top 10 findings


class ConversationManager:
    """Manage conversation history and state"""
    
    def __init__(self):
        """Initialize conversation manager"""
        self.history: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
    
    def add_message(self, sender: str, content: str, message_type: str = "text"):
        """Add message to history"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": content,
            "type": message_type
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.history
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        self.start_time = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "total_messages": len(self.history),
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "senders": list(set(m["sender"] for m in self.history))
        }
    
    def export_to_json(self) -> str:
        """Export conversation to JSON"""
        return json.dumps({
            "metadata": self.get_summary(),
            "conversation": self.history
        }, indent=2)


class ErrorHandler:
    """Handle and format errors"""
    
    @staticmethod
    def format_error(error: Exception, context: str = "") -> str:
        """Format error with context"""
        error_msg = f"❌ Error"
        if context:
            error_msg += f" in {context}"
        error_msg += f": {str(error)}\n"
        error_msg += f"Details: {traceback.format_exc()}"
        return error_msg
    
    @staticmethod
    def is_retryable(error: Exception) -> bool:
        """Check if error is retryable"""
        retryable_errors = (
            TimeoutError,
            ConnectionError,
            RuntimeError,
        )
        return isinstance(error, retryable_errors)
    
    @staticmethod
    def get_user_friendly_message(error: Exception) -> str:
        """Get user-friendly error message"""
        error_type = type(error).__name__
        error_str = str(error)
        
        if "API" in error_str:
            return f"🔌 API Error: Unable to connect to the service. Please check your API configuration."
        elif "timeout" in error_str.lower():
            return f"⏱️ Timeout Error: The request took too long. Please try again."
        elif "authentication" in error_str.lower():
            return f"🔐 Authentication Error: Please verify your API credentials."
        else:
            return f"⚠️ Error: {error_str}"


class TaskValidator:
    """Validate user inputs and tasks"""
    
    @staticmethod
    def validate_url(url: str) -> tuple[bool, Optional[str]]:
        """Validate URL format"""
        url_pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
        
        if not re.match(url_pattern, url):
            return False, "Invalid URL format"
        
        return True, None
    
    @staticmethod
    def validate_query(query: str, min_length: int = 5, max_length: int = 2000) -> tuple[bool, Optional[str]]:
        """Validate query input"""
        query = query.strip()
        
        if len(query) < min_length:
            return False, f"Query must be at least {min_length} characters long"
        
        if len(query) > max_length:
            return False, f"Query must not exceed {max_length} characters"
        
        return True, None
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitize user input"""
        # Remove potential code injection attempts
        dangerous_patterns = [
            r'__import__',
            r'exec\(',
            r'eval\(',
            r'os\.',
            r'subprocess\.',
        ]
        
        sanitized = user_input
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        """Initialize performance monitor"""
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.now(),
            "operations": []
        }
    
    def record_operation(self, operation: str, duration: float, status: str = "success"):
        """Record an operation"""
        self.metrics["operations"].append({
            "operation": operation,
            "duration_ms": duration * 1000,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        operations = self.metrics["operations"]
        
        if not operations:
            return {
                "total_operations": 0,
                "average_duration": 0,
                "total_duration": 0
            }
        
        total_duration = sum(op["duration_ms"] for op in operations)
        
        return {
            "total_operations": len(operations),
            "average_duration_ms": total_duration / len(operations),
            "total_duration_ms": total_duration,
            "success_rate": sum(1 for op in operations if op["status"] == "success") / len(operations) * 100
        }
