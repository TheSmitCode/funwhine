// app/ClientShell.tsx
"use client";

import dynamic from "next/dynamic";
import { usePathname } from "next/navigation";
import { useAuthContext } from "@/context/AuthContext";
import { useEffect } from "react";

const Sidebar = dynamic(() => import("@/components/Sidebar"), { ssr: false });
const Navbar = dynamic(() => import("@/components/Navbar"), { ssr: false });

export default function ClientShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { loading, user, theme } = useAuthContext();

  // Apply theme class to document root
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.className = theme;
    }
  }, [theme]);

  const publicRoutes = ["/login", "/register", "/", "/public"];
  const isPublic = publicRoutes.some(route =>
    pathname === route || pathname.startsWith(route + "/")
  );

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-lg">Loading FunWine...</div>
      </div>
    );
  }

  if (isPublic || !user) return <>{children}</>;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[var(--bg)] text-[var(--fg)]">
      {user.ui_sidebar !== false && (
        <aside className="w-64 border-r border-theme h-full overflow-y-auto">
          <Sidebar />
        </aside>
      )}

      <div className="flex flex-col flex-1 h-full overflow-hidden">
        {user.ui_navbar !== false && (
          <header className="border-b border-theme">
            <Navbar />
          </header>
        )}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
