import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { LoginForm } from "@/components/login-form";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}));

describe("LoginForm", () => {
  beforeEach(() => {
    pushMock.mockReset();
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    cleanup();
  });

  it("logs in and redirects to bookings", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          access_token: "jwt-token",
          token_type: "bearer",
        }),
      }),
    );

    render(<LoginForm />);

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "user@mail.com" } });
    fireEvent.change(screen.getByLabelText("Password"), {
      target: { value: "password123" },
    });
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(localStorage.getItem("meeting_room_access_token")).toBe("jwt-token");
    expect(pushMock).toHaveBeenCalledWith("/bookings");
  });
});
