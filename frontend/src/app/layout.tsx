import type { Metadata } from "next";
import type { ReactNode } from "react";

import { AppShell } from "@/components/app-shell";

import "./globals.css";

export const metadata: Metadata = {
  title: "Meeting Room Booking",
  description: "Meeting room booking frontend",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-root">
          <AppShell>{children}</AppShell>
        </div>
      </body>
    </html>
  );
}
