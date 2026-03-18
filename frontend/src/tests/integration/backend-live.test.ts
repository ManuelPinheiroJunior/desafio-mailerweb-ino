import { describe, expect, it } from "vitest";

const API_BASE_URL = process.env.FRONTEND_E2E_API_BASE_URL;

describe("frontend live integration with backend", () => {
  it.runIf(Boolean(API_BASE_URL))("registers and logs in against a real backend", async () => {
    const uniqueEmail = `live_${Date.now()}@mail.com`;
    const password = "123456";

    const registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: uniqueEmail, password }),
    });
    expect(registerResponse.ok).toBe(true);

    const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: uniqueEmail, password }),
    });
    expect(loginResponse.ok).toBe(true);

    const payload = (await loginResponse.json()) as { access_token?: string };
    expect(typeof payload.access_token).toBe("string");
    expect(payload.access_token?.length).toBeGreaterThan(20);
  });
});
