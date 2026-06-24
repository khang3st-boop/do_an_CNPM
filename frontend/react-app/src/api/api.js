/**
 * API service - chuyển đổi từ app/static/js/api.js
 * Toàn bộ logic gọi backend FastAPI được giữ nguyên, chỉ đổi cách lưu
 * session (localStorage) sang dùng cùng cơ chế nhưng export dạng module
 * để các component React import và dùng trực tiếp.
 */

const TOKEN_KEY = "token";
const USER_KEY = "user";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Hàm fetch dùng chung cho mọi request, tự đính kèm token và xử lý lỗi.
 * onUnauthorized: callback được gọi khi token hết hạn / không hợp lệ (401),
 * dùng để điều hướng người dùng về trang đăng nhập từ React Router.
 */
async function request(path, options = {}, onUnauthorized) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(path, { ...options, headers });
  const data = await response.json().catch(() => ({}));

  if (response.status === 401) {
    clearSession();
    if (onUnauthorized) onUnauthorized();
    throw new Error(data.message || "Phiên đăng nhập hết hạn");
  }

  if (!response.ok) {
    throw new Error(data.message || "Có lỗi xảy ra");
  }

  return data;
}

export const API = {
  getToken,
  getUser,
  setSession,
  clearSession,

  async login(email, password) {
    return request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  async me(onUnauthorized) {
    return request("/api/auth/me", {}, onUnauthorized);
  },

  async getUsers(params = {}, onUnauthorized) {
    const query = new URLSearchParams(params).toString();
    return request(`/api/users${query ? `?${query}` : ""}`, {}, onUnauthorized);
  },

  async createUser(payload, onUnauthorized) {
    return request(
      "/api/users",
      { method: "POST", body: JSON.stringify(payload) },
      onUnauthorized
    );
  },

  async toggleUserStatus(userId, onUnauthorized) {
    return request(
      `/api/users/${userId}/toggle-status`,
      { method: "PATCH" },
      onUnauthorized
    );
  },

  async getReminders(params = {}, onUnauthorized) {
    const query = new URLSearchParams(params).toString();
    return request(`/api/reminders${query ? `?${query}` : ""}`, {}, onUnauthorized);
  },

  async getMyReminders(onUnauthorized) {
    return request("/api/reminders/my", {}, onUnauthorized);
  },

  async getOverdueReminders(onUnauthorized) {
    return request("/api/reminders/overdue", {}, onUnauthorized);
  },

  async createReminder(payload, onUnauthorized) {
    return request(
      "/api/reminders",
      { method: "POST", body: JSON.stringify(payload) },
      onUnauthorized
    );
  },

  async updateReminderStatus(reminderId, status, onUnauthorized) {
    return request(
      `/api/reminders/${reminderId}/status`,
      { method: "PATCH", body: JSON.stringify({ status }) },
      onUnauthorized
    );
  },

  async getRooms(onUnauthorized) {
    return request("/api/rooms", {}, onUnauthorized);
  },
};

export default API;
