from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rules = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)
    is_nsfw = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_categories")
    posts = relationship("Post", back_populates="category")
    members = relationship("CategoryMember", back_populates="category")

class CategoryMember(Base):
    __tablename__ = "category_members"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    role = Column(String(20), default="member")  # member, moderator, admin
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="category_memberships")
    category = relationship("Category", back_populates="members") 