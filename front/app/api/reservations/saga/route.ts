import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_GATEWAY_URL || "http://api:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const token = request.headers.get("authorization");

    console.log("Saga API route - body:", body);

    const response = await fetch(`${API_URL}/reservations/saga`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: token } : {}),
      },
      body: JSON.stringify(body),
    });

    console.log("Saga API response status:", response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error("Saga API error:", error);
      return NextResponse.json(
        { message: error.detail || "Erreur reservation", detail: error.detail },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log("Saga API success:", data);
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Saga API exception:", error);
    return NextResponse.json(
      { message: "Erreur serveur", detail: error.message },
      { status: 500 }
    );
  }
}
