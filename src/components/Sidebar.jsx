import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h2>Hotel Admin</h2>
        <p>Notification System</p>
      </div>

      <nav className="sidebar-nav">
        {/* NavLink tự thêm class 'active' khi đường dẫn khớp, không cần gõ thủ công */}
        <NavLink to="/dashboard" className="nav-item">Dashboard</NavLink>
        <NavLink to="/rooms" className="nav-item">Rooms</NavLink>
        <NavLink to="/staff" className="nav-item">Staff</NavLink>
        <NavLink to="/notifications" className="nav-item">Notifications</NavLink>
        <NavLink to="/settings" className="nav-item">Settings</NavLink>
      </nav>

      <div className="sidebar-footer">
        {user ? (
          <button className="btn-auth logout" onClick={logout}>Logout</button>
        ) : (
          <button className="btn-auth login" onClick={() => navigate("/login")}>Login</button>
        )}
      </div>
    </aside>
  );
}