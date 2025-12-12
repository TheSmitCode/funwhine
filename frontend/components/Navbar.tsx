"use client";

import { useRouter } from "next/navigation";
import { useAuthContext } from "@/context/AuthContext";

export default function Navbar() {
  const router = useRouter();
  const { user, logout } = useAuthContext();

  async function handleLogout() {
    try {
      await logout();
      router.push("/login");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  }

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-[var(--bg)] text-[var(--fg)]">
      <h1 className="text-lg font-semibold">FunWine</h1>

      <div className="flex items-center gap-4">
        {!user?.ui_simple_mode && (
          <button
            className="px-3 py-1 rounded bg-accent text-white"
            onClick={() => router.push("/settings/view")}
          >
            Settings
          </button>
        )}

        <button
          className="px-3 py-1 rounded border border-theme"
          onClick={handleLogout}
        >
          Logout
        </button>
      </div>
    </div>
  );
}
