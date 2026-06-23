from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/ui", tags=["web"])

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "page_title": "Đăng nhập"},
    )


@router.get("/users")
def users_page(request: Request):
    return templates.TemplateResponse(
        "users.html",
        {"request": request, "page_title": "Phân quyền tài khoản"},
    )


@router.get("/guests")
def guests_page(request: Request):
    return templates.TemplateResponse(
        "guests.html",
        {"request": request, "page_title": "Thông tin khách hàng"},
    )
