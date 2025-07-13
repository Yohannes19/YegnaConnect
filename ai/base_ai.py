"""
Base AI Service - Foundation for all AI functionality
"""
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import httpx
from config import settings

logger = logging.getLogger(__name__)

class BaseAIService(ABC):
    """Base class for all AI services"""
    
    def __init__(self):
        self.hf_api_key = settings.AI_HF_API_KEY
        self.openai_api_key = settings.AI_OPENAI_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @abstractmethod
    async def process(self, content: str) -> Dict[str, Any]:
        """Process content with AI"""
        pass
    
    def _log_error(self, error: Exception, context: str = ""):
        """Log AI processing errors"""
        logger.error(f"AI Error in {context}: {str(error)}")
    
    def _validate_api_key(self, api_key: Optional[str], service_name: str) -> bool:
        """Validate API key exists"""
        if not api_key:
            logger.warning(f"{service_name} API key not configured")
            return False
        return True 