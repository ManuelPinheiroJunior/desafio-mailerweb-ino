import Link from "next/link";

import { Button, Card, PageHeader } from "@/components/ui";

export default function HomePage() {
  return (
    <main className="page-wrap stack-lg">
      <PageHeader
        title="Meeting Room Booking"
        subtitle="A clean SaaS interface for room reservations and async notifications."
      />
      <Card className="stack-md" padding="lg">
        <p style={{ margin: 0, color: "var(--text-muted)" }}>
          Start by signing in, then manage bookings and rooms from the dashboard.
        </p>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Link href="/login">
            <Button>Go to login</Button>
          </Link>
          <Link href="/register">
            <Button variant="secondary">Create user</Button>
          </Link>
          <Link href="/bookings">
            <Button variant="ghost">View bookings</Button>
          </Link>
          <Link href="/rooms">
            <Button variant="ghost">View rooms</Button>
          </Link>
        </div>
      </Card>
    </main>
  );
}
