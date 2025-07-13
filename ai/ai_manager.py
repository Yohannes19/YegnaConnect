"""
AI Service Manager
Coordinates all AI functionality in the application
"""
import logging
from typing import Dict, Any, Optional
from .content_moderation import ContentModerationService
from .sentiment_analysis import SentimentAnalysisService
from .content_summarization import ContentSummarizationService

logger = logging.getLogger(__name__)

class AIManager:
    """Manages all AI services"""
    
    def __init__(self):
        self.moderation_service = ContentModerationService()
        self.sentiment_service = SentimentAnalysisService()
        self.summarization_service = ContentSummarizationService()
    
    async def analyze_post(self, content: str) -> Dict[str, Any]:
        """Comprehensive analysis of a post"""
        try:
            async with self.moderation_service as mod_service:
                moderation_result = await mod_service.process(content)
            
            async with self.sentiment_service as sent_service:
                sentiment_result = await sent_service.process(content)
            
            async with self.summarization_service as sum_service:
                summary_result = await sum_service.process(content)
            
            return {
                "moderation": moderation_result,
                "sentiment": sentiment_result,
                "summary": summary_result,
                "overall_score": self._calculate_overall_score(moderation_result, sentiment_result),
                "recommendations": self._generate_recommendations(moderation_result, sentiment_result)
            }
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return self._fallback_analysis(content)
    
    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Content moderation only"""
        async with self.moderation_service as service:
            return await service.process(content)
    
    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Sentiment analysis only"""
        async with self.sentiment_service as service:
            return await service.process(content)
    
    async def summarize_content(self, content: str) -> Dict[str, Any]:
        """Content summarization only"""
        async with self.summarization_service as service:
            return await service.process(content)
    
    def _calculate_overall_score(self, moderation: Dict, sentiment: Dict) -> float:
        """Calculate overall content quality score"""
        # Moderation score (higher is better)
        mod_score = 1.0 - max(
            moderation.get("toxicity_score", 0),
            moderation.get("hate_speech_score", 0)
        )
        
        # Sentiment score (neutral is 0.5, positive/negative can be higher/lower)
        sent_score = sentiment.get("sentiment_score", 0.5)
        
        # Combine scores (moderation weighted more heavily)
        overall = (mod_score * 0.7) + (sent_score * 0.3)
        return max(0.0, min(1.0, overall))
    
    def _generate_recommendations(self, moderation: Dict, sentiment: Dict) -> list:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Moderation recommendations
        if not moderation.get("is_appropriate", True):
            recommendations.append("Consider revising content to be more appropriate")
        
        if moderation.get("toxicity_score", 0) > 0.5:
            recommendations.append("Content may be perceived as toxic")
        
        if moderation.get("hate_speech_score", 0) > 0.5:
            recommendations.append("Content may contain hate speech")
        
        # Sentiment recommendations
        sentiment_type = sentiment.get("sentiment", "neutral")
        if sentiment_type == "negative":
            recommendations.append("Consider adding more positive language")
        elif sentiment_type == "positive":
            recommendations.append("Great positive tone!")
        
        emotion = sentiment.get("emotion", "neutral")
        if emotion in ["anger", "fear", "sadness"]:
            recommendations.append(f"Content expresses {emotion} - consider tone")
        
        return recommendations
    
    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when AI services fail"""
        return {
            "moderation": {
                "is_appropriate": True,
                "toxicity_score": 0.0,
                "hate_speech_score": 0.0,
                "confidence": 0.5,
                "flags": [],
                "ai_processed": False
            },
            "sentiment": {
                "sentiment": "neutral",
                "sentiment_score": 0.5,
                "emotion": "neutral",
                "emotion_score": 0.5,
                "confidence": 0.5,
                "ai_processed": False
            },
            "summary": {
                "summary": content[:100] + "..." if len(content) > 100 else content,
                "original_length": len(content),
                "summary_length": min(100, len(content)),
                "compression_ratio": 0.5,
                "ai_processed": False,
                "model": "fallback"
            },
            "overall_score": 0.5,
            "recommendations": ["AI analysis unavailable"]
        } 