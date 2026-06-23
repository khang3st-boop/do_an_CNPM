# Website hỗ trợ quản lý thông báo và nhắc lịch trong khách sạn

## 1. Giới thiệu đề tài

Đây là backend API cho đồ án môn **Công nghệ phần mềm**, đề tài:

**Xây dựng website hỗ trợ quản lý thông báo và nhắc lịch trong khách sạn theo mô hình Agile Scrum**

Hệ thống hỗ trợ các chức năng quản lý tài khoản nhân viên, quản lý phòng, gửi thông báo nội bộ, tạo lịch nhắc check-in/check-out và theo dõi công việc trong khách sạn.

Project gồm **backend API** (FastAPI) và **giao diện web** (Jinja2 + HTML/CSS/JS), kiểm thử qua trình duyệt, Swagger UI và Postman.

---

## 2. Công nghệ sử dụng

* Python
* FastAPI
* Jinja2
* SQLite
* SQLAlchemy
* JWT Authentication
* Swagger UI
* Postman
* Git/GitHub
* Jira Scrum

---

## 3. Cấu trúc thư mục

```txt
do_an_CNPM/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── rooms.py
│   │   ├── notifications.py
│   │   ├── reminders.py
│   │   └── web.py
│   ├── static/
│   │   ├── css/main.css
│   │   └── js/
│   ├── templates/
│   │   ├── login.html
│   │   ├── users.html
│   │   └── guests.html
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── main.py
├── requirements.txt
├── .env.example
├── README.md
└── .gitignore
```

---

## 4. Chức năng chính

### 4.1. Xác thực người dùng

* Đăng nhập hệ thống
* Tạo JWT token sau khi đăng nhập thành công
* Lấy thông tin người dùng hiện tại bằng token

### 4.2. Quản lý tài khoản nhân viên

* Xem danh sách tài khoản nhân viên
* Tạo tài khoản nhân viên
* Khóa hoặc mở khóa tài khoản nhân viên
* Phân quyền theo vai trò: admin, manager, receptionist, housekeeping, technician, staff

### 4.3. Quản lý phòng khách sạn

* Xem danh sách phòng
* Tạo phòng mới
* Cập nhật trạng thái phòng
* Vô hiệu hóa phòng

### 4.4. Quản lý thông báo

* Tạo thông báo nội bộ
* Gửi thông báo theo bộ phận hoặc người nhận
* Xem danh sách thông báo
* Xem thông báo của người dùng đang đăng nhập
* Xác nhận đã đọc thông báo

### 4.5. Quản lý nhắc lịch

* Tạo lịch nhắc check-in/check-out
* Xem danh sách lịch nhắc
* Xem lịch nhắc được giao cho người dùng hiện tại
* Cập nhật trạng thái lịch nhắc
* Xem danh sách lịch nhắc quá hạn

### 4.6. Giao diện web (Python FastAPI + Jinja2)

| Mã Jira | Màn hình | URL |
| ------- | -------- | --- |
| N1-69 | Đăng nhập | http://127.0.0.1:8000/ui/login |
| N1-166 | Phân quyền tài khoản | http://127.0.0.1:8000/ui/users |
| N1-165 | Thông tin khách hàng | http://127.0.0.1:8000/ui/guests |

---

## 5. Cài đặt project

### Bước 1: Clone project

```bash
git clone https://github.com/khang3st-boop/do_an_CNPM.git
cd do_an_CNPM
```

### Bước 2: Tạo môi trường ảo

```bash
python -m venv venv
```

### Bước 3: Kích hoạt môi trường ảo trên Windows

```bash
venv\Scripts\activate
```

### Bước 4: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 5 (tùy chọn): Cấu hình môi trường

```bash
copy .env.example .env
```

---

## 6. Chạy project

Chạy server bằng lệnh:

```bash
uvicorn main:app --reload
```

Sau khi chạy thành công, mở trình duyệt:

```txt
http://127.0.0.1:8000/ui/login
```

Hoặc Swagger API docs:

```txt
http://127.0.0.1:8000/docs
```

---

## 7. Tài khoản demo

| Email | Password | Role | Mô tả |
| ----- | -------- | ---- | ----- |
| admin@hotel.com | 123456 | admin | Quản trị hệ thống |
| reception@hotel.com | 123456 | receptionist | Lễ tân - tạo/xem lịch nhắc |
| housekeeping@hotel.com | 123456 | housekeeping | Buồng phòng - xem thông báo được giao |

