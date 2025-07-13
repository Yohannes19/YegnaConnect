"""
Sentiment Analysis AI Service
Analyzes the emotional tone of posts and comments
"""
import logging
from typing import Dict, Any, List
from .base_ai import BaseAIService

logger = logging.getLogger(__name__)

class SentimentAnalysisService(BaseAIService):
    """AI-powered sentiment analysis"""
    
    def __init__(self):
        super().__init__()
        self.sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.emotion_model = "j-hartmann/emotion-english-distilroberta-base"
    
    async def process(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment and emotions in content"""
        try:
            if not self._validate_api_key(self.hf_api_key, "Hugging Face"):
                return self._fallback_sentiment(content)
            
            results = await self._analyze_sentiment(content)
            return {
                "sentiment": results["sentiment"],
                "sentiment_score": results["sentiment_score"],
                "emotion": results["emotion"],
                "emotion_score": results["emotion_score"],
                "confidence": results["confidence"],
                "ai_processed": True
            }
        except Exception as e:
            self._log_error(e, "Sentiment Analysis")
            return self._fallback_sentiment(content)
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment using Hugging Face models"""
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        
        # Analyze sentiment
        sentiment_response = await self.client.post(
            f"https://api-inference.huggingface.co/models/{self.sentiment_model}",
            headers=headers,
            json={"inputs": content}
        )
        
        # Analyze emotions
        emotion_response = await self.client.post(
            f"https://api-inference.huggingface.co/models/{self.emotion_model}",
            headers=headers,
            json={"inputs": content}
        )
        
        sentiment_data = sentiment_response.json() if sentiment_response.status_code == 200 else []
        emotion_data = emotion_response.json() if emotion_response.status_code == 200 else []
        
        # Process sentiment results
        sentiment_result = self._extract_sentiment(sentiment_data)
        emotion_result = self._extract_emotion(emotion_data)
        
        return {
            "sentiment": sentiment_result["label"],
            "sentiment_score": sentiment_result["score"],
            "emotion": emotion_result["label"],
            "emotion_score": emotion_result["score"],
            "confidence": max(sentiment_result["score"], emotion_result["score"])
        }
    
    def _extract_sentiment(self, data: List) -> Dict[str, Any]:
        """Extract sentiment from model output"""
        try:
            if not data or not isinstance(data, list):
                return {"label": "neutral", "score": 0.5}
            
            # Handle different response formats
            if len(data) == 0:
                return {"label": "neutral", "score": 0.5}
            
            # Find the highest scoring sentiment
            best_result = None
            best_score = 0
            
            for item in data:
                if isinstance(item, dict):
                    score = item.get("score", 0)
                    if score > best_score:
                        best_score = score
                        best_result = item
            
            if not best_result:
                return {"label": "neutral", "score": 0.5}
            
            label_map = {
                "LABEL_0": "negative",
                "LABEL_1": "neutral", 
                "LABEL_2": "positive"
            }
            
            label = best_result.get("label", "LABEL_1")
            return {
                "label": label_map.get(label, "neutral"),
                "score": best_result.get("score", 0.5)
            }
        except Exception as e:
            logger.error(f"Error extracting sentiment: {e}")
            return {"label": "neutral", "score": 0.5}
    
    def _extract_emotion(self, data: List) -> Dict[str, Any]:
        """Extract emotion from model output"""
        try:
            if not data or not isinstance(data, list):
                return {"label": "neutral", "score": 0.5}
            
            # Handle different response formats
            if len(data) == 0:
                return {"label": "neutral", "score": 0.5}
            
            # Find the highest scoring emotion
            best_result = None
            best_score = 0
            
            for item in data:
                if isinstance(item, dict):
                    score = item.get("score", 0)
                    if score > best_score:
                        best_score = score
                        best_result = item
            
            if not best_result:
                return {"label": "neutral", "score": 0.5}
            
            return {
                "label": best_result.get("label", "neutral").lower(),
                "score": best_result.get("score", 0.5)
            }
        except Exception as e:
            logger.error(f"Error extracting emotion: {e}")
            return {"label": "neutral", "score": 0.5}
    
    def _fallback_sentiment(self, content: str) -> Dict[str, Any]:
        """Fallback sentiment analysis when AI is not available"""
        # Simple keyword-based sentiment analysis
        positive_words = [
            "good", "great", "awesome", "amazing", "love", "happy", "joy",
            "excellent", "wonderful", "fantastic", "beautiful", "perfect"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "hate", "sad", "angry", "disappointed",
            "horrible", "worst", "disgusting", "terrible", "upset"
        ]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            score = min(0.8, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            score = min(0.8, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "sentiment_score": score,
            "emotion": "neutral",
            "emotion_score": 0.5,
            "confidence": 0.6,
            "ai_processed": False
        } 