from sqlalchemy.ext.declarative import declarative_base

# Create a single Base instance for all models
Base = declarative_base()

# Import all models to ensure they're registered with the Base metadata
from .user import User, UserFollow
from .post import Post, PostLike, Comment, CommentLike
from .category import Category, CategoryMember

# Make sure all models are imported so Alembic can detect them
__all__ = ['Base', 'User', 'UserFollow', 'Post', 'PostLike', 'Comment', 'CommentLike', 'Category', 'CategoryMember']



