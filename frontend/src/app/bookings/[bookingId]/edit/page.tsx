import { BookingEditForm } from "@/components/booking-edit-form";
import { PageHeader } from "@/components/ui";

type Props = {
  params: Promise<{ bookingId: string }>;
};

export default async function EditBookingPage({ params }: Props) {
  const { bookingId } = await params;

  return (
    <main className="page-wrap stack-lg">
      <PageHeader
        title="Edit booking"
        subtitle="Update details while preserving conflict rules."
      />
      <BookingEditForm bookingId={bookingId} />
    </main>
  );
}
