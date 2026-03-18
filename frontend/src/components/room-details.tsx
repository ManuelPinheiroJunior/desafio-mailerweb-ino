"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiRequest } from "@/lib/api-client";
import { getAccessToken } from "@/lib/auth";
import type { Room } from "@/types/api";
import { Alert, Button, Card } from "@/components/ui";

type Props = {
  roomId: string;
};

export function RoomDetails({ roomId }: Props) {
  const [room, setRoom] = useState<Room | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRoom() {
      const token = getAccessToken();
      if (!token) {
        setError("You must login first.");
        setLoading(false);
        return;
      }

      try {
        const response = await apiRequest<Room>(`/rooms/${roomId}`, { token });
        setRoom(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load room.");
      } finally {
        setLoading(false);
      }
    }

    void loadRoom();
  }, [roomId]);

  if (loading) {
    return (
      <Card>
        <p style={{ margin: 0 }}>Loading room details...</p>
      </Card>
    );
  }

  if (error || !room) {
    return (
      <Card className="stack-md">
        <Alert role="alert">{error ?? "Room not found."}</Alert>
        <Link href="/rooms">
          <Button variant="ghost" type="button">
            Back to rooms
          </Button>
        </Link>
      </Card>
    );
  }

  return (
    <Card className="stack-md" padding="lg">
      <h2 style={{ margin: 0 }}>{room.name}</h2>
      <p style={{ margin: 0, color: "var(--text-muted)" }}>Room ID: {room.id}</p>
      <p style={{ margin: 0 }}>Capacity: {room.capacity}</p>
      <div>
        <Link href="/rooms">
          <Button variant="secondary" type="button">
            Back to rooms
          </Button>
        </Link>
      </div>
    </Card>
  );
}
