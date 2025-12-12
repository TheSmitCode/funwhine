// app/layout.tsx
import "./globals.css";
import type { ReactNode } from "react";
import { AuthProvider } from "@/context/AuthContext";
import ClientShell from "./ClientShell";

export const metadata = {
  title: "FunWine",
  description: "FunWine React + FastAPI App",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      {/*
        Apply theme classes here.
        Default is theme-light but changes once UIContext loads.
      */}
      <body className="theme-light">
        <AuthProvider>
          <ClientShell>
            {children}
          </ClientShell>
        </AuthProvider>
      </body>
    </html>
  );
}
