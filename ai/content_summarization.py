"""
Content Summarization AI Service
Creates concise summaries of posts and content
"""
import logging
from typing import Dict, Any, Optional
from .base_ai import BaseAIService

logger = logging.getLogger(__name__)

class ContentSummarizationService(BaseAIService):
    """AI-powered content summarization"""
    
    def __init__(self):
        super().__init__()
        self.summarization_model = "facebook/bart-large-cnn"
        self.max_length = 150
    
    async def process(self, content: str) -> Dict[str, Any]:
        """Generate a summary of the content"""
        try:
            # Try OpenAI first (better quality)
            if self._validate_api_key(self.openai_api_key, "OpenAI"):
                return await self._summarize_with_openai(content)
            
            # Fallback to Hugging Face
            if self._validate_api_key(self.hf_api_key, "Hugging Face"):
                return await self._summarize_with_huggingface(content)
            
            return self._fallback_summarization(content)
            
        except Exception as e:
            self._log_error(e, "Content Summarization")
            return self._fallback_summarization(content)
    
    async def _summarize_with_openai(self, content: str) -> Dict[str, Any]:
        """Summarize using OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
        Please provide a concise summary of the following text in 2-3 sentences:
        
        {content}
        
        Summary:
        """
        
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that creates concise summaries."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data["choices"][0]["message"]["content"].strip()
            return {
                "summary": summary,
                "original_length": len(content),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(content) if len(content) > 0 else 0,
                "ai_processed": True,
                "model": "openai"
            }
        else:
            raise Exception(f"OpenAI API error: {response.status_code}")
    
    async def _summarize_with_huggingface(self, content: str) -> Dict[str, Any]:
        """Summarize using Hugging Face models"""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        response = await self.client.post(
            f"https://api-inference.huggingface.co/models/{self.summarization_model}",
            headers=headers,
            json={
                "inputs": content,
                "parameters": {
                    "max_length": self.max_length,
                    "min_length": 30,
                    "do_sample": False
                }
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data[0]["summary_text"] if data else ""
            
            return {
                "summary": summary,
                "original_length": len(content),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(content) if len(content) > 0 else 0,
                "ai_processed": True,
                "model": "huggingface"
            }
        else:
            raise Exception(f"Hugging Face API error: {response.status_code}")
    
    def _fallback_summarization(self, content: str) -> Dict[str, Any]:
        """Fallback summarization when AI is not available"""
        # Simple extractive summarization
        sentences = content.split('.')
        if len(sentences) <= 2:
            summary = content
        else:
            # Take first two sentences as summary
            summary = '. '.join(sentences[:2]) + '.'
        
        return {
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(content) if len(content) > 0 else 0,
            "ai_processed": False,
            "model": "fallback"
        } 