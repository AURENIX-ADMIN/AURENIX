from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.auth_service import authenticate_user, create_access_token
from src.api.middleware.auth import get_current_user
from src.models.user import User
from config.settings import get_settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")
settings = get_settings()

COOKIE_NAME = "orbit_session"
COOKIE_MAX_AGE = settings.jwt_expire_hours * 3600


class LoginForm(BaseModel):
    email: str
    password: str


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    form = await request.form()
    email = form.get("email", "")
    password = form.get("password", "")

    user = await authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Email o contraseña incorrectos"},
            status_code=401,
        )

    token = create_access_token(str(user.id), user.email)

    resp = templates.TemplateResponse("login.html", {"request": request})
    resp = Response(status_code=302, headers={"Location": "/"})
    resp.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        max_age=COOKIE_MAX_AGE,
    )
    return resp


@router.post("/logout")
async def logout():
    response = Response(status_code=302, headers={"Location": "/login"})
    response.delete_cookie(key=COOKIE_NAME)
    return response


@router.get("/auth/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email, "name": current_user.name}
