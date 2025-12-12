// context/AuthContext.tsx
"use client";

/**
 * AuthContext: provides user state and auth actions to the app.
 *
 * Design decisions:
 * - Uses cookie-based auth (HttpOnly cookie). The client cannot read cookie,
 *   so we call GET /auth/me to learn the current user.
 * - Login sends credentials to POST /auth/login and backend sets HttpOnly cookie.
 * - Logout calls POST /auth/logout which clears cookie.
 * - We expose `user`, `loading`, `error`, and `actions: login, logout, refreshMe`.
 *
 * Impact on backend:
 * - Backend must accept credentials via JSON and set cookie with same path/domain.
 * - If you use CSRF protection on backend, you must implement CSRF token fetch/submit here.
 */

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import axiosClient from "../lib/axiosClient";
import type { User, TokenResponse } from "../types/auth";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  error: string | null;
  theme: string;
  login: (username: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<User | null>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<string>("theme-light");

  const fetchMe = useCallback(async (): Promise<User | null> => {
    setLoading(true);
    setError(null);
    try {
      const resp = await axiosClient.get<User>("/auth/me");
      setUser(resp.data);
      // Apply user's theme preference
      if (resp.data.ui_theme) {
        setTheme(resp.data.ui_theme);
      }
      return resp.data;
    } catch (err: any) {
      setUser(null);
      // swallow 401 as unauthenticated state
      if (err?.response?.status && err.response.status !== 401) {
        setError(err?.response?.data?.detail || err.message || "Failed to fetch user");
      }
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // On mount attempt to load current user
    void fetchMe();
  }, [fetchMe]);

  const login = useCallback(async (username: string, password: string): Promise<User> => {
    setLoading(true);
    setError(null);
    try {
      // backend should set HttpOnly cookie; token may be returned in JSON for testing
      await axiosClient.post<TokenResponse>("/auth/login", { username, password });
      // After login, fetch user via cookie-based /auth/me
      const me = await fetchMe();
      if (!me) throw new Error("Login succeeded but failed to load user");
      return me;
    } catch (err: any) {
      setUser(null);
      setError(err?.response?.data?.detail || err.message || "Login failed");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchMe]);

  const logout = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      await axiosClient.post("/auth/logout");
      setUser(null);
      setTheme("theme-light");
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Logout failed");
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const value: AuthContextValue = {
    user,
    loading,
    error,
    theme,
    login,
    logout,
    fetchMe,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used inside AuthProvider");
  return ctx;
}
