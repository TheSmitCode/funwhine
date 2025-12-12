"use client";

import Link from "next/link";
import { useAuthContext } from "@/context/AuthContext";

export default function Sidebar() {
  const { user } = useAuthContext();

  const links = [
    { href: "/dashboard", label: "Dashboard", key: "dashboard" },
    { href: "/intake", label: "Intake", key: "intake" },
    { href: "/blocks", label: "Blocks", key: "blocks" },
    { href: "/reports", label: "Reports", key: "reports" },
  ];

  return (
    <div className="p-4 h-full bg-[var(--bg)] text-[var(--fg)]">
      <nav className="flex flex-col gap-3">
        {links.map((l) =>
          user?.ui_simple_mode && !user?.ui_features?.[l.key]
            ? null
            : (
                <Link
                  key={l.href}
                  href={l.href}
                  className="px-3 py-2 rounded hover:bg-[var(--border)]"
                >
                  {l.label}
                </Link>
              )
        )}
      </nav>
    </div>
  );
}
