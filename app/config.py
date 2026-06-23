import os

SECRET_KEY = os.getenv("SECRET_KEY", "hotel-reminder-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hotel_reminder.db")
