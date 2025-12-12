// app/dashboard/page.tsx
"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthContext } from "../../context/AuthContext";

export default function DashboardPage() {
  const { user, loading, fetchMe } = useAuthContext();
  const router = useRouter();

  useEffect(() => {
    // If not loading and no user, redirect to login
    if (!loading && !user) {
      router.replace("/(auth)/login");
    }
  }, [user, loading, router]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Redirecting...</div>;

  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", padding: "1rem" }}>
      <h1>Dashboard</h1>
      <p>Welcome, {user.username} (id: {user.id})</p>
      <pre>{JSON.stringify(user, null, 2)}</pre>
    </main>
  );
}
