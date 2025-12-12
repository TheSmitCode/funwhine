// app/page.tsx
"use client";

import Link from "next/link";

export default function Home() {
  return (
    <main style={{ maxWidth: 760, margin: "2rem auto", padding: "1rem" }}>
      <h1>Home</h1>
      <p>
        <Link href="/(auth)/login">Login</Link> | <Link href="/dashboard">Dashboard</Link>
      </p>
    </main>
  );
}
