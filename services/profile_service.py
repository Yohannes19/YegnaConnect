from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import UploadFile
import os
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any

from models.user import User, UserFollow
from models.post import Post, PostLike, Comment, CommentLike

class ProfileService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        # Count posts
        posts_count = self.db.query(Post).filter(Post.user_id == user_id).count()
        
        # Count followers
        followers_count = self.db.query(UserFollow).filter(UserFollow.followed_id == user_id).count()
        
        # Count following
        following_count = self.db.query(UserFollow).filter(UserFollow.follower_id == user_id).count()
        
        # Count total likes received on posts
        total_likes = self.db.query(PostLike).join(Post).filter(Post.user_id == user_id).count()
        
        # Count total comments received on posts
        total_comments = self.db.query(Comment).join(Post).filter(Post.user_id == user_id).count()
        
        return {
            "posts": posts_count,
            "followers": followers_count,
            "following": following_count,
            "total_likes": total_likes,
            "total_comments": total_comments
        }
    
    def get_user_posts(self, user_id: int, limit: int = 10) -> List[Post]:
        """Get user's posts with like and comment counts"""
        posts = self.db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).limit(limit).all()
        
        # Add like and comment counts to each post
        for post in posts:
            post.likes_count = self.db.query(PostLike).filter(PostLike.post_id == post.id).count()
            post.comments_count = self.db.query(Comment).filter(Comment.post_id == post.id).count()
        
        return posts
    
    def is_following(self, follower_id: int, followed_id: int) -> bool:
        """Check if user is following another user"""
        return self.db.query(UserFollow).filter(
            and_(UserFollow.follower_id == follower_id, UserFollow.followed_id == followed_id)
        ).first() is not None
    
    def follow_user(self, follower_id: int, followed_id: int) -> bool:
        """Follow a user"""
        # Check if already following
        existing_follow = self.db.query(UserFollow).filter(
            and_(UserFollow.follower_id == follower_id, UserFollow.followed_id == followed_id)
        ).first()
        
        if existing_follow:
            return False
        
        # Create new follow relationship
        new_follow = UserFollow(follower_id=follower_id, followed_id=followed_id)
        self.db.add(new_follow)
        self.db.commit()
        return True
    
    def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        """Unfollow a user"""
        follow = self.db.query(UserFollow).filter(
            and_(UserFollow.follower_id == follower_id, UserFollow.followed_id == followed_id)
        ).first()
        
        if not follow:
            return False
        
        self.db.delete(follow)
        self.db.commit()
        return True
    
    def get_followers(self, user_id: int) -> List[User]:
        """Get list of users following this user"""
        return self.db.query(User).join(UserFollow, User.id == UserFollow.follower_id).filter(
            UserFollow.followed_id == user_id
        ).all()
    
    def get_following(self, user_id: int) -> List[User]:
        """Get list of users this user is following"""
        return self.db.query(User).join(UserFollow, User.id == UserFollow.followed_id).filter(
            UserFollow.follower_id == user_id
        ).all()
    
    def update_profile(self, user_id: int, **kwargs) -> User:
        """Update user profile fields"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Update only provided fields
        for field, value in kwargs.items():
            if value is not None and hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def upload_avatar(self, avatar: UploadFile, username: str) -> str:
        """Upload and save user avatar"""
        # Create uploads directory if it doesn't exist
        upload_dir = "static/uploads/avatars"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(avatar.filename)[1]
        filename = f"{username}_{timestamp}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
        
        # Return the URL path
        return f"/static/uploads/avatars/{filename}"
    
    def search_users(self, query: str, current_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for users by username or full name"""
        users = self.db.query(User).filter(
            User.username.ilike(f"%{query}%") | User.full_name.ilike(f"%{query}%")
        ).limit(limit).all()
        
        results = []
        for user in users:
            if user.id != current_user_id:  # Don't show current user in search
                is_following = self.is_following(current_user_id, user.id)
                results.append({
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "is_following": is_following
                })
        
        return results 