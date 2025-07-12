from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from datetime import datetime

from core.database import get_db
from fastapi import Cookie
from core.auth import verify_token
from models.user import User, UserFollow
from services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

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

# Profile routes
@router.get("/{username}", response_class=HTMLResponse)
async def view_profile(request: Request, username: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """View a user's profile page"""
    profile_service = ProfileService(db)
    
    # Get the profile user
    profile_user = profile_service.get_user_by_username(username)
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user stats
    stats = profile_service.get_user_stats(profile_user.id)
    
    # Check if current user is following this profile
    is_following = False
    if current_user_obj:
        is_following = profile_service.is_following(current_user_obj.id, profile_user.id)
    
    # Get user's posts
    posts = profile_service.get_user_posts(profile_user.id)
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile_user": profile_user,
        "current_user": current_user_obj,
        "stats": stats,
        "is_following": is_following,
        "posts": posts
    })

@router.get("/edit", response_class=HTMLResponse)
async def edit_profile_page(request: Request, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj)):
    """Show profile editing page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "current_user": current_user_obj
    })

@router.post("/edit")
async def update_profile(
    request: Request,
    full_name: str = Form(None),
    bio: str = Form(None),
    location: str = Form(None),
    website: str = Form(None),
    avatar: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user),
    current_user_obj: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    profile_service = ProfileService(db)
    
    # Handle avatar upload
    avatar_url = None
    if avatar and avatar.filename:
        avatar_url = await profile_service.upload_avatar(avatar, current_user_obj.username)
    
    # Update profile
    updated_user = profile_service.update_profile(
        user_id=current_user_obj.id,
        full_name=full_name,
        bio=bio,
        location=location,
        website=website,
        avatar_url=avatar_url
    )
    
    return RedirectResponse(url=f"/profile/{current_user_obj.username}", status_code=302)

# Follow/Unfollow routes
@router.post("/{username}/follow")
async def follow_user(request: Request, username: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Follow a user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profile_service = ProfileService(db)
    target_user = profile_service.get_user_by_username(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user_obj.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    success = profile_service.follow_user(current_user_obj.id, target_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    return {"message": "Successfully followed user"}

@router.post("/{username}/unfollow")
async def unfollow_user(request: Request, username: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Unfollow a user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profile_service = ProfileService(db)
    target_user = profile_service.get_user_by_username(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = profile_service.unfollow_user(current_user_obj.id, target_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Not following this user")
    
    return {"message": "Successfully unfollowed user"}

# Followers/Following pages
@router.get("/{username}/followers", response_class=HTMLResponse)
async def view_followers(request: Request, username: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """View a user's followers"""
    profile_service = ProfileService(db)
    
    profile_user = profile_service.get_user_by_username(username)
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    followers = profile_service.get_followers(profile_user.id)
    
    return templates.TemplateResponse("followers.html", {
        "request": request,
        "profile_user": profile_user,
        "current_user": current_user_obj,
        "followers": followers
    })

@router.get("/{username}/following", response_class=HTMLResponse)
async def view_following(request: Request, username: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """View who a user is following"""
    profile_service = ProfileService(db)
    
    profile_user = profile_service.get_user_by_username(username)
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    following = profile_service.get_following(profile_user.id)
    
    return templates.TemplateResponse("following.html", {
        "request": request,
        "profile_user": profile_user,
        "current_user": current_user_obj,
        "following": following
    }) 