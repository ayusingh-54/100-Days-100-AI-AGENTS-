"""
Configuration management for the AutoGen Web Info Agent
"""
import os
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

load_dotenv()


class Config:
    """Configuration class for the application"""
    
    # API Configuration
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "600"))
    CACHE_SEED = int(os.getenv("CACHE_SEED", "42"))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    MAX_CONSECUTIVE_AUTO_REPLY = int(os.getenv("MAX_CONSECUTIVE_AUTO_REPLY", "10"))
    
    # Model Configuration
    DEFAULT_MODELS = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    FALLBACK_MODELS = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
    
    # Execution Configuration
    USE_DOCKER = os.getenv("USE_DOCKER", "False").lower() == "true"
    WORK_DIR = os.getenv("WORK_DIR", "./work_dir")
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "agent.log")
    
    # Streamlit Configuration
    PAGE_TITLE = "🤖 AutoGen Web Info Agent"
    PAGE_ICON = "🤖"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # Task Templates
    TASK_TEMPLATES = {
        "paper_analysis": {
            "name": "📄 Analyze Research Paper",
            "description": "Analyze a research paper from URL and provide insights",
            "prompt_template": "Who should read this paper: {url}",
            "placeholder": "https://arxiv.org/abs/2308.08155"
        },
        "stock_market": {
            "name": "📈 Stock Market Analysis",
            "description": "Get market insights and financial data",
            "prompt_template": "{query}",
            "placeholder": "Show me the YTD gain of 10 largest technology companies as of today"
        },
        "web_research": {
            "name": "🔍 Web Research",
            "description": "Research any topic on the web",
            "prompt_template": "{query}",
            "placeholder": "Research the latest developments in AI safety"
        },
        "custom": {
            "name": "⚙️ Custom Task",
            "description": "Create a custom task",
            "prompt_template": "{query}",
            "placeholder": "Enter your custom task..."
        }
    }
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            "timeout": cls.API_TIMEOUT,
            "cache_seed": cls.CACHE_SEED,
            "temperature": cls.LLM_TEMPERATURE,
        }
    
    @classmethod
    def validate_config(cls) -> tuple[bool, Optional[str]]:
        """Validate configuration"""
        try:
            if not os.getenv("OPENAI_API_KEY") and not os.getenv("OAI_CONFIG_LIST"):
                return False, "OpenAI API key not configured. Set OPENAI_API_KEY or OAI_CONFIG_LIST environment variable."
            
            if cls.USE_DOCKER:
                try:
                    import docker
                    docker.from_env()
                except Exception as e:
                    return False, f"Docker is not available or not running: {str(e)}"
            
            return True, None
        except Exception as e:
            return False, f"Configuration validation failed: {str(e)}"
