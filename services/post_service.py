from sqlalchemy.orm import Session
from models.post import Post, PostLike, Comment, CommentLike
from models.user import User
from datetime import datetime, timezone

class PostService:
    @staticmethod
    def create_post(db: Session, content: str, user_id: int, category_id: int = None):
        post = Post(content=content, user_id=user_id, category_id=category_id)
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def get_posts_with_users(db: Session, current_user_id: int = None, limit: int = 50):
        posts = db.query(Post, User).join(User).order_by(Post.created_at.desc()).limit(limit).all()
        return [
            {
                "id": post.id,
                "content": post.content,
                "user": user.username,
                "time": PostService.format_time(post.created_at),
                "likes": post.likes_count,
                "comments": post.comments_count,
                "liked": PostService.has_liked_post(db, current_user_id, post.id) if current_user_id else False
            }
            for post, user in posts
        ]

    @staticmethod
    def format_time(created_at: datetime) -> str:
        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        diff = now - created_at
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"

    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int):
        post = db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()
        if post:
            db.delete(post)
            db.commit()
            return True
        return False

    @staticmethod
    def like_post(db: Session, user_id: int, post_id: int):
        # Check if already liked
        existing = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first()
        if existing:
            return False  # Already liked
        like = PostLike(user_id=user_id, post_id=post_id)
        db.add(like)
        # Increment likes_count
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            post.likes_count = (post.likes_count or 0) + 1
        db.commit()
        return True

    @staticmethod
    def unlike_post(db: Session, user_id: int, post_id: int):
        like = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first()
        if not like:
            return False  # Not liked
        db.delete(like)
        # Decrement likes_count
        post = db.query(Post).filter_by(id=post_id).first()
        if post and post.likes_count:
            post.likes_count = max(0, post.likes_count - 1)
        db.commit()
        return True

    @staticmethod
    def has_liked_post(db: Session, user_id: int, post_id: int) -> bool:
        return db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first() is not None

    @staticmethod
    def create_comment(db: Session, content: str, user_id: int, post_id: int):
        comment = Comment(content=content, user_id=user_id, post_id=post_id)
        db.add(comment)
        # Increment comments_count
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            post.comments_count = (post.comments_count or 0) + 1
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def get_comments_for_post(db: Session, post_id: int, current_user_id: int = None):
        comments = db.query(Comment, User).join(User).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()
        return [
            {
                "id": comment.id,
                "content": comment.content,
                "user": user.username,
                "time": PostService.format_time(comment.created_at),
                "user_id": comment.user_id,
                "likes": comment.likes_count,
                "liked": PostService.has_liked_comment(db, current_user_id, comment.id) if current_user_id else False
            }
            for comment, user in comments
        ]

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int):
        comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id).first()
        if comment:
            # Decrement comments_count
            post = db.query(Post).filter_by(id=comment.post_id).first()
            if post and post.comments_count:
                post.comments_count = max(0, post.comments_count - 1)
            db.delete(comment)
            db.commit()
            return True
        return False

    @staticmethod
    def like_comment(db: Session, user_id: int, comment_id: int):
        existing = db.query(CommentLike).filter_by(user_id=user_id, comment_id=comment_id).first()
        if existing:
            return False  # Already liked
        like = CommentLike(user_id=user_id, comment_id=comment_id)
        db.add(like)
        # Increment likes_count
        comment = db.query(Comment).filter_by(id=comment_id).first()
        if comment:
            comment.likes_count = (comment.likes_count or 0) + 1
        db.commit()
        return True

    @staticmethod
    def unlike_comment(db: Session, user_id: int, comment_id: int):
        like = db.query(CommentLike).filter_by(user_id=user_id, comment_id=comment_id).first()
        if not like:
            return False  # Not liked
        db.delete(like)
        # Decrement likes_count
        comment = db.query(Comment).filter_by(id=comment_id).first()
        if comment and comment.likes_count:
            comment.likes_count = max(0, comment.likes_count - 1)
        db.commit()
        return True

    @staticmethod
    def has_liked_comment(db: Session, user_id: int, comment_id: int) -> bool:
        return db.query(CommentLike).filter_by(user_id=user_id, comment_id=comment_id).first() is not None

    @staticmethod
    def create_reply(db: Session, content: str, user_id: int, post_id: int, parent_id: int):
        reply = Comment(content=content, user_id=user_id, post_id=post_id, parent_id=parent_id)
        db.add(reply)
        # Increment comments_count on the post
        post = db.query(Post).filter_by(id=post_id).first()
        if post:
            post.comments_count = (post.comments_count or 0) + 1
        db.commit()
        db.refresh(reply)
        return reply

    @staticmethod
    def get_replies_for_comment(db: Session, comment_id: int, current_user_id: int = None):
        replies = db.query(Comment, User).join(User).filter(Comment.parent_id == comment_id).order_by(Comment.created_at.asc()).all()
        return [
            {
                "id": reply.id,
                "content": reply.content,
                "user": user.username,
                "time": PostService.format_time(reply.created_at),
                "user_id": reply.user_id,
                "likes": reply.likes_count,
                "liked": PostService.has_liked_comment(db, current_user_id, reply.id) if current_user_id else False
            }
            for reply, user in replies
        ] 