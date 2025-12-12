// app/(auth)/login/page.tsx
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login, loading, error } = useAuthContext();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await login(username, password);
      // Navigate to protected route after login
      router.push("/dashboard");
    } catch (err) {
      // error state is exposed via context
    }
  }

  return (
    <main style={{ maxWidth: 480, margin: "2rem auto", padding: "1rem" }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <br />
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <br />
        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
        {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      </form>
    </main>
  );
}
