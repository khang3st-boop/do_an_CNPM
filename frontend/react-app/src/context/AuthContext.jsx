import { createContext, useContext, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { API, getToken, getUser, setSession, clearSession } from "../api/api";

/**
 * AuthContext thay cho việc gọi rải rác API.getToken()/getUser() trong
 * từng file JS gốc (login.js, users.js, guests.js, api.js#requireAuth).
 * Mọi component con dùng useAuth() để lấy user hiện tại, hàm login/logout.
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getUser());
  const navigate = useNavigate();

  // Gọi khi API trả 401 (token hết hạn) - tương đương API.request() trong api.js gốc
  const handleUnauthorized = useCallback(() => {
    clearSession();
    setUser(null);
    navigate("/ui/login");
  }, [navigate]);

  // Tương đương logic trong login.js
  const login = useCallback(async (email, password) => {
    const result = await API.login(email, password);
    setSession(result.data.token, result.data.user);
    setUser(result.data.user);
    return result.data.user;
  }, []);

  // Tương đương setupLogout() trong api.js gốc
  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    navigate("/ui/login");
  }, [navigate]);

  // Tương đương API.requireAuth() trong api.js gốc
  const isAuthenticated = !!getToken();

  const value = {
    user,
    setUser,
    login,
    logout,
    isAuthenticated,
    handleUnauthorized,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth phải được dùng trong AuthProvider");
  }
  return ctx;
}
