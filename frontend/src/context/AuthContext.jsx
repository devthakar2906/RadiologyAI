import { createContext, useContext, useEffect, useState } from "react";
import toast from "react-hot-toast";
import api, { setAuthToken } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    setAuthToken(token);
  }, [token]);

  useEffect(() => {
    const restoreSession = async () => {
      try {
        const { data } = await api.get("/auth/me");
        setUser(data);
      } catch {
        setUser(null);
        localStorage.removeItem("user");
      } finally {
        setAuthReady(true);
      }
    };
    restoreSession();
  }, []);

  const persistAuth = (payload) => {
    setToken(null);
    setUser(payload.user);
    localStorage.setItem("user", JSON.stringify(payload.user));
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
    api.post("/auth/logout").catch(() => null).finally(() => {
      setToken(null);
      setUser(null);
      localStorage.removeItem("user");
      setAuthToken(null);
    });
  };

  return <AuthContext.Provider value={{ token, user, login, signup, logout, authReady }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
