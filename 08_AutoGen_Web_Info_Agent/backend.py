"""
Simplified Backend for Web Info Agent
Uses OpenAI directly for a working, robust implementation
"""
import os
import sys
import time
import json
from typing import Dict, Any, Optional, Callable, List
from config import Config
from utils import Logger, ErrorHandler, ConversationManager, TaskValidator, PerformanceMonitor

try:
    from openai import OpenAI, APIError
except ImportError:
    raise ImportError("Please install openai: pip install openai")

# Setup logger
logger = Logger.setup(__name__, Config.LOG_LEVEL)


class SimpleAgentManager:
    """Manages agents with direct OpenAI API calls"""
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """Initialize agent manager"""
        self.config = config_dict or self._load_config()
        self.client = None
        self.conversation_manager = ConversationManager()
        self.performance_monitor = PerformanceMonitor()
        self.error_handler = ErrorHandler()
        self.validator = TaskValidator()
        self.chat_history = []
        
        logger.info("SimpleAgentManager initialized")
        self.setup_agents()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and validate configuration"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            
            config = {
                "api_key": api_key,
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            logger.info(f"Configuration loaded with model: {config['model']}")
            return config
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    def setup_agents(self) -> bool:
        """Setup OpenAI client"""
        try:
            start_time = time.time()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set")
                return False
            
            self.client = OpenAI(api_key=api_key)
            
            # Test connection
            try:
                response = self.client.models.list()
                logger.info(f"Connected to OpenAI API successfully")
            except Exception as e:
                logger.error(f"Failed to connect to OpenAI API: {str(e)}")
                return False
            
            duration = time.time() - start_time
            self.performance_monitor.record_operation("setup_agents", duration)
            
            logger.info(f"Agent setup completed in {duration:.2f}s")
            return True
        
        except Exception as e:
            error_msg = self.error_handler.format_error(e, "setup_agents")
            logger.error(error_msg)
            return False
    
    def initiate_chat(
        self, 
        message: str,
        on_message_callback: Optional[Callable] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """Initiate chat with improved error handling"""
        
        # Validate input
        is_valid, error = self.validator.validate_query(message)
        if not is_valid:
            logger.warning(f"Input validation failed: {error}")
            return error
        
        message = self.validator.sanitize_input(message)
        
        if not self.client:
            logger.error("Client not initialized. Call setup_agents() first.")
            return "❌ Client not initialized. Please setup agents first."
        
        try:
            start_time = time.time()
            
            # Add message to conversation history
            self.conversation_manager.add_message("user", message, "task")
            self.chat_history.append({"role": "user", "content": message})
            
            logger.info(f"Starting chat with message: {message[:100]}...")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-3.5-turbo"),
                messages=self.chat_history,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2000)
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            self.chat_history.append({"role": "assistant", "content": assistant_message})
            
            duration = time.time() - start_time
            self.performance_monitor.record_operation("chat", duration)
            
            logger.info(f"Chat completed in {duration:.2f}s")
            
            # Add to conversation manager
            self.conversation_manager.add_message("assistant", assistant_message, "response")
            
            return assistant_message
        
        except APIError as e:
            error_msg = f"OpenAI API Error: {str(e)}"
            logger.error(f"Chat failed: {error_msg}")
            self.conversation_manager.add_message("system", error_msg, "error")
            return error_msg
        
        except Exception as e:
            error_msg = self.error_handler.get_user_friendly_message(e)
            logger.error(f"Chat failed: {str(e)}")
            self.conversation_manager.add_message("system", error_msg, "error")
            return error_msg
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_manager.get_history()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return self.conversation_manager.get_summary()
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_manager.clear_history()
        self.chat_history = []
        logger.info("Conversation history cleared")
    
    def export_conversation(self) -> str:
        """Export conversation to JSON"""
        return self.conversation_manager.export_to_json()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.performance_monitor.get_stats()
    
    def reset(self):
        """Reset agent manager"""
        self.chat_history = []
        self.conversation_manager.clear_history()
        logger.info("Agent manager reset")


# Alias for compatibility
class AutoGenAgentManager(SimpleAgentManager):
    """Compatibility alias for AutoGenAgentManager"""
    pass


class TaskExecutor:
    """Execute predefined tasks"""
    
    def __init__(self, agent_manager: SimpleAgentManager):
        """Initialize task executor"""
        self.agent_manager = agent_manager
        self.logger = Logger.setup(__name__, Config.LOG_LEVEL)
    
    def execute_paper_analysis(self, url: str) -> str:
        """Execute paper analysis task"""
        validator = TaskValidator()
        is_valid, error = validator.validate_url(url)
        
        if not is_valid:
            return f"❌ {error}: {url}"
        
        message = f"""Please analyze this paper/article: {url}
        
Provide:
1. Summary of the main content
2. Key findings or arguments
3. Who should read this
4. Practical applications
5. Strengths and limitations"""
        
        return self.agent_manager.initiate_chat(message) or "Analysis failed"
    
    def execute_stock_market_analysis(self, query: str) -> str:
        """Execute stock market analysis task"""
        message = f"""Please analyze the stock market query: {query}
        
Provide:
1. Current market conditions
2. Relevant data and statistics
3. Market analysis and trends
4. Investment considerations
5. Risk assessment"""
        
        return self.agent_manager.initiate_chat(message) or "Analysis failed"
    
    def execute_web_research(self, topic: str) -> str:
        """Execute web research task"""
        message = f"""Please research and provide comprehensive information about: {topic}
        
Include:
1. Overview and background
2. Key points and findings
3. Recent developments
4. Relevant statistics or data
5. Resources and further reading"""
        
        return self.agent_manager.initiate_chat(message) or "Research failed"
    
    def execute_custom_task(self, task: str) -> str:
        """Execute custom task"""
        return self.agent_manager.initiate_chat(task) or "Task failed"


# Global agent manager instance
_agent_manager: Optional[SimpleAgentManager] = None


def get_agent_manager() -> SimpleAgentManager:
    """Get or create global agent manager"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = SimpleAgentManager()
    return _agent_manager


def initialize_agent_manager() -> bool:
    """Initialize the agent manager"""
    global _agent_manager
    try:
        _agent_manager = SimpleAgentManager()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize agent manager: {str(e)}")
        return False
