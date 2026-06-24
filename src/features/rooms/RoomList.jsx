import React, { useState, useEffect } from 'react';
import { RoomService } from './RoomService';

const RoomList = () => {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State tìm kiếm và lọc dữ liệu
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchRooms = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await RoomService.getRooms();
        if (result.success && result.data) {
          setRooms(result.data);
        } else {
          setRooms([]);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchRooms();
  }, []);

  // 1. Tính toán nhanh các số liệu thống kê từ dữ liệu thật đổ về
  const totalRooms = rooms.length;
  const occupiedCount = rooms.filter(r => r.status === 'occupied' || r.status === 'Đang ở').length;
  const vacantCount = rooms.filter(r => r.status === 'available' || r.status === 'Trống').length;
  const dndCount = rooms.filter(r => r.status === 'maintenance' || r.status === 'Bảo trì').length; // Giả định bảo trì hoặc DND

  // 2. Lọc danh sách phòng theo thanh tìm kiếm (Số phòng hoặc tên khách)
  const filteredRooms = rooms.filter(room => {
    const matchesNumber = room.room_number?.toString().includes(searchTerm);
    const matchesType = room.room_type?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesNumber || matchesType;
  });

  // Hàm định dạng thẻ Trạng thái (Badge) bên trong từng Card phòng
  const getStatusBadge = (status) => {
    switch (status) {
      case 'available':
      case 'Trống':
        return { bg: '#e0f2fe', color: '#0369a1', text: 'Vacant' };
      case 'occupied':
      case 'Đang ở':
        return { bg: '#e0e7ff', color: '#4f46e5', text: 'Occupied' };
      case 'maintenance':
      case 'Bảo trì':
        return { bg: '#fff7ed', color: '#c2410c', text: 'DND Active' };
      default:
        return { bg: '#f1f5f9', color: '#475569', text: status };
    }
  };

  if (loading) return <div style={{ padding: '40px', textAlign: 'center', fontFamily: 'Segoe UI, sans-serif', color: '#64748b' }}>🔄 Đang tải dữ liệu phòng...</div>;
  if (error) return <div style={{ padding: '24px', color: '#dc2626', background: '#fef2f2', borderRadius: '12px', fontFamily: 'Segoe UI, sans-serif', margin: '20px' }}>⚠️ Lỗi hệ thống: {error}</div>;

  return (
    <div style={{ fontFamily: '"Segoe UI", Roboto, sans-serif', padding: '24px', backgroundColor: '#f8fafc', minHeight: '100vh' }}>
      
      {/* Tiêu đề trang */}
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ margin: 0, fontSize: '28px', fontWeight: '700', color: '#1e293b' }}>Room Management</h1>
        <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '15px' }}>Monitor and manage all hotel rooms</p>
      </div>

      {/* KHU VỰC 1: Thanh thống kê nhanh (4 ô màu sắc dịu nhẹ) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '20px', marginBottom: '28px' }}>
        <div style={{ backgroundColor: '#eff6ff', borderRadius: '16px', padding: '20px', border: '1px solid #dbeafe', boxShadow: '0 2px 12px rgba(0,0,0,0.01)' }}>
          <p style={{ margin: 0, color: '#475569', fontSize: '14px', fontWeight: '500' }}>Total Rooms</p>
          <h2 style={{ margin: '10px 0 0 0', fontSize: '32px', fontWeight: '700', color: '#1e293b' }}>{totalRooms}</h2>
        </div>
        <div style={{ backgroundColor: '#eef2ff', borderRadius: '16px', padding: '20px', border: '1px solid #e0e7ff' }}>
          <p style={{ margin: 0, color: '#475569', fontSize: '14px', fontWeight: '500' }}>Occupied</p>
          <h2 style={{ margin: '10px 0 0 0', fontSize: '32px', fontWeight: '700', color: '#1e293b' }}>{occupiedCount}</h2>
        </div>
        <div style={{ backgroundColor: '#f8fafc', borderRadius: '16px', padding: '20px', border: '1px solid #e2e8f0' }}>
          <p style={{ margin: 0, color: '#475569', fontSize: '14px', fontWeight: '500' }}>Vacant</p>
          <h2 style={{ margin: '10px 0 0 0', fontSize: '32px', fontWeight: '700', color: '#1e293b' }}>{vacantCount}</h2>
        </div>
        <div style={{ backgroundColor: '#fff7ed', borderRadius: '16px', padding: '20px', border: '1px solid #ffedd5' }}>
          <p style={{ margin: 0, color: '#475569', fontSize: '14px', fontWeight: '500' }}>DND Active</p>
          <h2 style={{ margin: '10px 0 0 0', fontSize: '32px', fontWeight: '700', color: '#1e293b' }}>{dndCount}</h2>
        </div>
      </div>

      {/* KHU VỰC 2: Thanh Công Cụ (Tìm kiếm và Nút Bộ lọc) */}
      <div style={{ backgroundColor: '#ffffff', borderRadius: '14px', padding: '16px 20px', display: 'flex', gap: '16px', alignItems: 'center', boxShadow: '0 4px 14px rgba(148, 163, 184, 0.05)', border: '1px solid #f1f5f9', marginBottom: '28px' }}>
        <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center' }}>
          <span style={{ position: 'absolute', left: '14px', color: '#94a3b8', fontSize: '16px' }}>🔍</span>
          <input 
            type="text" 
            placeholder="Search by room number or room type..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '100%', padding: '10px 16px 10px 42px', borderRadius: '10px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', backgroundColor: '#f8fafc' }}
          />
        </div>
        <button style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '10px 20px', borderRadius: '10px', fontWeight: '600', color: '#334155', display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
          <span>🎛️</span> Filter
        </button>
      </div>

      {/* KHU VỰC 3: Lưới danh sách phòng dạng Card (Mỗi hàng 3-4 ô tùy màn hình) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '24px' }}>
        {filteredRooms.length === 0 ? (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', padding: '40px', color: '#94a3b8', backgroundColor: '#fff', borderRadius: '12px' }}>
            Không có phòng nào khớp với từ khóa tìm kiếm.
          </div>
        ) : (
          filteredRooms.map((room) => {
            const badge = getStatusBadge(room.status);
            return (
              <div key={room.id} style={{ 
                backgroundColor: '#ffffff', 
                borderRadius: '16px', 
                padding: '20px', 
                boxShadow: '0 4px 16px rgba(148, 163, 184, 0.06)', 
                border: '1px solid #f1f5f9',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}>
                {/* Phần đầu Card: Số phòng + Tầng */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{ width: '44px', height: '44px', borderRadius: '10px', backgroundColor: '#e0e7ff', display: 'flex', alignItems: 'center', justifycontent: 'center', fontSize: '20px', color: '#4f46e5', justifyContent: 'center' }}>
                    🛏️
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '20px', fontWeight: '700', color: '#1e293b' }}>{room.room_number}</h3>
                    <p style={{ margin: 0, fontSize: '13px', color: '#64748b', fontWeight: '500' }}>Floor {room.floor} • {room.room_type}</p>
                  </div>
                </div>

                {/* Phần giữa Card: Giá cả và nhãn trạng thái */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                  <span style={{ backgroundColor: badge.bg, color: badge.color, padding: '4px 12px', borderRadius: '8px', fontSize: '13px', fontWeight: '600' }}>
                    {badge.text}
                  </span>
                  <span style={{ fontSize: '15px', fontWeight: '700', color: '#059669' }}>
                    {room.price_per_night?.toLocaleString('vi-VN')} đ/đêm
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};

export default RoomList;