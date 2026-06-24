/**
 * Các hàm tiện ích hiển thị - chuyển đổi từ app/static/js/api.js
 */

export function formatDateTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  return date.toLocaleString("vi-VN");
}

const ROLE_LABELS = {
  admin: "Admin",
  manager: "Manager",
  receptionist: "Lễ tân",
  housekeeping: "Buồng phòng",
  technician: "Kỹ thuật",
  staff: "Nhân viên",
};

export function roleLabel(role) {
  return ROLE_LABELS[role] || role;
}
