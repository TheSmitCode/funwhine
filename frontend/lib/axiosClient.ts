// lib/axiosClient.ts
/**
 * Axios client used by the app.
 *
 * Important:
 * - withCredentials=true ensures browser includes cookies (HttpOnly) on requests.
 * - baseURL is '/api' to work with the rewrites in next.config.js during dev.
 *   If you prefer to call the production backend directly (separate origin),
 *   set baseURL to process.env.NEXT_PUBLIC_API_BASE and ensure server CORS is set up
 *   with allow_credentials=True and explicit origins.
 */

import axios, { AxiosInstance } from "axios";

const axiosClient: AxiosInstance = axios.create({
  baseURL: "/api", // uses next.config.js rewrites in dev. Change for prod if needed.
  withCredentials: true, // MUST be true for cookie-based auth
  headers: {
    "Content-Type": "application/json",
  },
});

// Optional: response interceptor to handle 401 globally
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // If you want, you can handle global logout on 401 here:
    // if (error.response?.status === 401) { /* do something */ }
    return Promise.reject(error);
  }
);

export default axiosClient;
