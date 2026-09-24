import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);

const STORAGE_KEY = "schoolhouse.auth";

function loadStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadStoredAuth);

  useEffect(() => {
    if (auth) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  }, [auth]);

  // `data` is whatever /auth/login returns — expected shape:
  // { access_token, token_type, role, user_id }. Adjust the mapping below
  // if your TokenResponse schema uses different field names.
  function loginWithResponse(data) {
    setAuth({
      token: data.access_token,
      role: data.role,
      userId: data.user_id,
    });
  }

  function logout() {
    setAuth(null);
  }

  const value = {
    token: auth?.token ?? null,
    role: auth?.role ?? null,
    userId: auth?.userId ?? null,
    isAuthenticated: Boolean(auth?.token),
    loginWithResponse,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside an AuthProvider");
  return ctx;
}
