// src/App.js
import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import RoomList from './features/rooms/RoomList';
import AccountTable from './features/accounts/AccountTable';
import LoginPage from './pages/LoginPage';

const AppLayout = () => {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  // Cách viết layout hiện đại và ổn định hơn
  const layoutStyle = {
    display: 'flex',
    minHeight: '100vh',
  };

  const mainContentStyle = {
    flex: 1, // Tự động giãn ra lấp đầy phần còn lại
    padding: '32px',
    background: '#f9fafb',
    transition: 'all 0.3s ease',
    // Đảm bảo nội dung không bị tràn ngang
    overflowX: 'hidden' 
  };

  return (
    <div style={layoutStyle}>
      {/* Chỉ hiện Sidebar khi không ở trang login */}
      {!isLoginPage && <Sidebar />} 
      
      <main style={mainContentStyle}>
        <Routes>
          <Route path="/" element={<Navigate to="/rooms" />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/rooms" element={<RoomList />} />
          <Route path="/accounts" element={<AccountTable />} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return <AppLayout />;
}

export default App;