import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  // Style cơ bản bằng CSS-in-JS cho giao diện Admin chuyên nghiệp
  const sidebarStyle = {
    width: '260px',
    height: '100vh',
    background: '#111827', // Màu tối sang trọng (Charcoal)
    color: '#fff',
    padding: '24px 16px',
    boxSizing: 'border-box',
    position: 'fixed',
    top: 0,
    left: 0
  };

  const navLinkStyle = ({ isActive }) => ({
    display: 'block',
    padding: '12px 16px',
    color: isActive ? '#3b82f6' : '#9ca3af', // Đổi màu xanh khi đang ở trang đó
    background: isActive ? '#1f2937' : 'transparent',
    textDecoration: 'none',
    borderRadius: '6px',
    marginBottom: '8px',
    fontWeight: '500',
    fontSize: '15px',
    transition: 'all 0.2s'
  });

  return (
    <div style={sidebarStyle}>
      <div style={{ padding: '0 16px 24px 16px', fontSize: '18px', fontWeight: 'bold', borderBottom: '1px solid #1f2937', marginBottom: '24px' }}>
        🏨 HOTEL MANAGEMENT
      </div>
      
      <nav>
        <div style={{ padding: '0 16px 8px 16px', color: '#4b5563', fontSize: '12px', fontWeight: 'bold', textTransform: 'uppercase' }}>
          Quản lý vận hành
        </div>
        {/* Đường dẫn tới tính năng Phòng */}
        <NavLink to="/rooms" style={navLinkStyle}>
          🛏️ Danh sách phòng
        </NavLink>

        <div style={{ padding: '16px 16px 8px 16px', color: '#4b5563', fontSize: '12px', fontWeight: 'bold', textTransform: 'uppercase' }}>
          Hệ thống
        </div>
        {/* Đường dẫn tới tính năng Tài khoản */}
        <NavLink to="/accounts" style={navLinkStyle}>
          👤 Quản lý tài khoản
        </NavLink>
      </nav>
    </div>
  );
};

export default Sidebar;