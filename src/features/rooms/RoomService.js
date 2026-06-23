export const fetchRooms = async () => {
  const response = await fetch('/api/rooms'); // URL API theo tài liệu dự án của bạn
  return response.json();
};