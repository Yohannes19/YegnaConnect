from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="user")
    liked_posts = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    liked_comments = relationship("CommentLike", back_populates="user", cascade="all, delete-orphan")
    
    # Follow relationships
    followers = relationship("UserFollow", foreign_keys="UserFollow.followed_id", back_populates="followed", cascade="all, delete-orphan")
    following = relationship("UserFollow", foreign_keys="UserFollow.follower_id", back_populates="follower", cascade="all, delete-orphan")
    
    # Category relationships
    created_categories = relationship("Category", back_populates="creator", cascade="all, delete-orphan")
    category_memberships = relationship("CategoryMember", back_populates="user", cascade="all, delete-orphan")

class UserFollow(Base):
    __tablename__ = "user_follows"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers") 