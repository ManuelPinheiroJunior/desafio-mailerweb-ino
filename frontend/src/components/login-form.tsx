"use client";

import React from "react";
import Link from "next/link";
import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api-client";
import { saveAccessToken } from "@/lib/auth";
import type { LoginResponse } from "@/types/api";
import { Alert, Button, Card, Field } from "@/components/ui";

import styles from "./login-form.module.css";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const payload = await apiRequest<LoginResponse>("/auth/login", {
        method: "POST",
        body: { email, password },
      });
      saveAccessToken(payload.access_token);
      router.push("/bookings");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to login.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className={styles.card} padding="lg">
      <h1 className={styles.title}>Sign in</h1>
      <p className={styles.subtitle}>Access your meeting room dashboard.</p>
      <form onSubmit={onSubmit} className={styles.form}>
        <Field
          id="email"
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Field
          id="password"
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button type="submit" loading={loading}>
          Sign in
        </Button>
        {error ? <Alert role="alert">{error}</Alert> : null}
      </form>
      <p className={styles.footerText}>
        New here?{" "}
        <Link className={styles.footerLink} href="/register">
          Create account
        </Link>
      </p>
    </Card>
  );
}
