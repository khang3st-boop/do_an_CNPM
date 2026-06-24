import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Trang đăng nhập - chuyển đổi từ templates/login.html + static/js/login.js
 *
 * Đối chiếu với login.js gốc:
 * - if (API.getToken()) { window.location.href = "/ui/guests"; }
 *   -> useEffect kiểm tra isAuthenticated rồi navigate.
 * - form.addEventListener("submit", ...) -> handleSubmit.
 * - showError("loginError", ...) -> state `error` + component Alert inline.
 * - btn.disabled / btn.textContent -> state `loading`.
 */
export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/ui/guests", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const loggedInUser = await login(email.trim(), password);

      // Tương đương: if (["admin", "manager"].includes(result.data.user.role)) { ... }
      if (["admin", "manager"].includes(loggedInUser.role)) {
        navigate("/ui/users");
      } else {
        navigate("/ui/guests");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="brand">
          <div className="brand-icon">H</div>
          <h1>Hotel Reminder</h1>
          <p>Hệ thống quản lý thông báo &amp; nhắc lịch khách sạn</p>
        </div>

        <form className="form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="admin@hotel.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Mật khẩu</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
            {loading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>

        <div className="demo-box">
          <p className="demo-title">Tài khoản demo</p>
          <ul>
            <li><strong>Admin:</strong> admin@hotel.com / 123456</li>
            <li><strong>Lễ tân:</strong> reception@hotel.com / 123456</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
