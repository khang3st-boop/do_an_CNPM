# Backend API - Quản lý thông báo nhắc lịch khách sạn

Backend được xây dựng theo mô hình ASP.NET Core Web API, sử dụng Controller để định nghĩa các API endpoint.

## Controller chính

### AuthController

Xử lý đăng nhập và phân quyền người dùng.

API:
- POST /api/auth/login

### ReminderController

Xử lý quản lý thông báo nhắc lịch trong khách sạn.

API:
- GET /api/reminders
- GET /api/reminders/{id}
- POST /api/reminders
- PUT /api/reminders/{id}/status
- GET /api/reminders/filter

## Chức năng backend

- Đăng nhập hệ thống
- Xem danh sách thông báo nhắc lịch
- Xem chi tiết thông báo
- Tạo thông báo nhắc lịch mới
- Cập nhật trạng thái thông báo
- Lọc thông báo theo phòng hoặc trạng thái