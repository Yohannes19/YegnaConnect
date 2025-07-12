from sqlalchemy.orm import Session
from models.user import User
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str):
        hashed_password = AuthService.get_password_hash(password)
        user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
            return user, None
        except IntegrityError as e:
            db.rollback()
            if 'username' in str(e.orig):
                return None, "Username already exists."
            elif 'email' in str(e.orig):
                return None, "Email already exists."
            return None, "Registration failed."

    @staticmethod
    def authenticate_user(db: Session, username_or_email: str, password: str):
        user = db.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if not user:
            return None, "User not found."
        if not AuthService.verify_password(password, user.hashed_password):
            return None, "Incorrect password."
        return user, None 