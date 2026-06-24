# Hotel Reminder - Frontend React

Bản chuyển đổi từ frontend HTML/JS thuần (Jinja2 templates + vanilla JS)
sang React (JSX). Backend FastAPI (`app/`) giữ nguyên không đổi — chỉ
cần xoá/bỏ các route render template trong `app/routers/web.py` nếu
không dùng nữa, các route `/api/...` vẫn giữ nguyên 100%.

## Cấu trúc

```
src/
├── api/
│   └── api.js              # gọi backend, thay cho static/js/api.js
├── context/
│   └── AuthContext.jsx     # quản lý session đăng nhập (thay localStorage rải rác)
├── components/
│   ├── Sidebar.jsx         # sidebar dùng chung (users.html + guests.html)
│   ├── Modal.jsx           # modal dùng chung (thay setupModal())
│   ├── Alert.jsx           # banner lỗi (thay showError/hideError)
│   ├── Badge.jsx           # badge trạng thái (thay statusBadge())
│   └── PrivateRoute.jsx    # bảo vệ route cần đăng nhập (thay requireAuth())
├── pages/
│   ├── LoginPage.jsx       # thay templates/login.html + static/js/login.js
│   ├── GuestsPage.jsx      # thay templates/guests.html + static/js/guests.js
│   └── UsersPage.jsx       # thay templates/users.html + static/js/users.js
├── utils/
│   └── format.js           # formatDateTime, roleLabel
├── styles/
│   └── main.css            # giữ nguyên 100% từ static/css/main.css
├── App.jsx                  # định nghĩa route /ui/login, /ui/guests, /ui/users
└── main.jsx                  # entry point
```

## Cách chạy

1. Cài dependencies:
   ```bash
   npm install
   ```

2. Chạy backend FastAPI như cũ (cổng 8000):
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. Chạy frontend React (cổng 5173, tự proxy `/api` sang `localhost:8000`):
   ```bash
   npm run dev
   ```

4. Mở `http://localhost:5173/ui/login`

## Build production

```bash
npm run build
```

Sau khi build, có thể trỏ FastAPI `StaticFiles` vào thư mục `dist/` để
phục vụ luôn trên cùng domain (khi đó không cần cấu hình proxy nữa).

## Đối chiếu logic quan trọng

| Logic gốc (vanilla JS)                     | Trong React                                  |
|---------------------------------------------|-----------------------------------------------|
| `localStorage` token/user                   | `AuthContext` + `api.js` (vẫn dùng localStorage bên dưới) |
| `API.requireAuth()`                         | `<PrivateRoute>`                              |
| `setupModal()` show/hide bằng class `hidden`| `<Modal open={...}>` điều khiển qua state     |
| `showError`/`hideError`                     | `<Alert message={...}>`                       |
| `tbody.innerHTML = items.map(...)`          | render `<tr>` trực tiếp trong JSX, React tự re-render |
| `renderGuests()` lọc lại DOM thủ công        | `useMemo(filteredItems)` tính lại tự động     |
| `window.toggleUser = toggleUser` (global fn) | hàm nội bộ component, gắn qua `onClick`        |
