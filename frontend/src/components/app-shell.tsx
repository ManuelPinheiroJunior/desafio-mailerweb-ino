"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import type { ReactNode } from "react";

import { getAccessToken } from "@/lib/auth";

function isActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === href;
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(Boolean(getAccessToken()));
  }, [pathname]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__inner">
          <Link href="/" className="brand">
            Meeting Room Booking System
          </Link>
          <nav className="app-nav" aria-label="Main navigation">
            <Link
              href="/login"
              className={`nav-link ${isActive(pathname, "/login") ? "nav-link--active" : ""}`}
            >
              Login
            </Link>
            {!isLoggedIn ? (
              <Link
                href="/register"
                className={`nav-link ${isActive(pathname, "/register") ? "nav-link--active" : ""}`}
              >
                Register
              </Link>
            ) : null}
            {isLoggedIn ? (
              <>
                <Link
                  href="/bookings"
                  className={`nav-link ${isActive(pathname, "/bookings") ? "nav-link--active" : ""}`}
                >
                  Bookings
                </Link>
                <Link
                  href="/rooms"
                  className={`nav-link ${isActive(pathname, "/rooms") ? "nav-link--active" : ""}`}
                >
                  Rooms
                </Link>
              </>
            ) : null}
          </nav>
        </div>
      </header>
      {children}
    </div>
  );
}