---

## 8. Cách test API

### Bước 1: Đăng nhập

API:

```txt
POST /api/auth/login
```

Body:

```json
{
  "email": "admin@hotel.com",
  "password": "123456"
}
```

Sau khi đăng nhập thành công, hệ thống trả về `token`.

### Bước 2: Gắn token vào Swagger

Bấm nút **Authorize** trên Swagger UI và nhập token (chỉ token, không cần thêm chữ `Bearer`):

```txt
<token>
```

Sau đó có thể test các API cần đăng nhập.

---

## 9. Danh sách API chính

### Auth API

```txt
POST /api/auth/login
GET /api/auth/me
```

### User API

```txt
GET /api/users
POST /api/users
PATCH /api/users/{user_id}/toggle-status
```

### Room API

```txt
GET /api/rooms
POST /api/rooms
PATCH /api/rooms/{room_id}/status
PATCH /api/rooms/{room_id}/deactivate
```

### Notification API

```txt
POST /api/notifications
GET /api/notifications
GET /api/notifications/my
GET /api/notifications/{notification_id}
PATCH /api/notifications/{notification_id}/read
PATCH /api/notifications/{notification_id}/deactivate
```

### Reminder API

```txt
POST /api/reminders
GET /api/reminders
GET /api/reminders/my
PATCH /api/reminders/{reminder_id}/status
GET /api/reminders/overdue
```

---

## 10. Mapping Jira Task với chức năng

| Mã Jira | Chức năng                   | API / File liên quan                                                              |
| ------- | --------------------------- | --------------------------------------------------------------------------------- |
| N1-68   | API xác thực đăng nhập      | `POST /api/auth/login`, `app/routers/auth.py`                                     |
| N1-42   | API danh sách tài khoản     | `GET /api/users`, `app/routers/users.py`                                          |
| N1-43   | API tạo tài khoản nhân viên | `POST /api/users`, `app/routers/users.py`                                         |
| N1-44   | API khóa/mở khóa tài khoản  | `PATCH /api/users/{user_id}/toggle-status`, `app/routers/users.py`                |
| N1-55   | API danh sách phòng         | `GET /api/rooms`, `app/routers/rooms.py`                                          |
| N1-56   | API tạo phòng mới           | `POST /api/rooms`, `app/routers/rooms.py`                                         |
| N1-57   | API vô hiệu hóa phòng       | `PATCH /api/rooms/{room_id}/deactivate`, `app/routers/rooms.py`                   |
| N1-16   | Tạo thông báo nội bộ        | `POST /api/notifications`, `app/routers/notifications.py`                         |
| N1-17   | Gửi thông báo theo bộ phận  | `POST /api/notifications`, `app/routers/notifications.py`                         |
| N1-18   | Xem thông báo của tôi       | `GET /api/notifications/my`, `app/routers/notifications.py`                       |
| N1-19   | Xác nhận đã đọc thông báo   | `PATCH /api/notifications/{notification_id}/read`, `app/routers/notifications.py` |
| N1-22   | Tạo lịch nhắc check-in      | `POST /api/reminders`, `app/routers/reminders.py`                                 |
| N1-23   | Tạo lịch nhắc check-out     | `POST /api/reminders`, `app/routers/reminders.py`                                 |
| N1-69   | Giao diện đăng nhập         | `/ui/login`, `app/templates/login.html`                                           |
| N1-166  | Giao diện phân quyền        | `/ui/users`, `app/templates/users.html`                                           |
| N1-165  | Giao diện khách hàng        | `/ui/guests`, `app/templates/guests.html`                                         |

---

## 11. Ghi chú

* Project hiện tại sử dụng SQLite để thuận tiện cho quá trình demo và kiểm thử.
* File database local `hotel_reminder.db` không được đưa lên GitHub.
* Thư mục `venv/` không được đưa lên GitHub.
* Backend có thể kiểm thử trực tiếp bằng Swagger UI tại `/docs`.
* API health check: `GET /api/health`
* Giao diện web: `/ui/login`, `/ui/users`, `/ui/guests`
* Lễ tân (`receptionist`) có thể xem danh sách phòng và quản lý lịch nhắc.
* Giao diện người dùng có thể được phát triển ở giai đoạn sau.
t e s t  
 