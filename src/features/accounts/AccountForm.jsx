import React from 'react';

const AccountForm = ({ onClose }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Thêm tài khoản mới</h3>
        <input type="text" placeholder="Tên đăng nhập" style={{ width: '100%', marginBottom: '10px' }} />
        <select style={{ width: '100%', marginBottom: '10px' }}>
          <option>Admin</option>
          <option>Staff</option>
        </select>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
          <button onClick={onClose}>Hủy</button>
          <button className="btn-add">Lưu</button>
        </div>
      </div>
    </div>
  );
};

export default AccountForm;