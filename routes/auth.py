from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
from sqlalchemy.orm import Session
from core.database import get_db
from services.auth_service import AuthService
from core.auth import create_access_token

router = APIRouter()
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
def login_post(request: Request, response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user, error = AuthService.authenticate_user(db, username, password)
    if error:
        return templates.TemplateResponse("login.html", {"request": request, "error": error, "username": username})
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/feed", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=3600)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register", response_class=HTMLResponse)
def register_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match.", "username": username, "email": email})
    user, error = AuthService.create_user(db, username, email, password)
    if error:
        return templates.TemplateResponse("register.html", {"request": request, "error": error, "username": username, "email": email})
    return RedirectResponse(url="/login", status_code=303)

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response 