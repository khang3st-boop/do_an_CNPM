import React, { useState, useEffect } from 'react';
import { fetchRooms } from './RoomService'; // Gọi service từ bước trước

const RoomList = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      const data = await fetchRooms();
      setRooms(data);
    } catch (error) {
      console.error("Lỗi tải danh sách phòng:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center p-5">Đang tải dữ liệu...</div>;

  return (
    <div className="room-list-container">
      <div className="header d-flex justify-content-between align-items-center mb-4">
        <h2>Danh sách phòng khách sạn</h2>
        <button className="btn btn-primary">+ Thêm phòng mới</button>
      </div>

      <table className="table table-hover align-middle">
        <thead className="table-light">
          <tr>
            <th>Tên phòng</th>
            <th>Loại phòng</th>
            <th>Trạng thái</th>
            <th className="text-end">Hành động</th>
          </tr>
        </thead>
        <tbody>
          {rooms.length > 0 ? (
            rooms.map((room) => (
              <tr key={room.id}>
                <td><strong>{room.name}</strong></td>
                <td>{room.type}</td>
                <td>
                  <span className={`badge ${room.status === 'Available' ? 'bg-success' : 'bg-warning'}`}>
                    {room.status}
                  </span>
                </td>
                <td className="text-end">
                  <button className="btn btn-sm btn-outline-info me-2">Sửa</button>
                  <button className="btn btn-sm btn-outline-danger">Xóa</button>
                </td>
              </tr>
            ))
          ) : (
            <tr><td colSpan="4" className="text-center">Chưa có phòng nào được tạo.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default RoomList;