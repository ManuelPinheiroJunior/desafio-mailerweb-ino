import { RoomsPanel } from "@/components/rooms-panel";
import { PageHeader } from "@/components/ui";

export default function RoomsPage() {
  return (
    <main className="page-wrap stack-lg">
      <PageHeader
        title="Rooms"
        subtitle="Manage available rooms and their capacity."
      />
      <RoomsPanel />
    </main>
  );
}
