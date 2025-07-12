from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Cookie

from core.database import get_db
from core.auth import verify_token
from models.user import User
from services.category_service import CategoryService

router = APIRouter(prefix="/category", tags=["category"])
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

# Category routes
@router.get("/", response_class=HTMLResponse)
async def categories_page(request: Request, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Browse all categories"""
    category_service = CategoryService(db)
    categories = category_service.get_all_categories(current_user_obj.id if current_user_obj else None)
    
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "current_user": current_user_obj,
        "categories": categories
    })

@router.get("/create", response_class=HTMLResponse)
async def create_category_page(request: Request, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj)):
    """Show category creation page"""
    if not current_user_obj:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("create_category.html", {
        "request": request,
        "current_user": current_user_obj
    })

@router.post("/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    display_name: str = Form(...),
    description: str = Form(None),
    rules: str = Form(None),
    is_public: bool = Form(True),
    is_nsfw: bool = Form(False),
    current_user: str = Depends(get_current_user),
    current_user_obj: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Create a new category"""
    if not current_user_obj:
        return RedirectResponse(url="/login", status_code=302)
    
    category_service = CategoryService(db)
    
    try:
        category = category_service.create_category(
            name=name,
            display_name=display_name,
            description=description or "",
            rules=rules or "",
            is_public=is_public,
            is_nsfw=is_nsfw,
            created_by=current_user_obj.id
        )
        return RedirectResponse(url=f"/category/{category.name}", status_code=302)
    except ValueError as e:
        return templates.TemplateResponse("create_category.html", {
            "request": request,
            "current_user": current_user_obj,
            "error": str(e),
            "name": name,
            "display_name": display_name,
            "description": description,
            "rules": rules,
            "is_public": is_public,
            "is_nsfw": is_nsfw
        })

@router.get("/{category_name}", response_class=HTMLResponse)
async def view_category(request: Request, category_name: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """View a category page"""
    category_service = CategoryService(db)
    
    category = category_service.get_category_by_name(category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if user can access this category
    if not category.is_public and not category_service.is_member(current_user_obj.id if current_user_obj else None, category.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get category stats and posts
    stats = category_service.get_category_stats(category.id)
    posts = category_service.get_category_posts(category.id)
    
    # Check if user is member
    is_member = False
    user_role = None
    if current_user_obj:
        is_member = category_service.is_member(current_user_obj.id, category.id)
        user_role = category_service.get_user_role(current_user_obj.id, category.id)
    
    return templates.TemplateResponse("category.html", {
        "request": request,
        "current_user": current_user_obj,
        "category": category,
        "stats": stats,
        "posts": posts,
        "is_member": is_member,
        "user_role": user_role
    })

@router.post("/{category_name}/join")
async def join_category(request: Request, category_name: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Join a category"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    category_service = CategoryService(db)
    category = category_service.get_category_by_name(category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    success = category_service.join_category(current_user_obj.id, category.id)
    if not success:
        raise HTTPException(status_code=400, detail="Already a member or cannot join")
    
    return {"message": "Successfully joined category"}

@router.post("/{category_name}/leave")
async def leave_category(request: Request, category_name: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Leave a category"""
    if not current_user_obj:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    category_service = CategoryService(db)
    category = category_service.get_category_by_name(category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    success = category_service.leave_category(current_user_obj.id, category.id)
    if not success:
        raise HTTPException(status_code=400, detail="Not a member or cannot leave")
    
    return {"message": "Successfully left category"}

@router.get("/{category_name}/members", response_class=HTMLResponse)
async def view_category_members(request: Request, category_name: str, current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """View category members"""
    category_service = CategoryService(db)
    
    category = category_service.get_category_by_name(category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if user can access this category
    if not category.is_public and not category_service.is_member(current_user_obj.id if current_user_obj else None, category.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = category_service.get_category_members(category.id)
    
    return templates.TemplateResponse("category_members.html", {
        "request": request,
        "current_user": current_user_obj,
        "category": category,
        "members": members
    })

# Search categories
@router.get("/search", response_class=HTMLResponse)
async def search_categories(request: Request, q: Optional[str] = Query(None), current_user: str = Depends(get_current_user), current_user_obj: User = Depends(get_current_user_obj), db: Session = Depends(get_db)):
    """Search categories"""
    category_service = CategoryService(db)
    
    results = []
    if q:
        results = category_service.search_categories(q, current_user_obj.id if current_user_obj else None)
    
    return templates.TemplateResponse("search_categories.html", {
        "request": request,
        "current_user": current_user_obj,
        "query": q,
        "results": results
    }) 