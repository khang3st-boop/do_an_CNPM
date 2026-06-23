from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Notification, NotificationRecipient, Reminder, Room, User
from app.routers import auth, notifications, reminders, rooms, users, web
from app.utils import api_response

DEMO_USERS = [
    {
        "name": "Admin Hotel",
        "email": "admin@hotel.com",
        "password": "123456",
        "role": "admin",
        "department": "management",
        "phone": "0900000000",
    },
    {
        "name": "Le Tan A",
        "email": "reception@hotel.com",
        "password": "123456",
        "role": "receptionist",
        "department": "reception",
        "phone": "0900000001",
    },
    {
        "name": "Buong Phong B",
        "email": "housekeeping@hotel.com",
        "password": "123456",
        "role": "housekeeping",
        "department": "housekeeping",
        "phone": "0900000002",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    create_default_data()
    yield


app = FastAPI(
    title="Hotel Reminder API",
    description="Backend API cho website quản lý thông báo và nhắc lịch khách sạn",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0]["msg"] if errors else "Dữ liệu không hợp lệ"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": first_error,
            "data": jsonable_encoder(errors),
        },
    )


@app.get("/", tags=["health"], include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/login")


@app.get("/api/health", tags=["health"])
def health_check():
    return api_response(
        "Hotel Reminder API đang hoạt động",
        {
            "service": "Hotel Reminder API",
            "version": "1.0.0",
            "docs": "/docs",
            "ui": "/ui/login",
        },
    )

def create_default_data():
    db = SessionLocal()

    try:
        admin = None

        for demo_user in DEMO_USERS:
            user = db.query(User).filter(User.email == demo_user["email"]).first()
            if not user:
                user = User(
                    name=demo_user["name"],
                    email=demo_user["email"],
                    password=hash_password(demo_user["password"]),
                    role=demo_user["role"],
                    department=demo_user["department"],
                    phone=demo_user["phone"],
                    status="active",
                )
                db.add(user)
            if demo_user["role"] == "admin":
                admin = user

        db.flush()

        if admin is None:
            admin = db.query(User).filter(User.email == "admin@hotel.com").first()

        room_101 = db.query(Room).filter(Room.room_number == "101").first()

        if not room_101:
            db.add_all([
                Room(
                    room_number="101",
                    floor=1,
                    room_type="Standard",
                    capacity=2,
                    price_per_night=500000,
                    status="available",
                    note="Phòng tiêu chuẩn",
                ),
                Room(
                    room_number="203",
                    floor=2,
                    room_type="Deluxe",
                    capacity=2,
                    price_per_night=850000,
                    status="available",
                    note="Phòng hướng thành phố",
                ),
                Room(
                    room_number="305",
                    floor=3,
                    room_type="Family",
                    capacity=4,
                    price_per_night=1200000,
                    status="maintenance",
                    note="Đang bảo trì điều hòa",
                ),
            ])

        db.flush()

        room_101 = db.query(Room).filter(Room.room_number == "101").first()
        sample_notification = db.query(Notification).first()

        if not sample_notification and admin:
            notification = Notification(
                title="Thông báo họp giao ban",
                content="Họp giao ban tại quầy lễ tân lúc 08:00.",
                type="general",
                department="management",
                status="active",
                created_by=admin.id,
            )
            db.add(notification)
            db.flush()
            db.add(NotificationRecipient(
                notification_id=notification.id,
                user_id=admin.id,
                status="unread",
            ))

        sample_reminder = db.query(Reminder).first()
        receptionist = db.query(User).filter(User.email == "reception@hotel.com").first()

        if not sample_reminder and room_101 and receptionist:
            db.add(Reminder(
                title="Nhắc check-in phòng 101",
                content="Chuẩn bị hồ sơ check-in cho khách mẫu.",
                room_id=room_101.id,
                guest_name="Khách Mẫu",
                reminder_type="check-in",
                reminder_time=datetime.utcnow() + timedelta(hours=2),
                assigned_user_id=receptionist.id,
                status="pending",
                created_by=admin.id if admin else receptionist.id,
            ))

        db.commit()

    finally:
        db.close()


app.include_router(web.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(notifications.router)
app.include_router(reminders.router)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")