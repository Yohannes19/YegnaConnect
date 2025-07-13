from fastapi import APIRouter, Request, Depends, Cookie, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from typing import Optional
from core.auth import verify_token
from core.database import get_db
from sqlalchemy.orm import Session
from models.user import User
from models.post import Comment
from services.post_service import PostService

router = APIRouter()
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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

@router.get("/feed", response_class=HTMLResponse)
def feed_page(request: Request, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    # Get real posts from database with liked status
    current_user_id = current_user_obj.id if current_user_obj else None
    posts = PostService.get_posts_with_users(db, current_user_id)
    
    return templates.TemplateResponse("feed.html", {
        "request": request,
        "current_user": current_user_obj,
        "current_user_id": current_user_id,
        "posts": posts
    })

@router.post("/posts/create")
async def create_post(content: str = Form(...), category_id: Optional[int] = Form(None), current_user_obj: User = Depends(get_current_user_obj)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not content.strip():
        raise HTTPException(status_code=400, detail="Post content cannot be empty")
    
    db = next(get_db())
    try:
        # Use AI analysis for post creation
        result = await PostService.create_post_with_ai_analysis(db, content.strip(), current_user_obj.id, category_id)
        
        # Check if content is appropriate
        if not result["is_appropriate"]:
            return JSONResponse({
                "success": False,
                "message": "Post blocked: Content appears to be inappropriate",
                "warnings": result["warnings"],
                "redirect": "/feed"
            }, status_code=400)
        
        # If there are warnings, show them but allow the post
        if result["warnings"]:
            return JSONResponse({
                "success": True,
                "message": "Post created with warnings",
                "warnings": result["warnings"],
                "redirect": "/feed"
            })
        
        return RedirectResponse(url="/feed", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")

@router.post("/posts/{post_id}/like")
def like_post(post_id: int, current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    success = PostService.like_post(db, current_user_obj.id, post_id)
    if not success:
        return JSONResponse({"message": "Already liked"}, status_code=400)
    return JSONResponse({"message": "Post liked"})

@router.post("/posts/{post_id}/unlike")
def unlike_post(post_id: int, current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    success = PostService.unlike_post(db, current_user_obj.id, post_id)
    if not success:
        return JSONResponse({"message": "Not liked yet"}, status_code=400)
    return JSONResponse({"message": "Post unliked"})

@router.post("/posts/{post_id}/comments")
async def create_comment(post_id: int, content: str = Form(...), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not content.strip():
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    
    try:
        # Use AI analysis for comment creation
        result = await PostService.create_comment_with_ai_analysis(db, content.strip(), current_user_obj.id, post_id)
        
        # Check if content is appropriate
        if not result["is_appropriate"]:
            return JSONResponse({
                "success": False,
                "message": "Comment blocked: Content appears to be inappropriate",
                "warnings": result["warnings"]
            }, status_code=400)
        
        # If there are warnings, show them but allow the comment
        if result["warnings"]:
            return JSONResponse({
                "success": True,
                "message": "Comment created with warnings",
                "comment_id": result["comment"].id,
                "warnings": result["warnings"]
            })
        
        return JSONResponse({
            "success": True,
            "message": "Comment created",
            "comment_id": result["comment"].id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")

@router.get("/posts/{post_id}/comments")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    try:
        comments = PostService.get_comments_for_post(db, post_id)
        return JSONResponse({"comments": comments})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get comments")

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success = PostService.delete_comment(db, comment_id, current_user_obj.id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    
    return JSONResponse({"message": "Comment deleted"})

@router.post("/comments/{comment_id}/like")
def like_comment(comment_id: int, current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    success = PostService.like_comment(db, current_user_obj.id, comment_id)
    if not success:
        return JSONResponse({"message": "Already liked"}, status_code=400)
    return JSONResponse({"message": "Comment liked"})

@router.post("/comments/{comment_id}/unlike")
def unlike_comment(comment_id: int, current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    success = PostService.unlike_comment(db, current_user_obj.id, comment_id)
    if not success:
        return JSONResponse({"message": "Not liked yet"}, status_code=400)
    return JSONResponse({"message": "Comment unliked"}) 

@router.post("/comments/{comment_id}/reply")
async def create_reply(comment_id: int, content: str = Form(...), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not content.strip():
        raise HTTPException(status_code=400, detail="Reply content cannot be empty")
    # Find the parent comment to get the post_id
    parent_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not parent_comment:
        raise HTTPException(status_code=404, detail="Parent comment not found")
    try:
        # Use AI analysis for reply creation
        result = await PostService.create_comment_with_ai_analysis(db, content.strip(), current_user_obj.id, parent_comment.post_id)
        result["comment"].parent_id = comment_id  # Set the parent_id for the reply
        db.commit()
        
        # Check if content is appropriate
        if not result["is_appropriate"]:
            return JSONResponse({
                "success": False,
                "message": "Reply blocked: Content appears to be inappropriate",
                "warnings": result["warnings"]
            }, status_code=400)
        
        # If there are warnings, show them but allow the reply
        if result["warnings"]:
            return JSONResponse({
                "success": True,
                "message": "Reply created with warnings",
                "reply_id": result["comment"].id,
                "warnings": result["warnings"]
            })
        
        return JSONResponse({
            "success": True,
            "message": "Reply created",
            "reply_id": result["comment"].id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reply: {str(e)}")

@router.get("/comments/{comment_id}/replies")
def get_replies(comment_id: int, current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    try:
        current_user_id = current_user_obj.id if current_user_obj else None
        replies = PostService.get_replies_for_comment(db, comment_id, current_user_id)
        return JSONResponse({"replies": replies})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get replies") 