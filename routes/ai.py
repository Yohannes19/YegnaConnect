"""
AI Routes - AI-powered features and content analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Cookie, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
from sqlalchemy import func
import os

from core.database import get_db
from core.auth import verify_token
from models.user import User
from models.post import Post, Comment
from ai import AIManager

router = APIRouter(prefix="/ai", tags=["AI Features"])
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Initialize AI Manager
ai_manager = AIManager()

def get_current_user(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        return None
    username = verify_token(access_token)
    if username:
        user = db.query(User).filter(User.username == username).first()
        return user.username if user else None
    return None

def get_current_user_obj(access_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not access_token:
        return None
    username = verify_token(access_token)
    if username:
        user = db.query(User).filter(User.username == username).first()
        return user
    return None

@router.post("/analyze-post")
async def analyze_post(
    content: str = Form(...),
    current_user_obj: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Analyze post content with AI"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        analysis = await ai_manager.analyze_post(content)
        
        return JSONResponse({
            "success": True,
            "analysis": analysis,
            "recommendations": analysis.get("recommendations", [])
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/moderate-content")
async def moderate_content(
    content: str = Form(...),
    current_user_obj: User = Depends(get_current_user_obj)
):
    """Moderate content for inappropriate material"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        moderation = await ai_manager.moderate_content(content)
        
        return JSONResponse({
            "success": True,
            "is_appropriate": moderation.get("is_appropriate", True),
            "toxicity_score": moderation.get("toxicity_score", 0),
            "hate_speech_score": moderation.get("hate_speech_score", 0),
            "flags": moderation.get("flags", [])
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content moderation failed: {str(e)}")

@router.post("/analyze-sentiment")
async def analyze_sentiment(
    content: str = Form(...),
    current_user_obj: User = Depends(get_current_user_obj)
):
    """Analyze sentiment of content"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        sentiment = await ai_manager.analyze_sentiment(content)
        
        return JSONResponse({
            "success": True,
            "sentiment": sentiment.get("sentiment", "neutral"),
            "sentiment_score": sentiment.get("sentiment_score", 0.5),
            "emotion": sentiment.get("emotion", "neutral"),
            "emotion_score": sentiment.get("emotion_score", 0.5)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/summarize-content")
async def summarize_content(
    content: str = Form(...),
    current_user_obj: User = Depends(get_current_user_obj)
):
    """Summarize content using AI"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        summary = await ai_manager.summarize_content(content)
        
        return JSONResponse({
            "success": True,
            "summary": summary.get("summary", ""),
            "original_length": summary.get("original_length", 0),
            "summary_length": summary.get("summary_length", 0),
            "compression_ratio": summary.get("compression_ratio", 0)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content summarization failed: {str(e)}")

@router.post("/posts/{post_id}/analyze")
async def analyze_existing_post(
    post_id: int,
    current_user_obj: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Analyze an existing post with AI"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if user owns the post or is admin
        if post.user_id != current_user_obj.id and current_user_obj.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Analyze the post
        analysis = await ai_manager.analyze_post(post.content)
        
        # Update post with AI analysis
        post.ai_analysis = analysis
        post.moderation_score = int(analysis["moderation"]["confidence"] * 100)
        post.sentiment_score = int(analysis["sentiment"]["sentiment_score"] * 100)
        post.content_summary = analysis["summary"]["summary"]
        post.is_ai_processed = 1
        
        db.commit()
        
        return JSONResponse({
            "success": True,
            "analysis": analysis,
            "post_id": post_id
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post analysis failed: {str(e)}")

@router.get("/posts/{post_id}/analysis")
async def get_post_analysis(
    post_id: int,
    current_user_obj: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get AI analysis for a post"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if not post.ai_analysis:
            raise HTTPException(status_code=404, detail="No AI analysis available")
        
        return JSONResponse({
            "success": True,
            "analysis": post.ai_analysis,
            "moderation_score": post.moderation_score,
            "sentiment_score": post.sentiment_score,
            "content_summary": post.content_summary,
            "is_ai_processed": bool(post.is_ai_processed)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

@router.get("/ai-dashboard", response_class=HTMLResponse)
async def ai_dashboard(
    request: Request,
    current_user_obj: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """AI Dashboard - View AI analysis features"""
    if not current_user_obj:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        # Get user's posts with AI analysis
        posts_with_ai = db.query(Post).filter(
            Post.user_id == current_user_obj.id,
            Post.is_ai_processed == 1
        ).order_by(Post.created_at.desc()).limit(10).all()
        
        # Calculate AI statistics
        total_posts = db.query(Post).filter(Post.user_id == current_user_obj.id).count()
        ai_processed_posts = db.query(Post).filter(
            Post.user_id == current_user_obj.id,
            Post.is_ai_processed == 1
        ).count()
        
        avg_moderation_score = db.query(func.avg(Post.moderation_score)).filter(
            Post.user_id == current_user_obj.id,
            Post.is_ai_processed == 1
        ).scalar() or 0
        
        avg_sentiment_score = db.query(func.avg(Post.sentiment_score)).filter(
            Post.user_id == current_user_obj.id,
            Post.is_ai_processed == 1
        ).scalar() or 50
        
        return templates.TemplateResponse("ai_dashboard.html", {
            "request": request,
            "current_user": current_user_obj,
            "posts_with_ai": posts_with_ai,
            "total_posts": total_posts,
            "ai_processed_posts": ai_processed_posts,
            "avg_moderation_score": round(avg_moderation_score, 1),
            "avg_sentiment_score": round(avg_sentiment_score, 1),
            "ai_processing_rate": round((ai_processed_posts / total_posts * 100) if total_posts > 0 else 0, 1)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load AI dashboard: {str(e)}") 

@router.get("/ai", response_class=HTMLResponse)
def ai_dashboard(request: Request, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj)):
    if not current_user_obj:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("ai_dashboard.html", {
        "request": request,
        "current_user": current_user_obj
    })

@router.post("/ai/analyze-post")
async def analyze_post(content: str = Form(...), current_user_obj: User = Depends(get_current_user_obj)):
    """Real-time AI analysis for post preview"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    try:
        ai_manager = AIManager()
        analysis = await ai_manager.analyze_post(content.strip())
        
        return JSONResponse({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.post("/ai/analyze-comment")
async def analyze_comment(content: str = Form(...), current_user_obj: User = Depends(get_current_user_obj)):
    """Real-time AI analysis for comment preview"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    try:
        ai_manager = AIManager()
        analysis = await ai_manager.analyze_post(content.strip())  # Reuse post analysis for comments
        
        return JSONResponse({
            "success": True,
            "analysis": analysis
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@router.post("/ai/test")
async def test_ai_features(content: str = Form(...), current_user_obj: User = Depends(get_current_user_obj)):
    """Test AI features with custom content"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    try:
        ai_manager = AIManager()
        analysis = await ai_manager.analyze_post(content.strip())
        
        return JSONResponse({
            "success": True,
            "analysis": analysis,
            "recommendations": analysis.get("recommendations", [])
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500) 