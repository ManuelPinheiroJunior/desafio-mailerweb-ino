import React from "react";
import { cn } from "@/lib/cn";

import styles from "./badge.module.css";

type Props = {
  children: string;
  tone: "active" | "canceled";
};

export function Badge({ children, tone }: Props) {
  return <span className={cn(styles.badge, styles[tone])}>{children}</span>;
}
