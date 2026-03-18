"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { ApiError, apiRequest } from "@/lib/api-client";
import { clearAccessToken, getAccessToken } from "@/lib/auth";
import type { Booking } from "@/types/api";
import { Alert, Badge, Button, Card, EmptyState, PageHeader } from "@/components/ui";

import styles from "./booking-list.module.css";

export function BookingList() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelingBookingId, setCancelingBookingId] = useState<string | null>(null);

  async function loadBookings() {
    const token = getAccessToken();
    if (!token) {
      setError("You must login first.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<Booking[]>("/bookings", { token });
      setBookings(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load bookings.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadBookings();
  }, []);

  function onLogout() {
    clearAccessToken();
    window.location.href = "/login";
  }

  async function onCancelBooking(bookingId: string) {
    const token = getAccessToken();
    if (!token) {
      setError("You must login first.");
      return;
    }

    setCancelingBookingId(bookingId);
    try {
      await apiRequest<Booking>(`/bookings/${bookingId}/cancel`, {
        method: "POST",
        token,
      });
      await loadBookings();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to cancel booking.");
      }
    } finally {
      setCancelingBookingId(null);
    }
  }

  if (loading) {
    return (
      <div className="page-wrap">
        <PageHeader title="Bookings" subtitle="Manage meetings, conflicts and status." />
        <Card style={{ marginTop: 14 }}>
          <p style={{ margin: 0 }}>Loading bookings...</p>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-wrap">
        <PageHeader title="Bookings" subtitle="Manage meetings, conflicts and status." />
        <Card style={{ marginTop: 14 }}>
          <div className="stack-md">
            <Alert role="alert">{error}</Alert>
            <div style={{ display: "flex", gap: 8 }}>
              <Button variant="secondary" onClick={() => void loadBookings()}>
                Retry
              </Button>
              <Button variant="ghost" onClick={onLogout}>
                Go to login
              </Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="page-wrap stack-lg">
      <PageHeader
        title="Bookings"
        subtitle="Create, edit and cancel room reservations."
        actions={
          <div style={{ display: "flex", gap: 8 }}>
            <Link href="/bookings/new">
              <Button>Create booking</Button>
            </Link>
            <Button variant="ghost" onClick={onLogout}>
              Logout
            </Button>
          </div>
        }
      />

      {bookings.length === 0 ? (
        <EmptyState
          title="No bookings yet"
          text="Create your first reservation to start using the system."
          action={
            <Link href="/bookings/new">
              <Button>Create booking</Button>
            </Link>
          }
        />
      ) : (
        <ul className={styles.list}>
          {bookings.map((booking) => (
            <li className={styles.item} key={booking.id}>
              <div className={styles.row}>
                <h3 className={styles.title}>{booking.title}</h3>
                <Badge tone={booking.status === "ACTIVE" ? "active" : "canceled"}>
                  {booking.status === "ACTIVE" ? "Active" : "Canceled"}
                </Badge>
              </div>
              <p className={styles.meta}>
                Room ID: {booking.room_id} | {booking.start_at} - {booking.end_at}
              </p>
              <div className={styles.actions}>
                <Link href={`/bookings/${booking.id}/edit`}>
                  <Button variant="secondary">Edit</Button>
                </Link>
                <Button
                  variant="danger"
                  onClick={() => void onCancelBooking(booking.id)}
                  loading={cancelingBookingId === booking.id}
                  disabled={booking.status === "CANCELED"}
                >
                  Cancel
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
