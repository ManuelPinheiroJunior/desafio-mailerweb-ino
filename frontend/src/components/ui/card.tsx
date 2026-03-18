import React from "react";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/cn";

import styles from "./card.module.css";

type Props = HTMLAttributes<HTMLDivElement> & {
  padding?: "md" | "lg";
};

export function Card({ className, padding = "md", ...props }: Props) {
  return (
    <div
      className={cn(className, styles.card, padding === "md" ? styles.paddingMd : styles.paddingLg)}
      {...props}
    />
  );
}
