from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
import re

from models.category import Category, CategoryMember
from models.user import User
from models.post import Post, PostLike, Comment

class CategoryService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_category(self, name: str, display_name: str, description: str, rules: str, 
                       is_public: bool, is_nsfw: bool, created_by: int) -> Optional[Category]:
        """Create a new category/group"""
        # Validate category name (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', name):
            raise ValueError("Category name can only contain letters, numbers, and underscores")
        
        # Check if category name already exists
        existing = self.db.query(Category).filter(Category.name == name).first()
        if existing:
            raise ValueError("Category name already exists")
        
        # Create category
        category = Category(
            name=name,
            display_name=display_name,
            description=description,
            rules=rules,
            is_public=is_public,
            is_nsfw=is_nsfw,
            created_by=created_by
        )
        
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        
        # Add creator as admin
        member = CategoryMember(
            user_id=created_by,
            category_id=category.id,
            role="admin"
        )
        self.db.add(member)
        self.db.commit()
        
        return category
    
    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        return self.db.query(Category).filter(Category.name == name).first()
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_all_categories(self, user_id: Optional[int] = None) -> List[Category]:
        """Get all public categories"""
        query = self.db.query(Category).filter(Category.is_public == True)
        
        if user_id:
            # Also include private categories where user is a member
            member_categories = self.db.query(CategoryMember.category_id).filter(
                CategoryMember.user_id == user_id
            ).subquery()
            
            query = query.filter(
                or_(
                    Category.is_public == True,
                    Category.id.in_(member_categories)
                )
            )
        
        return query.order_by(Category.display_name).all()
    
    def get_user_categories(self, user_id: int) -> List[Category]:
        """Get categories where user is a member"""
        return self.db.query(Category).join(CategoryMember).filter(
            CategoryMember.user_id == user_id
        ).order_by(Category.display_name).all()
    
    def join_category(self, user_id: int, category_id: int) -> bool:
        """Join a category"""
        # Check if already a member
        existing = self.db.query(CategoryMember).filter(
            and_(CategoryMember.user_id == user_id, CategoryMember.category_id == category_id)
        ).first()
        
        if existing:
            return False
        
        # Check if category exists and is public
        category = self.get_category_by_id(category_id)
        if not category or not category.is_public:
            return False
        
        # Add member
        member = CategoryMember(user_id=user_id, category_id=category_id)
        self.db.add(member)
        self.db.commit()
        return True
    
    def leave_category(self, user_id: int, category_id: int) -> bool:
        """Leave a category"""
        member = self.db.query(CategoryMember).filter(
            and_(CategoryMember.user_id == user_id, CategoryMember.category_id == category_id)
        ).first()
        
        if not member:
            return False
        
        # Don't allow admin to leave (they need to transfer ownership first)
        if member.role == "admin":
            return False
        
        self.db.delete(member)
        self.db.commit()
        return True
    
    def get_category_members(self, category_id: int) -> List[Dict[str, Any]]:
        """Get all members of a category"""
        members = self.db.query(CategoryMember, User).join(User).filter(
            CategoryMember.category_id == category_id
        ).order_by(CategoryMember.role.desc(), CategoryMember.joined_at).all()
        
        return [
            {
                "id": member.CategoryMember.id,
                "user_id": member.User.id,
                "username": member.User.username,
                "full_name": member.User.full_name,
                "avatar_url": member.User.avatar_url,
                "role": member.CategoryMember.role,
                "joined_at": member.CategoryMember.joined_at
            }
            for member in members
        ]
    
    def get_category_stats(self, category_id: int) -> Dict[str, Any]:
        """Get category statistics"""
        posts_count = self.db.query(Post).filter(Post.category_id == category_id).count()
        members_count = self.db.query(CategoryMember).filter(CategoryMember.category_id == category_id).count()
        
        return {
            "posts": posts_count,
            "members": members_count
        }
    
    def is_member(self, user_id: int, category_id: int) -> bool:
        """Check if user is a member of category"""
        return self.db.query(CategoryMember).filter(
            and_(CategoryMember.user_id == user_id, CategoryMember.category_id == category_id)
        ).first() is not None
    
    def get_user_role(self, user_id: int, category_id: int) -> Optional[str]:
        """Get user's role in category"""
        member = self.db.query(CategoryMember).filter(
            and_(CategoryMember.user_id == user_id, CategoryMember.category_id == category_id)
        ).first()
        return member.role if member else None
    
    def can_post_in_category(self, user_id: int, category_id: int) -> bool:
        """Check if user can post in category"""
        if not self.is_member(user_id, category_id):
            return False
        
        # Check if category is public or user is member
        category = self.get_category_by_id(category_id)
        if not category:
            return False
        
        return category.is_public or self.is_member(user_id, category_id)
    
    def get_category_posts(self, category_id: int, limit: int = 20) -> List[Post]:
        """Get posts from a category"""
        posts = self.db.query(Post).filter(Post.category_id == category_id).order_by(
            Post.created_at.desc()
        ).limit(limit).all()
        
        # Add like and comment counts
        for post in posts:
            post.likes_count = self.db.query(PostLike).filter(PostLike.post_id == post.id).count()
            post.comments_count = self.db.query(Comment).filter(Comment.post_id == post.id).count()
        
        return posts
    
    def search_categories(self, query: str, user_id: Optional[int] = None) -> List[Category]:
        """Search categories by name or description"""
        search_query = self.db.query(Category).filter(
            and_(
                Category.is_public == True,
                or_(
                    Category.name.ilike(f"%{query}%"),
                    Category.display_name.ilike(f"%{query}%"),
                    Category.description.ilike(f"%{query}%")
                )
            )
        )
        
        if user_id:
            # Also include private categories where user is a member
            member_categories = self.db.query(CategoryMember.category_id).filter(
                CategoryMember.user_id == user_id
            ).subquery()
            
            search_query = search_query.filter(
                or_(
                    Category.is_public == True,
                    Category.id.in_(member_categories)
                )
            )
        
        return search_query.order_by(Category.display_name).all() 