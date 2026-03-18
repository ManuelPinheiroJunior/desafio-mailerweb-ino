import React from "react";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

import styles from "./alert.module.css";

type Props = HTMLAttributes<HTMLDivElement> & {
  tone?: "error" | "success";
};

export function Alert({ tone = "error", className, ...props }: Props) {
  return <div className={cn(styles.alert, styles[tone], className)} {...props} />;
}
