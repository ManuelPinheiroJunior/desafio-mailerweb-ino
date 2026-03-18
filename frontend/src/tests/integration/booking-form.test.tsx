import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BookingForm } from "@/components/booking-form";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

describe("BookingForm integration", () => {
  beforeEach(() => {
    pushMock.mockReset();
    localStorage.clear();
    localStorage.setItem("meeting_room_access_token", "jwt-token");
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("creates booking and redirects", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          id: "b1",
          title: "Planning",
          room_id: "r1",
          organizer_user_id: "u1",
          start_at: "2026-03-17T09:00:00+00:00",
          end_at: "2026-03-17T10:00:00+00:00",
          status: "ACTIVE",
          participants: ["a@mail.com"],
          version: 1,
        }),
      }),
    );

    render(<BookingForm />);

    fireEvent.change(screen.getByLabelText("Meeting title"), { target: { value: "Planning" } });
    fireEvent.change(screen.getByLabelText("Room ID"), { target: { value: "room-123" } });
    fireEvent.change(screen.getByLabelText("Start (ISO 8601)"), {
      target: { value: "2026-03-17T09:00:00+00:00" },
    });
    fireEvent.change(screen.getByLabelText("End (ISO 8601)"), {
      target: { value: "2026-03-17T10:00:00+00:00" },
    });
    fireEvent.change(screen.getByLabelText(/Participants/i), {
      target: { value: "a@mail.com" },
    });

    await userEvent.click(screen.getByRole("button", { name: "Create booking" }));

    expect(pushMock).toHaveBeenCalledWith("/bookings");
  });

  it("shows conflict error when backend returns 409", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({ detail: "There is an active booking conflict in this room." }),
      }),
    );

    render(<BookingForm />);

    fireEvent.change(screen.getByLabelText("Meeting title"), { target: { value: "Conflict" } });
    fireEvent.change(screen.getByLabelText("Room ID"), { target: { value: "room-123" } });
    fireEvent.change(screen.getByLabelText("Start (ISO 8601)"), {
      target: { value: "2026-03-17T09:00:00+00:00" },
    });
    fireEvent.change(screen.getByLabelText("End (ISO 8601)"), {
      target: { value: "2026-03-17T10:00:00+00:00" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Create booking" }));

    expect(await screen.findByText(/Conflito de horário/i)).toBeInTheDocument();
  });
});
