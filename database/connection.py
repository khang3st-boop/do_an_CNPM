import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_NAME = os.getenv("DB_NAME", "HotelReminderDB")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUST_CERT = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
DB_TRUSTED_CONNECTION = (
    os.getenv("DB_TRUSTED_CONNECTION", "no").lower() in ("1", "true", "yes")
    or not DB_USER.strip()
)

# Dùng URL.create để password có ký tự đặc biệt (@, #, %, khoảng trắng...) không làm hỏng chuỗi kết nối.
query = {
    "driver": DB_DRIVER,
    "TrustServerCertificate": DB_TRUST_CERT,
}
if DB_TRUSTED_CONNECTION:
    query["Trusted_Connection"] = "yes"
    DB_USER = None
    DB_PASSWORD = None

CONNECTION_STRING = URL.create(
    "mssql+pyodbc",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_SERVER,
    database=DB_NAME,
    query=query,
)

engine = create_engine(CONNECTION_STRING, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    """Trả về session DB, dùng trong controller."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[DB] Kết nối SQL Server thành công!")
        return True
    except Exception as e:
        print(f"[DB] Lỗi kết nối: {e}")
        return False
