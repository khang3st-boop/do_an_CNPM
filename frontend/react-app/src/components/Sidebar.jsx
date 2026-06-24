import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { roleLabel } from "../utils/format";

/**
 * Sidebar dùng chung cho UsersPage và GuestsPage - phần markup này bị
 * lặp lại y hệt trong templates/users.html và templates/guests.html
 * (chỉ khác class "active" ở từng nav-item). Logic showCurrentUser()
 * và setupLogout() trong api.js gốc được gộp vào đây.
 */
export default function Sidebar() {
  const { user, logout } = useAuth();
  const canSeeUsers = user && ["admin", "manager"].includes(user.role);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-icon sm">H</span>
        <span>Hotel Reminder</span>
      </div>
      <nav className="sidebar-nav">
        <NavLink
          to="/ui/guests"
          className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
        >
          Thông tin khách hàng
        </NavLink>
        {/* Tương đương usersNav.style.display = "none" khi role không phải admin/manager */}
        {canSeeUsers && (
          <NavLink
            to="/ui/users"
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            Phân quyền tài khoản
          </NavLink>
        )}
        <a href="/docs" className="nav-item" target="_blank" rel="noreferrer">
          API Docs
        </a>
      </nav>
      <div className="sidebar-footer">
        <div className="user-badge">
          {user ? `${user.name} (${roleLabel(user.role)})` : ""}
        </div>
        <button className="btn btn-ghost btn-sm" onClick={logout}>
          Đăng xuất
        </button>
      </div>
    </aside>
  );
}
