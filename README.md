# Hotel Reminder System

Hotel Reminder System là ứng dụng web hỗ trợ quản lý vận hành khách sạn, tập trung vào nhắc lịch, thông báo, đặt phòng, khách hàng, phòng, công việc buồng phòng và báo cáo tổng quan.

Dự án được xây dựng bằng Flask theo kiến trúc nhiều lớp gồm `controllers`, `services`, `repositories`, `models`, sử dụng SQL Server làm cơ sở dữ liệu và APScheduler để tự động kiểm tra lịch nhắc.

## Mục lục

- [Tính năng](#tính-năng)
- [Công nghệ sử dụng](#công-nghệ-sử-dụng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cấu hình môi trường](#cấu-hình-môi-trường)
- [Khởi tạo cơ sở dữ liệu](#khởi-tạo-cơ-sở-dữ-liệu)
- [Chạy ứng dụng](#chạy-ứng-dụng)
- [Tài khoản mẫu](#tài-khoản-mẫu)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Các route chính](#các-route-chính)
- [API JSON](#api-json)
- [Ghi chú phát triển](#ghi-chú-phát-triển)
- [Xử lý lỗi thường gặp](#xử-lý-lỗi-thường-gặp)

## Tính năng

- Đăng nhập, đăng xuất bằng Flask session.
- Quản lý tài khoản nhân viên theo vai trò và phòng ban.
- Quản lý phòng: thêm, sửa, xóa, lọc theo trạng thái.
- Quản lý khách hàng và thông tin liên hệ.
- Quản lý đặt phòng, trạng thái đặt phòng và tổng tiền.
- Quản lý lịch nhắc gắn với người dùng hoặc đặt phòng.
- Tự động kiểm tra lịch nhắc mỗi 1 phút bằng APScheduler.
- Quản lý thông báo nội bộ giữa nhân viên, người dùng hoặc phòng ban.
- Quản lý thông báo gửi cho khách theo booking.
- Quản lý công việc buồng phòng và lịch bảo trì phòng.
- Báo cáo tổng quan về phòng, khách, booking, công việc, thông báo và lịch nhắc.
- Cung cấp giao diện server-rendered bằng Jinja2 và một giao diện React nhúng tại `/ui`.
- Cung cấp JSON API cho một số màn hình React.

## Công nghệ sử dụng

- Python 3.10+
- Flask 3
- SQLAlchemy 2
- SQL Server
- pyodbc
- APScheduler
- python-dotenv
- Werkzeug password hashing
- Jinja2 templates
- Bootstrap/CSS tĩnh
- React 18 CDN cho giao diện nhúng tại `/ui`

## Yêu cầu hệ thống

Trước khi chạy dự án, cần cài đặt:

- Python 3.10 trở lên
- SQL Server hoặc SQL Server Express
- SQL Server Management Studio (khuyến nghị)
- ODBC Driver 17 hoặc 18 for SQL Server
- Git (nếu clone source từ repository)

## Cài đặt

Tại thư mục gốc của project, tạo virtual environment và cài dependency:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Nếu dùng macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Cấu hình môi trường

Copy file `.env.example` thành `.env`:

```powershell
Copy-Item .env.example .env
```

Sau đó chỉnh lại thông tin SQL Server trong `.env`.

### Windows Authentication

Dùng khi đăng nhập SQL Server bằng tài khoản Windows:

```env
DB_SERVER=.\SQLSERVER
DB_NAME=HotelReminderDB
DB_TRUSTED_CONNECTION=yes
DB_USER=
DB_PASSWORD=
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes
SECRET_KEY=doi_chuoi_bi_mat_nay
```

### SQL Server Authentication

Dùng khi đăng nhập bằng user/password SQL Server:

```env
DB_SERVER=localhost
DB_NAME=HotelReminderDB
DB_TRUSTED_CONNECTION=no
DB_USER=sa
DB_PASSWORD=mat_khau_cua_ban
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes
SECRET_KEY=doi_chuoi_bi_mat_nay
```

Nếu máy đang cài ODBC Driver 18, đổi:

```env
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes
```

Không commit file `.env` vì file này chứa cấu hình cục bộ và khóa bí mật.

## Khởi tạo cơ sở dữ liệu

Cách khuyến nghị:

1. Mở SQL Server Management Studio.
2. Kết nối tới SQL Server instance đang dùng.
3. Mở file `database/setup.sql`.
4. Chạy toàn bộ script.

Script `database/setup.sql` sẽ tạo database `HotelReminderDB` và các bảng chính nếu chưa tồn tại. Script có thể chạy lại nhiều lần trong quá trình phát triển.

Khi chạy `python app.py`, ứng dụng cũng gọi `Base.metadata.create_all()` và một số migration nhẹ để đảm bảo các cột/bảng bổ sung tồn tại.

## Chạy ứng dụng

Kích hoạt virtual environment rồi chạy:

```powershell
.\venv\Scripts\activate
python app.py
```

Nếu kết nối database thành công, terminal sẽ hiển thị ứng dụng đang chạy tại:

```text
http://127.0.0.1:5000
```

Truy cập trình duyệt:

- Giao diện chính: <http://127.0.0.1:5000>
- Đăng nhập: <http://127.0.0.1:5000/login>
- Giao diện React nhúng: <http://127.0.0.1:5000/ui>

## Tài khoản mẫu

Khi khởi động, ứng dụng tự seed một số dữ liệu mẫu nếu chưa tồn tại:

| Vai trò | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Manager | `manager1` | `manager123` |

Ứng dụng cũng tạo một số phòng mẫu như `101`, `201`, `301`, `401` nếu dữ liệu chưa có.

## Cấu trúc thư mục

```text
.
├── app.py
├── requirements.txt
├── .env.example
├── controllers/
│   ├── auth_controller.py
│   ├── reminder_controller.py
│   ├── user_controller.py
│   ├── room_controller.py
│   ├── guest_controller.py
│   ├── guest_notification_controller.py
│   ├── internal_notification_controller.py
│   ├── housekeeping_controller.py
│   ├── report_controller.py
│   ├── api_controller.py
│   └── react_controller.py
├── services/
│   └── *_service.py
├── repositories/
│   └── *_repository.py
├── models/
│   └── *.py
├── database/
│   ├── connection.py
│   └── setup.sql
├── scheduler/
│   └── reminder_scheduler.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── reminders/
│   ├── rooms/
│   ├── users/
│   ├── guests/
│   ├── bookings/
│   ├── housekeeping/
│   ├── guest_notifications/
│   ├── internal_notifications/
│   └── reports/
└── static/
    └── css/
```

## Các route chính

| Route | Chức năng |
| --- | --- |
| `/login` | Đăng nhập |
| `/logout` | Đăng xuất |
| `/` hoặc `/dashboard` | Dashboard |
| `/reminders` | Quản lý lịch nhắc |
| `/rooms` | Quản lý phòng |
| `/users` | Quản lý tài khoản |
| `/guests` | Quản lý khách hàng |
| `/bookings` | Quản lý đặt phòng |
| `/housekeeping` | Quản lý dọn phòng/bảo trì |
| `/internal-notifications` | Quản lý thông báo nội bộ |
| `/guest-notifications` | Quản lý thông báo khách |
| `/reports` | Báo cáo tổng quan |
| `/ui` | Giao diện React nhúng |

## API JSON

Các endpoint JSON có prefix `/api` và dùng chung Flask session với màn hình đăng nhập.

| Method | Endpoint | Chức năng |
| --- | --- | --- |
| `POST` | `/api/auth/login` | Đăng nhập qua API |
| `POST` | `/api/auth/logout` | Đăng xuất qua API |
| `GET` | `/api/auth/me` | Lấy thông tin người dùng hiện tại |
| `GET` | `/api/rooms` | Danh sách phòng |
| `POST` | `/api/rooms` | Tạo phòng |
| `PATCH` | `/api/rooms/<room_id>` | Cập nhật phòng |
| `DELETE` | `/api/rooms/<room_id>` | Xóa phòng |
| `GET` | `/api/users` | Danh sách người dùng |
| `POST` | `/api/users` | Tạo người dùng |
| `PATCH` | `/api/users/<user_id>/toggle-status` | Khóa/mở khóa tài khoản |
| `GET` | `/api/reminders` | Danh sách lịch nhắc |
| `GET` | `/api/maintenance-schedules` | Danh sách lịch bảo trì |
| `POST` | `/api/maintenance-schedules` | Tạo lịch bảo trì |
| `PATCH` | `/api/maintenance-schedules/<task_id>` | Cập nhật lịch bảo trì |
| `DELETE` | `/api/maintenance-schedules/<task_id>` | Hủy/xóa lịch bảo trì |

Ví dụ đăng nhập API:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:5000/api/auth/login `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"admin123"}'
```

## Ghi chú phát triển

- `controllers/` xử lý route, request, response và render template.
- `services/` chứa logic nghiệp vụ và validation.
- `repositories/` đóng gói thao tác truy vấn database.
- `models/` định nghĩa SQLAlchemy model.
- `database/connection.py` đọc `.env`, tạo SQLAlchemy engine và session.
- `scheduler/reminder_scheduler.py` chạy job nền kiểm tra lịch nhắc mỗi 1 phút.
- `templates/` chứa giao diện Jinja2.
- `static/` chứa CSS và tài nguyên tĩnh.

Khi thêm chức năng mới, nên đi theo luồng:

```text
Route trong controller -> Service xử lý nghiệp vụ -> Repository truy vấn database -> Model ánh xạ bảng
```

## Xử lý lỗi thường gặp

### Không kết nối được SQL Server

Kiểm tra lại:

- SQL Server đang chạy.
- `DB_SERVER` trong `.env` đúng instance name.
- Đã cài ODBC Driver đúng với `DB_DRIVER`.
- Nếu dùng SQL Server Authentication, user/password đúng và SQL Server đã bật mixed authentication.
- Nếu dùng Windows Authentication, để trống `DB_USER`, `DB_PASSWORD` và đặt `DB_TRUSTED_CONNECTION=yes`.

### Lỗi ODBC Driver not found

Cài ODBC Driver for SQL Server, sau đó chỉnh `.env`:

```env
DB_DRIVER=ODBC Driver 17 for SQL Server
```

hoặc:

```env
DB_DRIVER=ODBC Driver 18 for SQL Server
```

### Trang hiển thị tiếng Việt bị lỗi font

Đảm bảo file được lưu bằng UTF-8 và template HTML có:

```html
<meta charset="UTF-8">
```

### Không đăng nhập được bằng tài khoản mẫu

Kiểm tra database đã được tạo và ứng dụng đã chạy qua bước seed dữ liệu. Có thể chạy lại:

```powershell
python app.py
```

Sau khi seed thành công, thử lại:

```text
admin / admin123
manager1 / manager123
```

## License

Dự án phục vụ mục đích học tập và đồ án môn Công nghệ Phần mềm.
