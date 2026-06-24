import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import PrivateRoute from "./components/PrivateRoute";
import LoginPage from "./pages/LoginPage";
import GuestsPage from "./pages/GuestsPage";
import UsersPage from "./pages/UsersPage";
import "./styles/main.css";

/**
 * App.jsx - định nghĩa các route phía client, thay cho các route
 * /ui/login, /ui/guests, /ui/users vốn được FastAPI (app/routers/web.py)
 * render template Jinja2 phía server. Bây giờ FastAPI chỉ cần phục vụ
 * các API (/api/...) còn phần UI hoàn toàn do React Router xử lý.
 */
function AuthRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/ui/login" replace />} />
      <Route path="/ui/login" element={<LoginPage />} />

      <Route
        path="/ui/guests"
        element={
          <PrivateRoute>
            <GuestsPage />
          </PrivateRoute>
        }
      />

      {/* Tương đương kiểm tra role trong users.js: chỉ admin/manager được vào */}
      <Route
        path="/ui/users"
        element={
          <PrivateRoute allowedRoles={["admin", "manager"]}>
            <UsersPage />
          </PrivateRoute>
        }
      />

      <Route path="*" element={<Navigate to="/ui/login" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AuthRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
