import { BookingForm } from "@/components/booking-form";
import { PageHeader } from "@/components/ui";

export default function NewBookingPage() {
  return (
    <main className="page-wrap stack-lg">
      <PageHeader
        title="Create booking"
        subtitle="Schedule a meeting and notify participants asynchronously."
      />
      <BookingForm />
    </main>
  );
}
