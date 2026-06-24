import { createContext, useContext, useState, useCallback } from "react";
import { API, getToken, getUser, setSession, clearSession } from "../api/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getUser());

  const login = useCallback(async (email, password) => {
    try {
      const result = await API.login(email, password);
      // Giả định API trả về cấu trúc { data: { token, user } }
      setSession(result.data.token, result.data.user);
      setUser(result.data.user);
      return result.data.user;
    } catch (error) {
      console.error("Login failed:", error);
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user, // Kiểm tra nhanh thông qua state user
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