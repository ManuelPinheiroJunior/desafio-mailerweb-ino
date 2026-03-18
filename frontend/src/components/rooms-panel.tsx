"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { ApiError, apiRequest } from "@/lib/api-client";
import { getAccessToken } from "@/lib/auth";
import type { Room } from "@/types/api";
import { Alert, Button, Card, EmptyState, Field } from "@/components/ui";

import styles from "./rooms-panel.module.css";

export function RoomsPanel() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState("8");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function loadRooms() {
    const token = getAccessToken();
    if (!token) {
      setError("You must login first.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<Room[]>("/rooms", { token });
      setRooms(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load rooms.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadRooms();
  }, []);

  async function onCreateRoom(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    const token = getAccessToken();
    if (!token) {
      setError("You must login first.");
      return;
    }

    setSubmitting(true);
    try {
      await apiRequest<Room>("/rooms", {
        method: "POST",
        token,
        body: {
          name: name.trim(),
          capacity: Number(capacity),
        },
      });
      setSuccess("Room created successfully.");
      setName("");
      setCapacity("8");
      await loadRooms();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Unable to create room.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className={styles.layout}>
      <Card className="stack-md">
        <h2 style={{ margin: 0 }}>Room list</h2>
        {loading ? (
          <p style={{ margin: 0 }}>Loading rooms...</p>
        ) : rooms.length === 0 ? (
          <EmptyState
            title="No rooms available"
            text="Create your first room on the right panel."
          />
        ) : (
          <ul className={styles.list}>
            {rooms.map((room) => (
              <li key={room.id} className={styles.room}>
                <div>
                  <p className={styles.name}>{room.name}</p>
                  <p className={styles.capacity}>Capacity: {room.capacity}</p>
                </div>
                <div style={{ display: "grid", justifyItems: "end", gap: 6 }}>
                  <small style={{ color: "var(--text-muted)" }}>{room.id}</small>
                  <Link href={`/rooms/${room.id}`}>
                    <Button variant="secondary" type="button">
                      Details
                    </Button>
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="stack-md">
        <h2 style={{ margin: 0 }}>Create room</h2>
        <form className={styles.form} onSubmit={onCreateRoom}>
          <Field
            id="room_name"
            label="Room name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ocean Room"
            required
          />
          <Field
            id="room_capacity"
            label="Capacity"
            type="number"
            min={1}
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
            required
          />
          {error ? <Alert role="alert">{error}</Alert> : null}
          {success ? <Alert tone="success">{success}</Alert> : null}
          <Button type="submit" loading={submitting}>
            Create room
          </Button>
        </form>
      </Card>
    </div>
  );
}
