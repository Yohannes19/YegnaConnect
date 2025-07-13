"""
Content Moderation AI Service
Uses Hugging Face models to detect inappropriate content
"""
import logging
from typing import Dict, Any, List
from .base_ai import BaseAIService

logger = logging.getLogger(__name__)

class ContentModerationService(BaseAIService):
    """AI-powered content moderation"""
    
    def __init__(self):
        super().__init__()
        self.toxicity_model = "unitary/toxic-bert"
        self.hate_speech_model = "facebook/roberta-hate-speech-detector"
    
    async def process(self, content: str) -> Dict[str, Any]:
        """Analyze content for inappropriate material"""
        try:
            if not self._validate_api_key(self.hf_api_key, "Hugging Face"):
                return self._fallback_moderation(content)
            
            results = await self._analyze_content(content)
            return {
                "is_appropriate": results["is_appropriate"],
                "toxicity_score": results["toxicity_score"],
                "hate_speech_score": results["hate_speech_score"],
                "confidence": results["confidence"],
                "flags": results["flags"],
                "ai_processed": True
            }
        except Exception as e:
            self._log_error(e, "Content Moderation")
            return self._fallback_moderation(content)
    
    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content using Hugging Face models"""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        # Analyze toxicity
        toxicity_response = await self.client.post(
            f"https://api-inference.huggingface.co/models/{self.toxicity_model}",
            headers=headers,
            json={"inputs": content}
        )
        
        # Analyze hate speech
        hate_response = await self.client.post(
            f"https://api-inference.huggingface.co/models/{self.hate_speech_model}",
            headers=headers,
            json={"inputs": content}
        )
        
        toxicity_data = toxicity_response.json() if toxicity_response.status_code == 200 else []
        hate_data = hate_response.json() if hate_response.status_code == 200 else []
        
        # Process results
        toxicity_score = self._extract_toxicity_score(toxicity_data)
        hate_score = self._extract_hate_score(hate_data)
        
        # Determine if content is appropriate
        is_appropriate = toxicity_score < 0.7 and hate_score < 0.7
        confidence = max(toxicity_score, hate_score)
        
        flags = []
        if toxicity_score > 0.5:
            flags.append("potentially_toxic")
        if hate_score > 0.5:
            flags.append("potentially_hateful")
        
        return {
            "is_appropriate": is_appropriate,
            "toxicity_score": toxicity_score,
            "hate_speech_score": hate_score,
            "confidence": confidence,
            "flags": flags
        }
    
    def _extract_toxicity_score(self, data: List) -> float:
        """Extract toxicity score from model output"""
        try:
            if not data or not isinstance(data, list):
                return 0.0
            
            # Look for toxic label
            for item in data:
                if isinstance(item, dict) and "label" in item:
                    label = item.get("label", "").lower()
                    if "toxic" in label:
                        return item.get("score", 0.0)
            
            # If no toxic label found, return highest score
            max_score = 0.0
            for item in data:
                if isinstance(item, dict):
                    score = item.get("score", 0.0)
                    if score > max_score:
                        max_score = score
            
            return max_score
        except Exception as e:
            logger.error(f"Error extracting toxicity score: {e}")
            return 0.0
    
    def _extract_hate_score(self, data: List) -> float:
        """Extract hate speech score from model output"""
        try:
            if not data or not isinstance(data, list):
                return 0.0
            
            # Look for hate label
            for item in data:
                if isinstance(item, dict) and "label" in item:
                    label = item.get("label", "").lower()
                    if "hate" in label:
                        return item.get("score", 0.0)
            
            # If no hate label found, return highest score
            max_score = 0.0
            for item in data:
                if isinstance(item, dict):
                    score = item.get("score", 0.0)
                    if score > max_score:
                        max_score = score
            
            return max_score
        except Exception as e:
            logger.error(f"Error extracting hate score: {e}")
            return 0.0
    
    def _fallback_moderation(self, content: str) -> Dict[str, Any]:
        """Fallback moderation when AI is not available"""
        # Simple keyword-based moderation
        inappropriate_keywords = [
            "hate", "racist", "discriminatory", "violent", "threat",
            "abuse", "harassment", "bully", "intimidate"
        ]
        
        content_lower = content.lower()
        flags = []
        
        for keyword in inappropriate_keywords:
            if keyword in content_lower:
                flags.append(f"contains_{keyword}")
        
        return {
            "is_appropriate": len(flags) == 0,
            "toxicity_score": 0.3 if flags else 0.0,
            "hate_speech_score": 0.2 if flags else 0.0,
            "confidence": 0.5,
            "flags": flags,
            "ai_processed": False
        } 