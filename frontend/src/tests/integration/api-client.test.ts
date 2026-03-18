import { describe, expect, it, vi } from "vitest";

import { apiRequest } from "@/lib/api-client";

describe("apiRequest backend integration contract", () => {
  it("sends bearer token and request body correctly", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await apiRequest("/bookings", {
      method: "POST",
      token: "jwt-token",
      body: { title: "Planning" },
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.headers).toMatchObject({
      "Content-Type": "application/json",
      Authorization: "Bearer jwt-token",
    });
    expect(init.body).toBe(JSON.stringify({ title: "Planning" }));
  });
});
