# Đặc tả Backend API

## 1. API đăng nhập

### POST /api/auth/login

Dùng để đăng nhập vào hệ thống.

Dữ liệu gửi lên:

- email
- password

Kết quả trả về:

- Thông tin người dùng
- Vai trò người dùng
- Token đăng nhập

---

## 2. API thông báo nhắc lịch

### POST /api/reminders

Dùng để tạo thông báo nhắc lịch mới.

Dữ liệu gửi lên:

- title
- content
- reminderTime
- roomId
- assignedUserId
- type

Kết quả trả về:

- Thông báo tạo thành công
- Thông tin lịch nhắc vừa tạo

---

### GET /api/reminders

Dùng để lấy danh sách thông báo nhắc lịch.

Kết quả trả về:

- Mã thông báo
- Tiêu đề
- Nội dung
- Thời gian nhắc
- Phòng liên quan
- Nhân viên phụ trách
- Trạng thái xử lý

---

### GET /api/reminders?date=2026-05-28

Dùng để lọc thông báo theo ngày.

---

### GET /api/reminders?roomId=101

Dùng để lọc thông báo theo phòng.

---

### PUT /api/reminders/{id}/status

Dùng để cập nhật trạng thái thông báo.

Dữ liệu gửi lên:

- status

Các trạng thái:

- pending
- processing
- completed
- cancelled