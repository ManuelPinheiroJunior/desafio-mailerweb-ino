import React from "react";
import type { InputHTMLAttributes, TextareaHTMLAttributes } from "react";

import styles from "./field.module.css";

type BaseProps = {
  id: string;
  label: string;
  error?: string | null;
  hint?: string;
};

type InputProps = BaseProps &
  InputHTMLAttributes<HTMLInputElement> & {
    multiline?: false;
  };

type TextareaProps = BaseProps &
  TextareaHTMLAttributes<HTMLTextAreaElement> & {
    multiline: true;
  };

export function Field(props: InputProps | TextareaProps) {
  const { id, label, error, hint, multiline = false, ...rest } = props;

  return (
    <label className={styles.root} htmlFor={id}>
      <span className={styles.label}>{label}</span>
      {multiline ? (
        <textarea id={id} className={styles.textarea} {...(rest as TextareaProps)} />
      ) : (
        <input id={id} className={styles.input} {...(rest as InputProps)} />
      )}
      {error ? <span className={styles.error}>{error}</span> : hint ? <span className={styles.hint}>{hint}</span> : null}
    </label>
  );
}
