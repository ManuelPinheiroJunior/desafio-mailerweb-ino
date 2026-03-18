import React from "react";
import type { ReactNode } from "react";

import styles from "./empty-state.module.css";

type Props = {
  title: string;
  text: string;
  action?: ReactNode;
};

export function EmptyState({ title, text, action }: Props) {
  return (
    <div className={styles.root}>
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.text}>{text}</p>
      {action ? <div style={{ marginTop: 14 }}>{action}</div> : null}
    </div>
  );
}
