import axios from 'axios';

// Dòng này rất quan trọng: thay URL bằng địa chỉ Backend của bạn
const API_BASE_URL = 'http://localhost:8080/api'; 

export const fetchAccounts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/accounts`);
    return response.data;
  } catch (error) {
    console.error("Lỗi khi kết nối Backend:", error);
    return []; // Trả về mảng rỗng để không bị crash app
  }
};