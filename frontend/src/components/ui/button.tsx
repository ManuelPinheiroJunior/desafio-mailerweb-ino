import React from "react";
import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

import styles from "./button.module.css";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  loading?: boolean;
};

export function Button({
  variant = "primary",
  loading = false,
  className,
  children,
  disabled,
  ...props
}: Props) {
  return (
    <button
      className={cn(styles.button, styles[variant], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? "Loading..." : children}
    </button>
  );
}
