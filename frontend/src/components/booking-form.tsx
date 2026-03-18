"use client";

import React from "react";
import { type FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ApiError, apiRequest } from "@/lib/api-client";
import { getAccessToken } from "@/lib/auth";
import type { Booking } from "@/types/api";
import { Alert, Button, Card, Field } from "@/components/ui";

import styles from "./booking-form.module.css";

export function BookingForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [roomId, setRoomId] = useState("");
  const [startAt, setStartAt] = useState("");
  const [endAt, setEndAt] = useState("");
  const [participants, setParticipants] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const token = getAccessToken();
    if (!token) {
      setError("You must login first.");
      setLoading(false);
      return;
    }

    const participantList = participants
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    try {
      await apiRequest<Booking>("/bookings", {
        method: "POST",
        token,
        body: {
          title,
          room_id: roomId,
          start_at: startAt,
          end_at: endAt,
          participants: participantList,
        },
      });
      router.push("/bookings");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("Conflito de horário: já existe uma reserva ativa nesta sala.");
      } else {
        setError(err instanceof Error ? err.message : "Unable to create booking.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card padding="lg">
      <form onSubmit={onSubmit} className={styles.form}>
        <div className="grid-two">
          <Field
            id="title"
            label="Meeting title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Weekly Planning"
            required
          />
          <Field
            id="room_id"
            label="Room ID"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            placeholder="room-uuid"
            required
          />
        </div>
        <div className="grid-two">
          <Field
            id="start_at"
            label="Start (ISO 8601)"
            value={startAt}
            onChange={(e) => setStartAt(e.target.value)}
            placeholder="2026-03-17T14:00:00+00:00"
            required
          />
          <Field
            id="end_at"
            label="End (ISO 8601)"
            value={endAt}
            onChange={(e) => setEndAt(e.target.value)}
            placeholder="2026-03-17T15:00:00+00:00"
            required
          />
        </div>
        <Field
          id="participants"
          label="Participants"
          value={participants}
          onChange={(e) => setParticipants(e.target.value)}
          hint="Use comma separated emails. Example: a@mail.com, b@mail.com"
        />
        {error ? <Alert role="alert">{error}</Alert> : null}
        <div className={styles.footer}>
          <Link href="/bookings">
            <Button type="button" variant="ghost">
              Back
            </Button>
          </Link>
          <Button type="submit" loading={loading}>
            Create booking
          </Button>
        </div>
      </form>
    </Card>
  );
}
