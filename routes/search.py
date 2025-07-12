from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from fastapi import Cookie
from core.auth import verify_token
from models.user import User
from services.profile_service import ProfileService

router = APIRouter(prefix="/search", tags=["search"])
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

@router.get("/", response_class=HTMLResponse)
async def search_page(request: Request, q: Optional[str] = Query(None), current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Search page with results"""
    profile_service = ProfileService(db)
    
    results = []
    if q and current_user_obj:
        results = profile_service.search_users(q, current_user_obj.id)
    
    return templates.TemplateResponse("search.html", {
        "request": request,
        "current_user": current_user_obj,
        "query": q,
        "results": results
    }) 