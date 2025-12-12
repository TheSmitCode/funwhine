// frontend/lib/api.ts
import axios from "axios";

// Axios instance for your backend
export const api = axios.create({
  baseURL: "http://192.168.0.110:8000/api/v1", // backend URL
  withCredentials: true, // critical for cookie auth
});

// Auth helpers

export async function login(username: string, password: string) {
  const res = await api.post("/auth/login", { username, password });
  return res.data; // cookie is set automatically
}

export async function getMe() {
  const res = await api.get("/auth/me");
  return res.data;
}

export async function logout() {
  await api.post("/auth/logout");
}

// ✅ Default export added for compatibility with current UIContext.tsx
export default api;
