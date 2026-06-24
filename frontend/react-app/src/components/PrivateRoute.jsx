import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Thay cho `if (!API.requireAuth()) return;` lặp lại ở đầu users.js và
 * guests.js gốc. Bọc quanh các route cần đăng nhập; nếu chưa có token
 * thì điều hướng về /ui/login giống `window.location.href = redirectTo`.
 */
export default function PrivateRoute({ children, allowedRoles }) {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/ui/login" replace />;
  }

  // Tương đương kiểm tra role trong users.js:
  // if (!["admin", "manager"].includes(user.role)) { window.location.href = "/ui/guests"; }
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/ui/guests" replace />;
  }

  return children;
}
