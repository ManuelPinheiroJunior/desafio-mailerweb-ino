"use client";

import React from "react";
import Link from "next/link";
import { type FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { apiRequest } from "@/lib/api-client";
import { Alert, Button, Card, Field } from "@/components/ui";

import styles from "./login-form.module.css";

type RegisterResponse = {
  message: string;
};

export function RegisterForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      await apiRequest<RegisterResponse>("/auth/register", {
        method: "POST",
        body: { email, password },
      });
      setSuccess("User created successfully. Redirecting to login...");
      setTimeout(() => {
        router.push("/login");
      }, 900);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to create user.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className={styles.card} padding="lg">
      <h1 className={styles.title}>Create account</h1>
      <p className={styles.subtitle}>Register a user to access the booking dashboard.</p>
      <form onSubmit={onSubmit} className={styles.form}>
        <Field
          id="register_email"
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <Field
          id="register_password"
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          hint="Use at least 6 characters."
          required
        />
        <Button type="submit" loading={loading}>
          Create user
        </Button>
        {error ? <Alert role="alert">{error}</Alert> : null}
        {success ? <Alert tone="success">{success}</Alert> : null}
      </form>
      <p className={styles.footerText}>
        Already have an account?{" "}
        <Link className={styles.footerLink} href="/login">
          Sign in
        </Link>
      </p>
    </Card>
  );
}
