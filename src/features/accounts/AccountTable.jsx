import React, { useState, useEffect, useCallback } from 'react';

const AccountTable = () => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State phục vụ Bộ lọc và Tìm kiếm
  const [keyword, setKeyword] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // State quản lý Modal Thêm mới
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '', email: '', password: '', role: 'receptionist', department: 'reception', phone: ''
  });
  const [formError, setFormError] = useState('');

  // Hàm gọi API lấy danh sách (Bọc bằng useCallback để tránh render thừa)
  const fetchAccounts = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Xây dựng Query Parameters dựa trên Backend hỗ trợ
      let url = 'http://localhost:8000/api/users?';
      if (keyword) url += `keyword=${encodeURIComponent(keyword)}&`;
      if (roleFilter) url += `role=${roleFilter}&`;
      if (statusFilter) url += `status_filter=${statusFilter}&`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) throw new Error('Không thể tải danh sách tài khoản.');
      const result = await response.json();
      
      if (result.success && result.data) {
        setAccounts(result.data);
      } else {
        setAccounts([]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [keyword, roleFilter, statusFilter]); // Tự động cập nhật tham số truy vấn mới nhất

  // Chạy lại mỗi khi ô tìm kiếm hoặc bộ lọc thay đổi dữ liệu
  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]); 

  // Hàm xử lý Tìm kiếm (Giờ chỉ cần kích hoạt fetchAccounts trực tiếp)
  const handleSearch = (e) => {
    e.preventDefault();
    fetchAccounts();
  };

  // Hàm xử lý Bật/Tắt trạng thái hoạt động tài khoản (PATCH API)
  const handleToggleStatus = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/users/${userId}/toggle-status`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Cập nhật thất bại');
      
      // Đồng bộ trạng thái mới từ API trả về (active / locked)
      setAccounts(prevAccounts => 
        prevAccounts.map(acc => acc.id === userId ? { ...acc, status: result.data.status } : acc)
      );
    } catch (err) {
      alert(`⚠️ Lỗi: ${err.message}`);
    }
  };

  // Hàm xử lý gửi Form tạo tài khoản mới (POST API)
  const handleCreateUser = async (e) => {
    e.preventDefault();
    setFormError('');
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/users', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.message || 'Đã có lỗi xảy ra');

      setIsModalOpen(false); // Đóng modal
      setFormData({ name: '', email: '', password: '', role: 'receptionist', department: 'reception', phone: '' }); // Reset form
      fetchAccounts(); // Làm mới lại danh sách hiển thị
    } catch (err) {
      setFormError(err.message);
    }
  };

  const getRoleBadgeStyle = (role) => {
    switch (role) {
      case 'admin': return { bg: '#fee2e2', color: '#991b1b', text: 'Quản trị viên' };
      case 'receptionist': return { bg: '#e0f2fe', color: '#0369a1', text: 'Lễ tân' };
      case 'housekeeping': return { bg: '#f3e8ff', color: '#6b21a8', text: 'Buồng phòng' };
      default: return { bg: '#f1f5f9', color: '#475569', text: role };
    }
  };

  return (
    <div style={{ fontFamily: 'Segoe UI, sans-serif', padding: '10px' }}>
      {/* Tiêu đề & Nút thêm */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '24px', color: '#111827' }}>Quản lý tài khoản nhân viên</h2>
          <p style={{ margin: '4px 0 0 0', color: '#6b7280', fontSize: '14px' }}>Danh sách tài khoản nhân viên phân theo phòng ban</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          style={{ background: '#059669', color: '#fff', border: 'none', padding: '10px 16px', borderRadius: '8px', fontWeight: '500', cursor: 'pointer' }}
        >
          + Cấp tài khoản mới
        </button>
      </div>

      {/* Thanh Công cụ: Tìm kiếm & Bộ lọc */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap', alignItems: 'center' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '6px', flex: 1, minWidth: '260px' }}>
          <input 
            type="text" 
            placeholder="Tìm theo tên, email, sđt..." 
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            style={{ flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
          />
          <button type="submit" style={{ background: '#2563eb', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer' }}>Tìm</button>
        </form>

        <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }}>
          <option value="">-- Tất cả chức vụ --</option>
          <option value="admin">Quản trị viên</option>
          <option value="receptionist">Lễ tân</option>
          <option value="housekeeping">Buồng phòng</option>
        </select>

        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }}>
          <option value="">-- Tất cả trạng thái --</option>
          <option value="active">Hoạt động</option>
          <option value="locked">Tạm khóa</option>
        </select>
      </div>

      {/* Bảng Dữ liệu */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>🔄 Đang tải dữ liệu...</div>
      ) : error ? (
        <div style={{ color: '#dc2626', background: '#fef2f2', padding: '16px', borderRadius: '8px' }}>⚠️ {error}</div>
      ) : (
        <div style={{ background: '#fff', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                <th style={{ padding: '14px 20px', color: '#475569' }}>Họ tên nhân viên</th>
                <th style={{ padding: '14px 20px', color: '#475569' }}>Email đăng nhập</th>
                <th style={{ padding: '14px 20px', color: '#475569' }}>Bộ phận</th>
                <th style={{ padding: '14px 20px', color: '#475569' }}>Chức vụ</th>
                <th style={{ padding: '14px 20px', color: '#475569' }}>Trạng thái</th>
                <th style={{ padding: '14px 20px', color: '#475569', textAlign: 'center' }}>Hành động</th>
              </tr>
            </thead>
            <tbody>
              {accounts.length === 0 ? (
                <tr><td colSpan="6" style={{ padding: '32px', textAlign: 'center', color: '#9ca3af' }}>Không tìm thấy nhân viên nào phù hợp.</td></tr>
              ) : (
                accounts.map((acc) => {
                  const roleStyle = getRoleBadgeStyle(acc.role);
                  return (
                    <tr key={acc.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '14px 20px', fontWeight: '500' }}>{acc.name}</td>
                      <td style={{ padding: '14px 20px', color: '#475569' }}>{acc.email}</td>
                      <td style={{ padding: '14px 20px', color: '#64748b', textTransform: 'capitalize' }}>{acc.department}</td>
                      <td style={{ padding: '14px 20px' }}>
                        <span style={{ background: roleStyle.bg, color: roleStyle.color, padding: '4px 8px', borderRadius: '6px', fontSize: '13px' }}>
                          {roleStyle.text}
                        </span>
                      </td>
                      <td style={{ padding: '14px 20px' }}>
                        <span style={{ color: acc.status === 'active' ? '#16a34a' : '#dc2626', fontWeight: '500' }}>
                          {acc.status === 'active' ? '● Hoạt động' : '● Tạm khóa'}
                        </span>
                      </td>
                      <td style={{ padding: '14px 20px', textAlign: 'center' }}>
                        <button 
                          onClick={() => handleToggleStatus(acc.id)}
                          style={{ background: acc.status === 'active' ? '#ea580c' : '#0284c7', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' }}
                        >
                          {acc.status === 'active' ? 'Khóa lại' : 'Mở khóa'}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* MODAL THÊM TÀI KHOẢN MỚI */}
      {isModalOpen && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '12px', width: '400px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '18px' }}>Cấp Tài Khoản Nhân Viên Mới</h3>
            {formError && <div style={{ color: '#dc2626', background: '#fef2f2', padding: '8px', borderRadius: '6px', marginBottom: '12px', fontSize: '13px' }}>⚠️ {formError}</div>}
            
            <form onSubmit={handleCreateUser} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <input type="text" placeholder="Họ và tên" required value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              <input type="email" placeholder="Email" required value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              <input type="password" placeholder="Mật khẩu khởi tạo" required value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              <input type="text" placeholder="Số điện thoại" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              
              <label style={{ fontSize: '13px', color: '#475569' }}>Chức vụ:</label>
              <select value={formData.role} onChange={(e) => setFormData({...formData, role: e.target.value})} style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }}>
                <option value="admin">Quản trị viên</option>
                <option value="receptionist">Lễ tân</option>
                <option value="housekeeping">Buồng phòng</option>
              </select>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '12px' }}>
                <button type="button" onClick={() => setIsModalOpen(false)} style={{ background: '#94a3b8', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer' }}>Hủy</button>
                <button type="submit" style={{ background: '#059669', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer' }}>Lưu lại</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountTable;