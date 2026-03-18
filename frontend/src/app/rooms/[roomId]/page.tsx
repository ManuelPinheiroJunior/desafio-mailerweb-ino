import { RoomDetails } from "@/components/room-details";
import { PageHeader } from "@/components/ui";

type Props = {
  params: Promise<{ roomId: string }>;
};

export default async function RoomDetailsPage({ params }: Props) {
  const { roomId } = await params;

  return (
    <main className="page-wrap stack-lg">
      <PageHeader title="Room details" subtitle="View room metadata and capacity." />
      <RoomDetails roomId={roomId} />
    </main>
  );
}
