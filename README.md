# Hệ thống quản lý nhắc lịch khách sạn

**Hotel Reminder Management System** là website hỗ trợ khách sạn quản lý tài khoản nhân viên, phòng, khách lưu trú, thông báo nội bộ và lịch nhắc các công việc như check-in/check-out.

Source này sử dụng **Flask** làm framework chính, phù hợp để demo và nộp đồ án môn **Công nghệ Phần mềm**.

## Công nghệ sử dụng

- Python
- Flask
- HTML/CSS/JavaScript
- SQLite
- SQLAlchemy
- Passlib/Bcrypt để hash mật khẩu

## Chức năng chính

- Đăng nhập, đăng xuất.
- Dashboard tổng quan số lượng tài khoản, phòng, khách lưu trú, nhắc lịch và thông báo.
- Quản lý tài khoản nhân viên.
- Quản lý phòng khách sạn.
- Quản lý khách lưu trú.
- Quản lý lịch nhắc.
- Quản lý thông báo nội bộ.

## Cài đặt

```bash
git clone <link-repository>
cd code
python -m venv venv
```

Kích hoạt môi trường ảo trên Windows:

```bash
venv\Scripts\activate
```

Cài đặt thư viện:

```bash
pip install -r requirements.txt
```

## Chạy dự án

```bash
python app.py
```

Sau khi chạy, mở trình duyệt:

```txt
http://127.0.0.1:5000
```

## Tài khoản demo

```txt
Email: admin@hotel.com
Mật khẩu: 123456
Vai trò: admin
```

## Cấu trúc thư mục

```txt
hotel-reminder-management-system/
├── app.py
├── controllers/
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── user_controller.py
│   ├── room_controller.py
│   ├── guest_controller.py
│   ├── reminder_controller.py
│   └── notification_controller.py
├── services/
│   ├── auth_service.py
│   ├── dashboard_service.py
│   └── seed_service.py
├── repositories/
│   ├── user_repository.py
│   ├── room_repository.py
│   ├── guest_repository.py
│   ├── reminder_repository.py
│   └── notification_repository.py
├── models/
│   ├── user.py
│   ├── room.py
│   ├── guest.py
│   ├── reminder.py
│   └── notification.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── users.html
│   ├── rooms.html
│   ├── guests.html
│   ├── reminders.html
│   └── notifications.html
├── static/
│   ├── css/styles.css
│   └── js/main.js
├── database/
│   └── connection.py
├── scheduler/
│   └── reminder_scheduler.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Route/trang chính

```txt
GET  /                 Chuyển đến đăng nhập hoặc dashboard
GET  /login            Trang đăng nhập
POST /login            Xử lý đăng nhập
GET  /logout           Đăng xuất
GET  /dashboard        Trang tổng quan
GET  /users            Danh sách tài khoản
POST /users            Tạo tài khoản
POST /users/<id>/toggle-status
GET  /rooms            Danh sách phòng
POST /rooms            Tạo phòng
POST /rooms/<id>/deactivate
GET  /guests           Danh sách khách lưu trú
POST /guests           Tạo khách lưu trú
POST /guests/<id>/toggle-status
GET  /reminders        Danh sách lịch nhắc
POST /reminders        Tạo lịch nhắc
POST /reminders/<id>/status
GET  /notifications    Danh sách thông báo
POST /notifications    Tạo thông báo
POST /notifications/<id>/read
```

## Ghi chú

- File database runtime `*.db`, `*.sqlite`, `*.sqlite3` không đưa lên GitHub.
- Thư mục `venv/`, `__pycache__/`, `.env`, file tạm IDE không đưa lên GitHub.
- Khi chạy lần đầu, hệ thống tự tạo database SQLite và tài khoản demo.
