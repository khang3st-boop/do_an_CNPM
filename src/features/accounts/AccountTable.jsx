import React, { useEffect, useState } from 'react';
import { fetchAccounts } from './AccountService'; // Import hàm gọi API
import { ACCOUNT_COLUMNS } from './AccountConstants'; // Import cấu hình cột
import './AccountTable.css';

const AccountTable = () => {
  const [accounts, setAccounts] = useState([]); // Lưu trữ dữ liệu lấy về từ Backend

  useEffect(() => {
    // Hàm chạy ngay khi Component vừa hiển thị
    const loadData = async () => {
      const data = await fetchAccounts();
      setAccounts(data);
    };
    loadData();
  }, []);

  return (
    <div className="container">
      <h2>Danh sách tài khoản</h2>
      <table className="styled-table">
        <thead>
          <tr>
            {ACCOUNT_COLUMNS.map(col => <th key={col.key}>{col.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {accounts.map((acc) => (
            <tr key={acc.id}>
              <td>{acc.id}</td>
              <td>{acc.username}</td>
              <td>{acc.role}</td>
              <td>
                <button className="btn-edit">Sửa</button>
                <button className="btn-delete">Xóa</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AccountTable;