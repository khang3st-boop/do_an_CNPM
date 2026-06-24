# Hotel Reminder System

Website hỗ trợ quản lý thông báo và nhắc lịch trong khách sạn.

## Công nghệ
- Python 3.10+, Flask, SQLAlchemy, APScheduler
- SQL Server, pyodbc
- Bootstrap 5

## Cài đặt

### 1. Chuẩn bị môi trường
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 2. Cấu hình Database
- Mở SQL Server Management Studio (SSMS)
- Chạy file `database/setup.sql` để tạo database và bảng

### 3. Cấu hình file .env
Có thể copy `.env.example` thành `.env`, rồi sửa lại theo SQL Server của bạn.

**Windows Authentication** (thường dùng khi `DB_USER` để trống):
```
DB_SERVER=.\SQLSERVER
DB_NAME=HotelReminderDB
DB_TRUSTED_CONNECTION=yes
DB_USER=
DB_PASSWORD=
SECRET_KEY=khóa_bí_mật_bất_kỳ
```

**SQL Server Authentication**:
```
DB_SERVER=localhost
DB_NAME=HotelReminderDB
DB_TRUSTED_CONNECTION=no
DB_USER=sa
DB_PASSWORD=mật_khẩu_của_bạn
SECRET_KEY=khóa_bí_mật_bất_kỳ
```

Nếu máy bạn dùng ODBC Driver 18 thì đổi thêm:
```
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes
```

### 4. Chạy ứng dụng
```bash
python app.py
```

Truy cập: http://127.0.0.1:5000

**Tài khoản mặc định:** `admin` / `admin123`

## Cấu trúc thư mục
```
HotelReminderSystem/
├── app.py                     # Điểm khởi động chính
├── .env                       # Cấu hình (không commit)
├── requirements.txt
├── controllers/               # Route handler
│   ├── auth_controller.py     # Login, Logout
│   └── reminder_controller.py # CRUD Reminder
├── services/                  # Logic nghiệp vụ
│   ├── auth_service.py
│   └── reminder_service.py
├── repositories/              # Truy vấn database
│   ├── user_repository.py
│   ├── reminder_repository.py
│   └── notification_repository.py
├── models/                    # SQLAlchemy models
│   ├── user.py
│   ├── reminder.py
│   └── notification.py
├── database/
│   ├── connection.py          # Kết nối SQL Server
│   └── setup.sql              # Script tạo bảng
├── scheduler/
│   └── reminder_scheduler.py  # APScheduler — nhắc lịch tự động
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── reminders/
│       ├── list.html
│       └── form.html
└── static/
    └── css/style.css
```

## Tính năng
- Đăng nhập / Đăng xuất an toàn (password hash)
- CRUD lịch nhắc (Thêm / Xem / Sửa / Xóa)
- Dashboard hiển thị lịch sắp tới
- APScheduler tự động kiểm tra và thông báo mỗi 1 phút


## Các lỗi đã được vá trong bản này
- Bổ sung đầy đủ template cho Khách hàng, Đặt phòng, Dọn phòng, Thông báo và Báo cáo.
- Sửa `database/setup.sql` để tạo bảng đúng thứ tự và có thể chạy lại nhiều lần.
- Sửa chuỗi kết nối SQL Server để password có ký tự đặc biệt không làm lỗi kết nối.
- Hỗ trợ tự dùng Windows Authentication khi `DB_USER` để trống.
- Sửa lỗi lazy-load SQLAlchemy sau khi đóng session ở các trang booking/notification/housekeeping/report.
- Bổ sung kiểm tra dữ liệu form để tránh lỗi khi submit thiếu phòng, khách hoặc tổng tiền sai định dạng.
