"use client";

import Link from "next/link";
import { type FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, apiRequest } from "@/lib/api-client";
import { getAccessToken } from "@/lib/auth";
import type { Booking } from "@/types/api";
import { Alert, Button, Card, Field } from "@/components/ui";

type Props = {
  bookingId: string;
};

export function BookingEditForm({ bookingId }: Props) {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [roomId, setRoomId] = useState("");
  const [startAt, setStartAt] = useState("");
  const [endAt, setEndAt] = useState("");
  const [participants, setParticipants] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadBooking() {
      const token = getAccessToken();
      if (!token) {
        setError("You must login first.");
        setLoading(false);
        return;
      }

      try {
        const booking = await apiRequest<Booking>(`/bookings/${bookingId}`, { token });
        setTitle(booking.title);
        setRoomId(booking.room_id);
        setStartAt(booking.start_at);
        setEndAt(booking.end_at);
        setParticipants(booking.participants.join(", "));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load booking.");
      } finally {
        setLoading(false);
      }
    }

    void loadBooking();
  }, [bookingId]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const token = getAccessToken();
    if (!token) {
      setError("You must login first.");
      return;
    }

    setSaving(true);
    const participantList = participants
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    try {
      await apiRequest<Booking>(`/bookings/${bookingId}`, {
        method: "PUT",
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
        setError(err instanceof Error ? err.message : "Unable to update booking.");
      }
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <Card>
        <p style={{ margin: 0 }}>Loading booking...</p>
      </Card>
    );
  }

  return (
    <Card padding="lg">
      <form onSubmit={onSubmit} className="stack-md">
        <div className="grid-two">
          <Field
            id="title"
            label="Meeting title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <Field
            id="room_id"
            label="Room ID"
            value={roomId}
            onChange={(e) => setRoomId(e.target.value)}
            required
          />
        </div>
        <div className="grid-two">
          <Field
            id="start_at"
            label="Start (ISO 8601)"
            value={startAt}
            onChange={(e) => setStartAt(e.target.value)}
            required
          />
          <Field
            id="end_at"
            label="End (ISO 8601)"
            value={endAt}
            onChange={(e) => setEndAt(e.target.value)}
            required
          />
        </div>
        <Field
          id="participants"
          label="Participants"
          value={participants}
          onChange={(e) => setParticipants(e.target.value)}
        />
        {error ? <Alert role="alert">{error}</Alert> : null}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
          <Link href="/bookings">
            <Button type="button" variant="ghost">
              Back
            </Button>
          </Link>
          <Button type="submit" loading={saving}>
            Save changes
          </Button>
        </div>
      </form>
    </Card>
  );
}
