import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';

// Import các tính năng từ 2 nhánh đã gộp
import RoomList from './features/rooms/RoomList';
import AccountTable from './features/accounts/AccountTable';

function App() {
  // Style để đẩy nội dung bên phải sang, không bị thanh Menu đè lên
  const mainContentStyle = {
    marginLeft: '260px', 
    padding: '32px',
    background: '#f9fafb',
    minHeight: '100vh',
    boxSizing: 'border-box',
    flex: 1
  };

  return (
    <Router>
      <div style={{ display: 'flex' }}>
        {/* 1. Thanh Menu chính cố định ở bên trái */}
        <Sidebar />

        {/* 2. Vùng hiển thị nội dung động ở bên phải */}
        <div style={mainContentStyle}>
          <Routes>
            {/* Vừa vào trang chủ tự động chuyển hướng sang trang phòng */}
            <Route path="/" element={<Navigate to="/rooms" />} />
            
            {/* Khi URL là /rooms -> Hiển thị Danh sách phòng */}
            <Route path="/rooms" element={<RoomList />} />
            
            {/* Khi URL là /accounts -> Hiển thị Bảng tài khoản của bạn */}
            <Route path="/accounts" element={<AccountTable />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;