const API_URL = 'http://localhost:8000/api/rooms';

export const RoomService = {
  // 1. Hàm lấy danh sách phòng
  getRooms: async () => {
    try {
      const token = localStorage.getItem('token'); // Lấy mã token đã lưu khi đăng nhập

      const response = await fetch(API_URL, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Vượt bộ lọc phân quyền của FastAPI
        }
      });

      if (response.status === 401 || response.status === 403) {
        throw new Error('Tài khoản của bạn không có quyền xem danh sách phòng.');
      }

      if (!response.ok) {
        throw new Error('Không thể kết nối danh sách phòng từ server.');
      }

      return await response.json(); // Trả về object dữ liệu dạng { success: true, data: [...] }
    } catch (error) {
      throw error;
    }
  }
};