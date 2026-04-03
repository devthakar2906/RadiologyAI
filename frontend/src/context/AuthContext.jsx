import { createContext, useContext, useEffect, useState } from "react";
import toast from "react-hot-toast";
import api, { setAuthToken } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  const persistAuth = (payload) => {
    setToken(payload.access_token);
    setUser(payload.user);
    localStorage.setItem("token", payload.access_token);
    localStorage.setItem("user", JSON.stringify(payload.user));
    setAuthToken(payload.access_token);
  };

  const login = async (values) => {
    const { data } = await api.post("/auth/login", values);
    persistAuth(data);
    toast.success("Logged in");
  };

  const signup = async (values) => {
    const { data } = await api.post("/auth/signup", values);
    persistAuth(data);
    toast.success("Account created");
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setAuthToken(null);
  };

  return <AuthContext.Provider value={{ token, user, login, signup, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
